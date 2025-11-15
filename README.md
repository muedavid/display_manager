# Installation Instructions

Follow these steps to set up your Raspberry Pi for running the button image display application.

## 1. Update System Packages
Make sure your system is up to date:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-pil python3-tk
```

## 2. Setup Virutal Env
Setup venv

```bash
mkdir -p ~/code
cd ~/code
python3 -m venv .venv
source .venv/bin/activate
pip install pillow gpiod
```

## 3. Configure GPIO Permissions

To allow non-root users to access GPIO pins:

**1. Create a udev rules file:**
```bash
sudo nano /etc/udev/rules.d/99-gpio.rules

```

**2. Add the following line:**
```bash
SUBSYSTEM=="gpio*", PROGRAM="/bin/sh -c 'chown -R root:gpio /sys/class/gpio && chmod -R 770 /sys/class/gpio'"

```

**3. Save the file and reload udev rules:**
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## 4. Setup Start at BOOT using a Systemd Service

**1. Open a new service file:**
```bash
sudo nano /etc/systemd/system/button_display.service
```

**2. Create Basch Script for Launching the Application:**
Create a script `/home/pi/code/start_display.sh`:
```bash
#!/bin/bash
# Wait 2 seconds for X server to be ready
sleep 2
/home/pi/code/.venv/bin/python /home/pi/code/display_application/display.py
```

Make it executable:
```bash
sudo chmod +x /home/pi/code/start_display.sh
```

**3. Paste the following:**
```bash
[Unit]
Description=Button Image Display
After=graphical.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/code
Environment=DISPLAY=:0
ExecStart=/home/pi/code/start_display.sh
Restart=on-failure

[Install]
WantedBy=graphical.target
```

**4. Enable the service:**
Paste the following:
```bash
sudo systemctl daemon-reload
sudo systemctl enable button_display.service
sudo systemctl start button_display.service
```

## 5. Disable Cursor:
In `/etc/lightdm/lightdm.conf` Add under `[Seat:*]` the following line: `xserver-command=X -nocursor`

## 6. Connect to the Pi

Configure a **static IP** on your development laptop for the Ethernet connection:

- **IP:** `192.168.0.5`  
- **Netmask:** `/24` (equivalent to `255.255.255.0`)

Then connect to the Pi via SSH (default password: `feg`):

```bash
ssh pi@192.168.0.1
```

## 7. Change Wifi Config

Edit the Wi-Fi netplan file on the Pi:
```bash
/etc/netplan/00-wifi.yaml
```
After making changes, apply the new configuration:
```bash
sudo netplan generate
sudo netplan apply
```
