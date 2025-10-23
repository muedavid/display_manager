#!/usr/bin/env python3
import sys
import subprocess
import re
import os
import signal
from PIL import Image, ImageTk
import tkinter as tk

DISPLAY = "HDMI-1"
IMAGE_1 = "feg.png"
IMAGE_2 = "test.png"
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")

XRANDR_REGEX = re.compile(r"^(?P<name>\S+)\sconnected(?:\sprimary)?\s(?P<res>\d+x\d+\+\d+\+\d+)")

root = None
label = None
photo_cache = {}
current_image_index = 0
geom = None


def parse_xrandr():
    out = subprocess.check_output(["xrandr", "--query"], text=True, stderr=subprocess.DEVNULL)
    displays = {}
    for line in out.splitlines():
        m = XRANDR_REGEX.match(line.strip())
        if m:
            displays[m.group("name")] = m.group("res")
    return displays


def geometry_to_tuple(geom):
    w_h, plus = geom.split("+", 1)
    w, h = w_h.split("x")
    x, y = plus.split("+")
    return int(w), int(h), int(x), int(y)


def load_and_scale_image(path, w, h):
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
    return im_resized, new_w, new_h


def show_image_on_monitor(image_path, geom):
    global root, label, photo_cache
    w, h, x, y = geometry_to_tuple(geom)
    im_resized, new_w, new_h = load_and_scale_image(image_path, w, h)

    if root is None:
        root = tk.Tk()
        root.overrideredirect(True)
        root.geometry(f"{w}x{h}+{x}+{y}")
        root.configure(background="black")

        frame = tk.Frame(root, width=w, height=h, bg="black")
        frame.pack(fill="both", expand=True)
        label = tk.Label(frame, bg="black")
        label.place(x=0, y=0)

        # Ensure focus and grab keyboard input
        def ensure_focus(event=None):
            root.focus_force()
            root.focus_set()
            root.grab_set_global()
        root.after(100, ensure_focus)
        root.bind("<FocusOut>", ensure_focus)

        # Bindings
        root.bind("<Escape>", lambda e: root.destroy())
        root.bind("n", toggle_image)

        # Handle Ctrl+C instantly
        signal.signal(signal.SIGINT, lambda s, f: root.destroy())

        # Small polling to keep SIGINT responsive
        def poll_signals():
            root.after(100, poll_signals)
        root.after(100, poll_signals)

    photo = ImageTk.PhotoImage(im_resized)
    photo_cache["current"] = photo
    offset_x = (w - new_w) // 2
    offset_y = (h - new_h) // 2
    label.config(image=photo)
    label.place(x=offset_x, y=offset_y)

    root.update_idletasks()
    root.update()


def toggle_image(event=None):
    global current_image_index
    current_image_index = 1 - current_image_index
    img_name = IMAGE_1 if current_image_index == 0 else IMAGE_2
    img_path = os.path.join(IMAGE_DIR, img_name)
    if not os.path.isfile(img_path):
        print(f"Missing image: {img_path}", file=sys.stderr)
        return
    show_image_on_monitor(img_path, geom)


def main():
    global geom
    img_path = os.path.join(IMAGE_DIR, IMAGE_1)
    if not os.path.isfile(img_path):
        print(f"Image not found: {img_path}", file=sys.stderr)
        sys.exit(1)

    try:
        displays = parse_xrandr()
    except Exception as e:
        print(f"Failed to run xrandr: {e}", file=sys.stderr)
        sys.exit(1)

    if DISPLAY not in displays:
        print(f"Display '{DISPLAY}' not found.", file=sys.stderr)
        sys.exit(1)

    geom = displays[DISPLAY]
    show_image_on_monitor(img_path, geom)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
