# Raspberry Pi Access Point Setup

This project automates the setup of a Raspberry Pi as
an isolated wireless access point (AP) for ethical hacking courses.
Utilizing `hostapd` for creating the AP, and `dnsmasq`
for DHCP and DNS services and configuring network interfaces
via scripts. It simplifies network management and ensures
persistent configurations through reboots.

Once active, the RPi is not intended to access other networks,
and several steps have been taken to harden the device and
hamper certain networking operations without interfering with
the purpose of the project.

## Prerequisites

- Raspberry Pi with Raspberry Pi OS installed.
- Wireless network adapter compatible with AP mode.
- Root privileges on the Raspberry Pi.
- See the requirements.txt file for a list of required packages 

## Installation
To install packages, access to the internet, and a
correct system clock is required.
Accessing the internet can be a achieved by either
hooking up a LAN cable to an established network,
or connecting to a wireless network with internet access.

### 1. Set the System Date

Ensure that the system date is correct, as this can
affect package installation and SSL/TLS verification:

```bash
sudo date -s "YYYY-MM-DD HH:MM:SS"
```
Replace `YYYY-MM-DD HH:MM:SS` with the current year (YYYY),
month (MM), day (DD), hour (HH), minute (MM), and seconds (SS).

### 2. Install Required Packages

Install the necessary packages using `apt`, by first updating the repository:

```bash
sudo apt update
```

Afterwards, install packages either individually or collectively.
```bash
sudo apt install -y [PACKAGE_NAME]
# OR collectively
cat requirements.txt | xargs sudo apt install -y
```

Remember to replace `[PACKAGE_NAME]` with the package names
found in the requirements.txt file.

## Usage
Navigate the terminal to where the package is located.

It could be something like this.
```bash
cd /home/$USER/Project10
```
Run the program with the following options as needed:

| Operator | Description
|:---|:---|
| `-v`           | Enable verbose output for detailed logging. |
| `-i input_file`| Specify an `.ini` configuration file to customize the AP settings. |
| `-y`           | Automatically accept all prompts (useful for non-interactive setups). |

### Example Command

```bash
sudo python3 src/tool.py -v
sudo python3 src/tool.py -v -i relative/path/to/ini_file.ini -y
```

Replace `relative/path/to/ini_file.ini` with your configuration.

## Options

| Option      | Description                               |
|-------------|-------------------------------------------|
| `-v`        | Enable verbose mode for detailed output.  |
| `-i FILE`   | Specify an `.ini` file for configurations.|
| `-y`        | Auto-accept all prompts during setup.     |

## Troubleshooting

For issues during installation or operation, refer to the
verbose output provided by the `-v` option. Check system logs
for more detailed error messages if necessary:

```bash
journalctl -xe
```

## MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.