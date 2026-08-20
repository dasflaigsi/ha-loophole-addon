# Home Assistant Apps Repository

This repository contains Home Assistant apps that extend the functionality of your Home Assistant instance.

## Available Apps

### 1. [Loophole Tunnel](./loophole/README.md)

Expose your Home Assistant instance through a secure HTTPS tunnel using Loophole.

**Features:**
- Secure HTTPS tunnel to your Home Assistant
- Free tunnel service hosted in Europe
- One-click Home Assistant repository integration
- Automatic authentication and tunnel management
- Support for custom hostnames

**Supported architectures:** amd64, aarch64

[Read the Loophole App Documentation](./loophole/README.md)

---

## Installation

To add this repository to your Home Assistant instance, use this button:

[![Open your Home Assistant instance and add this repository.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/dasflaigsi/ha-supervisor-apps)

Or manually:
1. Go to Settings → Add-ons & Services → Add-ons
2. Click the ⋮ menu and select "Manage add-on repositories"
3. Add this repository URL

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE) for details.

This project uses the [Loophole CLI](https://github.com/loophole-dev/loophole-client), which is also licensed under the MIT License.
