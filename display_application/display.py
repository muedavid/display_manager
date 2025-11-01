#!/usr/bin/env python3
import sys
import subprocess
import re
import os
import signal
from PIL import Image, ImageTk
import tkinter as tk
import gpiod
import time

class ButtonImageDisplay:
    XRANDR_REGEX = re.compile(
        r"^(?P<name>\S+)\sconnected(?:\sprimary)?\s(?P<res>\d+x\d+\+\d+\+\d+)"
    )

    DEBOUNCE_MS = 20

    def __init__(self, button_pin=17, chip="/dev/gpiochip0",
                 display="HDMI-A-2", image1="feg.png", image2="test.png", image_dir=None):
        self.button_pin = button_pin
        self.chip_path = chip
        self.display_name = display
        self.image1_file = image1
        self.image2_file = image2
        self.image_dir = image_dir or os.path.join(os.path.dirname(__file__), "images")

        self.root = None
        self.label = None
        self.photo_cache = {}
        self.geom = None
        self.last_state = None
        self.last_change_time = time.time()

        # Setup gpiod
        self.chip = gpiod.Chip(self.chip_path)
        settings = gpiod.LineSettings()
        settings.direction = gpiod.line.Direction.INPUT
        settings.bias = gpiod.line.Bias.PULL_UP
        self.request = self.chip.request_lines(
            consumer="button",
            config={self.button_pin: settings},
        )
        self.last_state = self.request.get_values()[0]

        # Determine display geometry
        self.geom = self.get_display_geometry()

        # Preload images
        self.image1 = self.load_image(os.path.join(self.image_dir, self.image1_file))
        self.image2 = self.load_image(os.path.join(self.image_dir, self.image2_file))

        # Show initial image
        self.show_image(self.image1)

        # Start polling button
        self.poll_button()

        # Bind cleanup
        signal.signal(signal.SIGINT, lambda s, f: self.cleanup_and_exit())

    def parse_xrandr(self):
        out = subprocess.check_output(
            ["xrandr", "--query"], text=True, stderr=subprocess.DEVNULL
        )
        displays = {}
        for line in out.splitlines():
            m = self.XRANDR_REGEX.match(line.strip())
            if m:
                displays[m.group("name")] = m.group("res")
        return displays

    def get_display_geometry(self):
        try:
            displays = self.parse_xrandr()
        except Exception as e:
            print(f"Failed to run xrandr: {e}", file=sys.stderr)
            sys.exit(1)

        if self.display_name not in displays:
            print(f"Display '{self.display_name}' not found.", file=sys.stderr)
            sys.exit(1)

        geom_str = displays[self.display_name]
        w_h, plus = geom_str.split("+", 1)
        w, h = w_h.split("x")
        x, y = plus.split("+")
        return int(w), int(h), int(x), int(y)

    def load_image(self, path):
        if not os.path.isfile(path):
            print(f"Image not found: {path}", file=sys.stderr)
            sys.exit(1)
        w, h, _, _ = self.geom
        im = Image.open(path)
        im_ratio = im.width / im.height
        screen_ratio = w / h
        if im_ratio > screen_ratio:
            new_w = w
            new_h = int(round(w / im_ratio))
        else:
            new_h = h
            new_w = int(round(h * im_ratio))
        im_resized = im.resize((new_w, new_h), Image.LANCZOS)
        return im_resized

    def show_image(self, pil_image):
        w, h, x, y = self.geom
        if self.root is None:
            self.root = tk.Tk()
            self.root.overrideredirect(True)
            self.root.geometry(f"{w}x{h}+{x}+{y}")
            self.root.configure(background="black")
            frame = tk.Frame(self.root, width=w, height=h, bg="black")
            frame.pack(fill="both", expand=True)
            self.label = tk.Label(frame, bg="black")
            self.label.place(x=0, y=0)

            # Keep focus
            def ensure_focus(event=None):
                self.root.focus_force()
                self.root.focus_set()
                self.root.grab_set_global()
            self.root.after(100, ensure_focus)
            self.root.bind("<FocusOut>", ensure_focus)

            # ESC = exit
            self.root.bind("<Escape>", lambda e: self.cleanup_and_exit())

        photo = ImageTk.PhotoImage(pil_image)
        self.photo_cache["current"] = photo
        self.label.config(image=photo)
        self.label.place(x=0, y=0)
        self.root.update_idletasks()
        self.root.update()

    def poll_button(self):
        value = self.request.get_values()[0]
        now = time.time()
        if value != self.last_state and (now - self.last_change_time) * 1000 >= self.DEBOUNCE_MS:
            # gpiod 2.4.0 returns enum-like Value objects; compare as string
            if str(value) == "Value.INACTIVE":  # pressed
                self.show_image(self.image2)
            elif str(value) == "Value.ACTIVE":  # released
                self.show_image(self.image1)
            self.last_state = value
            self.last_change_time = now
        self.root.after(10, self.poll_button)  # poll every 10 ms for fast switch

    def cleanup_and_exit(self):
        self.request.release()
        self.chip.close()
        if self.root:
            self.root.destroy()
        sys.exit(0)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ButtonImageDisplay(
        button_pin=17,
        chip="/dev/gpiochip0",
        display="HDMI-A-2",
        image1="feg.png",
        image2="test.png",
    )
    app.run()
