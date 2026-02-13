import sys
import time
import uselect
import ujson
import math

from lcd_1in28 import LCD_1inch28


COLOR_WHITE = 0xFFFF
COLOR_BLACK = 0x0000


def fmt_temp(value):
    if value is None:
        return "--"
    return "{:.1f}C".format(value)


def fmt_percent(value):
    if value is None:
        return "--"
    return "{:.0f}%".format(value)


def fmt_fps(value):
    if value is None:
        return "--"
    return "{:.0f}".format(value)


def fmt_mem(used_mb, total_mb):
    if used_mb is None or total_mb is None:
        return "--/--"
    return "{:.0f}/{:.0f}MB".format(used_mb, total_mb)


def circle_text_line(lcd, text, y, base_x=10, font_w=8, font_h=8, edge_padding=4):
    center_x = lcd.width // 2
    center_y = lcd.height // 2
    radius = min(lcd.width, lcd.height) // 2
    line_center = y + (font_h // 2)
    dy = line_center - center_y

    if dy * dy >= radius * radius:
        return None, None

    max_half = int(math.sqrt((radius * radius) - (dy * dy)))
    left_x = center_x - max_half + edge_padding
    right_x = center_x + max_half - edge_padding

    if right_x <= base_x:
        return None, None

    if left_x < base_x:
        left_x = base_x

    spaces = (left_x - base_x + font_w - 1) // font_w
    start_x = base_x + (spaces * font_w)
    max_chars = int((right_x - start_x) // font_w)

    if max_chars <= 0:
        return None, None

    if len(text) > max_chars:
        text = text[:max_chars]

    return (" " * spaces) + text, base_x


def draw_stats(lcd, stats):
    lcd.fill(COLOR_WHITE)

    cpu_temp = fmt_temp(stats.get("cpu_temp_c"))
    gpu_temp = fmt_temp(stats.get("gpu_temp_c"))
    fps = fmt_fps(stats.get("fps"))
    cpu_load = fmt_percent(stats.get("cpu_load"))
    gpu_load = fmt_percent(stats.get("gpu_load"))
    ram = fmt_mem(stats.get("ram_used_mb"), stats.get("ram_total_mb"))

    lines = [
        ("PC STATS", 10),
        ("CPU T: " + cpu_temp, 40),
        ("GPU T: " + gpu_temp, 60),
        ("FPS:   " + fps, 80),
        ("CPU %: " + cpu_load, 100),
        ("GPU %: " + gpu_load, 120),
        ("RAM:   " + ram, 140),
    ]

    for text, y in lines:
        line_text, x = circle_text_line(lcd, text, y)
        if line_text is None:
            continue
        lcd.text(line_text, x, y, COLOR_BLACK)

    lcd.show()


def main():
    lcd = LCD_1inch28()
    lcd.set_bl_pwm(40000)

    poller = uselect.poll()
    poller.register(sys.stdin, uselect.POLLIN)

    stats = {}
    last_draw = 0

    while True:
        if poller.poll(100):
            line = sys.stdin.readline()
            if line:
                try:
                    stats = ujson.loads(line)
                except ValueError:
                    pass

        now = time.ticks_ms()
        if time.ticks_diff(now, last_draw) > 500:
            draw_stats(lcd, stats)
            last_draw = now


if __name__ == "__main__":
    main()
