import sys
import time
import uselect
import ujson

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


def draw_stats(lcd, stats):
    lcd.fill(COLOR_WHITE)
    lcd.text("PC STATS", 10, 10, COLOR_BLACK)

    cpu_temp = fmt_temp(stats.get("cpu_temp_c"))
    gpu_temp = fmt_temp(stats.get("gpu_temp_c"))
    fps = fmt_fps(stats.get("fps"))
    cpu_load = fmt_percent(stats.get("cpu_load"))
    gpu_load = fmt_percent(stats.get("gpu_load"))
    ram = fmt_mem(stats.get("ram_used_mb"), stats.get("ram_total_mb"))

    lcd.text("CPU T: " + cpu_temp, 10, 40, COLOR_BLACK)
    lcd.text("GPU T: " + gpu_temp, 10, 60, COLOR_BLACK)
    lcd.text("FPS:   " + fps, 10, 80, COLOR_BLACK)
    lcd.text("CPU %: " + cpu_load, 10, 100, COLOR_BLACK)
    lcd.text("GPU %: " + gpu_load, 10, 120, COLOR_BLACK)
    lcd.text("RAM:   " + ram, 10, 140, COLOR_BLACK)
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
