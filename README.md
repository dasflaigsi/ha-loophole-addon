<p align="center">
  <img src="https://loophole.cloud/img/logo.png" alt="Loophole Logo" width="250"/>
</p>

# HA Loophole Add-on

[![Open your Home Assistant instance and add this repository.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/dasflaigsi/ha-loophole-addon)

This Home Assistant add-on exposes your Home Assistant instance through a Loophole tunnel [(https://loophole.cloud/)](https://loophole.cloud/) over HTTPS. The add-on verifies Loophole authentication at startup, prompts for login when needed, and then starts a persistent tunnel to the local Home Assistant HTTP port.

### What is Loophole
Loophole is a totally free to use HTTPS tunnel, which is hosted in Europe. You can run the service on your local machine which allows you to securely expose services running on that machine to the web, even if they're behind a firewall or NAT. Currently, Loophole serves HTTP/HTTPs requests and plan to introduce TCP connections in future. As a bonus, all traffic from the internet to your local machine will be encrypted with SSL certificates using lets-encrypt. Authentication using Auth0 provides the security to your Loophole tunnels. Loophole lets you have multiple parallel tunnels running with custom host names at any given point along with end-to-end encryption.

## What this add-on does

At startup, the add-on:

1. Loads the configured local port and hostname from Home Assistant options.
2. Checks whether the Loophole CLI is authenticated.
3. If not authenticated, starts `loophole account login` and watches the output.
4. Sends a Home Assistant persistent notification with the login URL when authentication is required.
5. Once authentication succeeds, starts the tunnel with `loophole http <port> homeassistant --hostname <hostname>`.
6. Keeps a watchdog thread running to restart the tunnel if it exits unexpectedly.

## Supported architecture

- `amd64`
- `aarch64`

## Important warning

This add-on expects an authenticated Loophole account and a valid `hostname` before exposing a public tunnel. If either is missing, the tunnel will not start. Therefore sign up on [https://loophole.cloud/](https://loophole.cloud/)

## Installation

Use above link to direcly open the repository in your Home Assistant 

or

1. Add this repository as a local Home Assistant add-on repository. Copy the `ha-loophole-addon` folder into your Home Assistant's `addons` folder.
2. Open the Home Assistant Add-on Store.
3. Find the add-on called `Loophole Tunnel`.
4. Install it.
5. Start the add-on after configuring the required options.

## Configuration

The add-on expects these options:

- `port`: The local Home Assistant port, usually `8123`.
- `hostname`: The tunnel hostname, for example `myhome`. The resulting tunnel URL will be `https://myhome.loophole.site`.
- `verbose`: Enables verbose Loophole CLI output in the logs.

Example configuration:

```yaml
port: 8123
hostname: myhome
verbose: false
```

## Authentication workflow

This add-on does not assume the Loophole CLI is already logged in. On every startup it checks authentication status.

If the CLI is not authenticated, the add-on starts the login flow and prints the URL to the logs. It also creates a persistent notification in Home Assistant so the login prompt is visible in the UI.

In practice, the flow is:

```bash
loophole account login
```

Then you follow the URL in the notification or in the add-on log, complete the browser login, and the add-on continues automatically.

## Start-up behavior

Once the user is authenticated and the config is valid, the add-on starts a tunnel like this:

```bash
loophole http 8123 homeassistant --hostname myhome
```

The add-on stores Loophole state in the add-on data directory so that the login session persists across restarts.

## Logs and troubleshooting

Check the add-on log in Home Assistant for:

- authentication status
- login URL output
- tunnel startup messages
- restart warnings
- tunnel exit codes

Common issues:

- `hostname` is empty: the add-on will not start the tunnel.
- `port` is invalid: the add-on requires a valid TCP port.
- authentication required: complete the browser login flow shown in the log or notification.
- tunnel exits unexpectedly: the watchdog thread will try to restart it automatically.

## Notes

- The Loophole CLI is installed automatically during the add-on build.
- Authentication state is kept under the add-on data volume, not in the container filesystem only.
- The add-on monitors the tunnel process and restarts it if it dies.
- The add-on uses Home Assistant’s persistent notifications to surface login steps where they are easy to notice.
