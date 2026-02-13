import argparse
import time

import serial


DEFAULT_BAUD = 115200
DEFAULT_INTERVAL_SEC = 2.0
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 240
FONT_W = 8
FONT_H = 8

# Standard RGB565 reference values
COLOR_BLACK = 0x0000


COLORS = [
    ("BLACK", 0x0000),
    ("WHITE", 0xFFFF),
    ("RED", 0xF800),
    ("GREEN", 0x07E0),
    ("BLUE", 0x001F),
    ("YELLOW", 0xFFE0),
    ("CYAN", 0x07FF),
    ("MAGENTA", 0xF81F),
]


def send_command(ser, cmd, *args):
    line = ",".join([cmd] + [str(arg) for arg in args]) + "\n"
    ser.write(line.encode("utf-8"))


def show_color(ser, name, fill_color):
    send_command(ser, "fill", fill_color)
    text_w = len(name) * FONT_W
    text_x = max(0, (SCREEN_WIDTH - text_w) // 2)
    text_y = max(0, (SCREEN_HEIGHT - FONT_H) // 2)
    send_command(ser, "text", name, text_x, text_y, COLOR_BLACK)
    send_command(ser, "show")


def main():
    parser = argparse.ArgumentParser(description="RGB565 color test for LCD")
    parser.add_argument("--port", required=True, help="Serial port, e.g. COM8")
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD)
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_SEC)
    parser.add_argument("--loop", action="store_true")
    args = parser.parse_args()

    with serial.Serial(args.port, args.baud, timeout=1) as ser:
        time.sleep(0.2)
        while True:
            for name, fill_color in COLORS:
                show_color(ser, name, fill_color)
                time.sleep(args.interval)
            if not args.loop:
                break


if __name__ == "__main__":
    main()
