#!/usr/bin/env python3
#!/usr/bin/with-contenv bashio
"""
Loophole Tunnel Add-on for Home Assistant
Manages a persistent loophole tunnel to expose Home Assistant over HTTPS
"""

import re
import json
import os
import subprocess
import sys
import selectors
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
OPTIONS_PATH = DATA_DIR / "options.json"
LOG_PATH = DATA_DIR / "loophole.log"
ANSI_ESCAPE_RE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

lock = threading.Lock()
tunnel_process = None


def get_loophole_env():
    """Return an environment that keeps Loophole state in the persistent add-on data volume."""
    loophole_home = DATA_DIR / "loophole-home"
    loophole_home.mkdir(parents=True, exist_ok=True)

    xdg_config = loophole_home / ".config"
    xdg_cache = loophole_home / ".cache"
    xdg_config.mkdir(parents=True, exist_ok=True)
    xdg_cache.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["HOME"] = str(loophole_home)
    env["XDG_CONFIG_HOME"] = str(xdg_config)
    env["XDG_CACHE_HOME"] = str(xdg_cache)
    return env


def log(message: str):
    """Log to stdout and logfile"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{timestamp} {message}"
    print(log_line, flush=True)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8", errors="replace") as fh:
            fh.write(log_line + "\n")
    except Exception as e:
        print(f"Failed to write to log file: {e}", flush=True)


def load_options():
    """Load options from Home Assistant"""
    if not OPTIONS_PATH.exists():
        return {"port": 80, "hostname": "", "verbose": False}
    try:
        return json.loads(OPTIONS_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        log(f"Error loading options: {e}")
        return {"port": 80, "hostname": "", "verbose": False}


def is_valid(options):
    """Check if configuration is valid"""
    try:
        port = int(options.get("port", 0))
        hostname = str(options.get("hostname", "")).strip()
        return hostname and 1 <= port <= 65535
    except (TypeError, ValueError):
        return False
    

def send_notification(title: str, message: str):
    """Send notification to Home Assistant UI"""
    try:
        token = os.environ.get("SUPERVISOR_TOKEN", "")

        log(f"SUPERVISOR_TOKEN present: {bool(token)}")
        log(f"SUPERVISOR_TOKEN length: {len(token) if token else 0}")

        if not token:
            log("Warning: SUPERVISOR_TOKEN not set, cannot send notification")
            return
        
        headers = {
            "Authorization": f"Bearer {token}",
            "content-type": "application/json",
        }
        data = {
            "title": title,
            "message": message,
            "notification_id": "loophole-addon-notification"
        }
        
        # Use urllib instead of requests (no external dependencies)
        url = "http://supervisor/core/api/services/persistent_notification/create"
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        response = urllib.request.urlopen(req, timeout=5)
        status = response.status
        
        if status != 200:
            log(f"Notification API returned status {status}")
        else:
            log(f"✓ Notification sent: {title}")
            
    except urllib.error.HTTPError as e:
        log(f"Notification API error {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        log(f"Failed to connect to supervisor API: {e.reason}")
    except Exception as e:
        log(f"Failed to send notification: {e}")

def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_RE.sub("", text)

def run_login_check():
    """Check login status - keeps command running and captures output"""
    try:
        log("Checking Loophole authentication status...")
        
        # First verify loophole command exists
        try:
            result = subprocess.run(
                ["loophole", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                env=get_loophole_env(),
            )
            log(f"✓ Loophole CLI available: {result.stdout.strip()}")
        except FileNotFoundError:
            log("❌ Loophole CLI not found in PATH")
            return False
        except Exception as e:
            log(f"⚠ Could not verify loophole: {e}")
            return False
        
        # Start login process - capture output from both stdout and stderr
        log("Starting: loophole account login")

        proc = subprocess.Popen(
            ["loophole", "account", "login"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
            env=get_loophole_env(),
        )

        log(f"Login process started (PID {proc.pid})")

        sel = selectors.DefaultSelector()
        sel.register(proc.stdout, selectors.EVENT_READ, data="stdout")
        sel.register(proc.stderr, selectors.EVENT_READ, data="stderr")

        output = bytearray()

        start_time = time.time()
        timeout = 600

        while True:

            # Process exited?
            rc = proc.poll()
            if rc is not None:
                break

            # Timeout?
            if time.time() - start_time > timeout:
                log(f"⚠ Authentication timeout ({timeout}s)")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                return False

            # Wait up to 0.5s for new output
            events = sel.select(timeout=0.5)

            for key, _ in events:

                try:
                    data = os.read(key.fileobj.fileno(), 4096)
                except OSError:
                    continue

                if not data:
                    continue

                output.extend(data)

                text = data.decode(errors="replace")

                # Print immediately exactly as loophole produced it
                log(f"[{key.data}] {text}")

                if ("https://" in text or "http://" in text):
                    clean = strip_ansi(text)
                    send_notification(
                        "Loophole Tunnel - Authentication Required", 
                        f"{clean}\n\n" 
                        "The tunnel will start automatically once authentication is complete." 
                    )

        # Drain any remaining output after exit
        for key in list(sel.get_map().values()):
            try:
                while True:
                    data = os.read(key.fileobj.fileno(), 4096)
                    if not data:
                        break
                    output.extend(data)
                    log(f"[{key.data}] {data.decode(errors='replace')}")
            except OSError:
                pass

        sel.close()

        full_output = output.decode(errors="replace")

        log(f"Process exited with code {rc}")

        if rc in (0, 1):
            log("✓ Successfully authenticated!")
            return True

        log("❌ Authentication failed")
        log(full_output)
        send_notification(
            "Loophole Tunnel - Authentication Failed", 
            f"{full_output}\n\n"
            "Please check the logs for details."
        )
        return False
            
    except Exception as e:
        log(f"❌ Login check error: {e}")
        import traceback
        traceback.print_exc()
        return False


def start_tunnel(options):
    """Start the loophole tunnel"""
    global tunnel_process
    
    if not is_valid(options):
        log("ERROR: Configuration invalid - hostname and port must be set")
        return False
    
    with lock:
        if tunnel_process is not None and tunnel_process.poll() is None:
            log("Tunnel already running")
            return True
        
        try:
            port = int(options["port"])
            hostname = str(options["hostname"]).strip()
            
            command = [
                "loophole",
                "http",
                str(port),
                "homeassistant",
                "--hostname",
                hostname,
            ]
            
            if options.get("verbose", False):
                command.append("--verbose")
            
            log(f"Starting tunnel: {' '.join(command)}")
            
            logfile = open(LOG_PATH, "a", encoding="utf-8", errors="replace")
            tunnel_process = subprocess.Popen(
                command,
                stdout=logfile,
                stderr=subprocess.STDOUT,
                text=True,
                env=get_loophole_env(),
            )
            log(f"Tunnel started with PID {tunnel_process.pid}")
            return True
            
        except Exception as e:
            log(f"ERROR: Failed to start tunnel: {e}")
            tunnel_process = None
            return False


def stop_tunnel():
    """Stop the loophole tunnel"""
    global tunnel_process
    
    with lock:
        if tunnel_process is None or tunnel_process.poll() is not None:
            log("Tunnel is not running")
            return True
        
        try:
            log(f"Stopping tunnel (PID {tunnel_process.pid})...")
            tunnel_process.terminate()
            tunnel_process.wait(timeout=10)
            log("Tunnel stopped")
        except subprocess.TimeoutExpired:
            log("Tunnel did not stop cleanly, killing...")
            tunnel_process.kill()
        finally:
            tunnel_process = None
        
        return True


def tunnel_watchdog():
    """Monitor tunnel and restart if it crashes"""
    global tunnel_process

    while True:
        time.sleep(5)

        with lock:
            if tunnel_process is not None:
                if tunnel_process.poll() is not None:
                    log(f"WARNING: Tunnel process exited with code {tunnel_process.returncode}")
                    tunnel_process = None

                    # Try to restart
                    options = load_options()
                    if is_valid(options):
                        log("Attempting to restart tunnel...")
                        start_tunnel(options)


def main():
    """Main entry point"""
    try:
        log("========================================")
        log("Loophole Tunnel Add-on starting")
        log("========================================")
        
        # Create data directory
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load options
        options = load_options()
        log(f"Configuration: port={options.get('port')}, hostname={options.get('hostname')}, verbose={options.get('verbose', False)}")
        
        # Check authentication status on every startup
        log("Checking Loophole authentication...")
        authenticated = run_login_check()
        
        if not authenticated:
            log("Not authenticated with Loophole - tunnel will not start until authenticated")
            return
        
        # Start watchdog thread
        watchdog = threading.Thread(target=tunnel_watchdog, daemon=True)
        watchdog.start()
        log("Watchdog thread started")
        
        # Start tunnel only if configuration is valid AND authenticated
        if is_valid(options):
            if authenticated:
                log("Configuration valid and authenticated, starting tunnel...")
                start_tunnel(options)
            else:
                log("Configuration valid but not authenticated - tunnel not started")
                return
        else:
            log("Configuration is not valid yet. Please configure port and hostname.")
            return
        
        log("Add-on ready")
        
        # Keep running
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        log("Received interrupt signal")
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        log("Shutting down...")
        stop_tunnel()
        log("Loophole Tunnel Add-on stopped")


if __name__ == "__main__":
    main()
