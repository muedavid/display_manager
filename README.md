# Install the following packages

sudo apt update
sudo apt install python3-pil python3-tk

pip install pillow RPi.GPIO

sudo nano /etc/udev/rules.d/99-gpio.rules
SUBSYSTEM=="gpio*", PROGRAM="/bin/sh -c 'chown -R root:gpio /sys/class/gpio && chmod -R 770 /sys/class/gpio'"


https://projects.raspberrypi.org/en/projects/rpi-gpio-wiring-a-button
https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/