# HA Loophole Add-on

This is a Home Assistant Supervisor add-on that manages a Loophole tunnel to expose your Home Assistant instance over HTTPS to the public internet.

## Features

- Simple configuration in Home Assistant settings
- Automatic tunnel startup when configured
- Loophole CLI automatically installed during add-on installation
- Automatic tunnel restart if it crashes
- Verbose logging mode for debugging
- Support for both `amd64` and `aarch64` architectures

## Installation

1. Copy the `ha-loophole-addon` folder into your Home Assistant add-ons repository
2. In Home Assistant, go to Settings → Add-ons → Create local add-on repository and add your repository URL
3. Search for "Loophole Tunnel" in the Add-on Store
4. Click Install

## Configuration

After installing, configure the add-on:

1. **Port**: The HTTP port on your Home Assistant system (typically 80)
2. **Hostname**: Your custom domain name (the tunnel URL will be `https://<hostname>.loophole.site`)
3. **Verbose**: Enable debug logging from Loophole

Then click **Start** to begin the tunnel.

## Initial Setup

On first run, you may need to authenticate with Loophole:

```bash
loophole account login
```

Follow the URL provided in the logs to complete authentication, then restart the add-on.

## Logs

Check the add-on logs in Home Assistant to see:
- Tunnel startup messages
- Loophole tunnel output
- Any errors or warnings

## Notes

- The Loophole CLI is downloaded and installed automatically during add-on installation
- The add-on will automatically restart the tunnel if it crashes
- All logs are stored in the add-on's data directory
