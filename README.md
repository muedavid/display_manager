# Installation Instructions

Follow these steps to set up your Raspberry Pi for running the button image display application.

---

## 1. Update System Packages
Make sure your system is up to date:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-pil python3-tk
```

## 3. Setup Virutal Env
Setup venv

```bash
mkdir -p ~/code
cd ~/code
python3 -m venv .venv
source .venv/bin/activate
pip install pillow gpiod
```

## 4. Configure GPIO Permissions

To allow non-root users to access GPIO pins:

*1. Create a udev rules file:*
```bash
sudo nano /etc/udev/rules.d/99-gpio.rules

```

*2. Add the following line:*
```bash
SUBSYSTEM=="gpio*", PROGRAM="/bin/sh -c 'chown -R root:gpio /sys/class/gpio && chmod -R 770 /sys/class/gpio'"

```

*3. Save the file and reload udev rules:*
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```