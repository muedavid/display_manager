#!/usr/bin/env python3
import gpiod
import time

CHIP = "/dev/gpiochip0"
BUTTON_PIN = 17  # BCM pin

chip = gpiod.Chip(CHIP)

# Configure line as input with pull-up
settings = gpiod.LineSettings()
settings.direction = gpiod.line.Direction.INPUT
settings.bias = gpiod.line.Bias.PULL_UP

# Request the line (no edge detection)
request = chip.request_lines(
    consumer="button",
    config={BUTTON_PIN: settings},
)

print("Waiting for button...")

last_state = request.get_values()[0]  # initial state: 1 if not pressed, 0 if pressed

try:
    while True:
        value = request.get_values()[0]

        if value != last_state:
            if str(value) == "Value.INACTIVE":
                print("pressed")
            else:
                print("released")
            last_state = value

        time.sleep(0.005)  # 5 ms poll interval

except KeyboardInterrupt:
    pass
finally:
    request.release()
    chip.close()
