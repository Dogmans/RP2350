import argparse
import json
import math
import os
import time
import urllib.request
import subprocess

import psutil
import serial
import pynvml


DEFAULT_BAUD = 115200
DEFAULT_INTERVAL_SEC = 1.0
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 240
COLOR_WHITE = 0xFFFF
COLOR_BLACK = 0x0000

# LibreHardwareMonitor web server JSON URL
LHM_URL = os.environ.get("LHM_URL", "")

# PresentMon settings (optional)
PRESENTMON_PATH = os.environ.get("PRESENTMON_PATH", "")
PRESENTMON_PROCESS_NAME = os.environ.get("PRESENTMON_PROCESS_NAME", "")

CPU_TEMP_LABELS = [
    "CPU Package",
    "CPU (Tctl/Tdie)",
    "CPU CCD",
    "CPU",
]


def parse_float_from_text(text):
    if text is None:
        return None
    cleaned = "".join(ch if (ch.isdigit() or ch == "." or ch == "-") else " " for ch in text)
    for token in cleaned.split():
        try:
            return float(token)
        except ValueError:
            continue
    return None


def find_value_by_labels(node, labels):
    if isinstance(node, dict):
        name = node.get("Text") or node.get("Name") or ""
        value = node.get("Value") or node.get("value")
        if value and any(label.lower() in name.lower() for label in labels):
            parsed = parse_float_from_text(value)
            if parsed is not None:
                return parsed
        for child in node.get("Children", []) + node.get("children", []):
            found = find_value_by_labels(child, labels)
            if found is not None:
                return found
    elif isinstance(node, list):
        for item in node:
            found = find_value_by_labels(item, labels)
            if found is not None:
                return found
    return None


def read_lhm_cpu_temp():
    if not LHM_URL:
        return None
    try:
        with urllib.request.urlopen(LHM_URL, timeout=2) as response:
            data = json.loads(response.read().decode("utf-8"))
        return find_value_by_labels(data, CPU_TEMP_LABELS)
    except Exception:
        return None


def read_presentmon_fps():
    if not PRESENTMON_PATH or not PRESENTMON_PROCESS_NAME:
        return None
    try:
        output_file = "presentmon_sample.csv"
        cmd = [
            PRESENTMON_PATH,
            "-process_name",
            PRESENTMON_PROCESS_NAME,
            "-output_file",
            output_file,
            "-timed",
            "1",
        ]
        subprocess.run(cmd, check=False, capture_output=True, text=True)
        if not os.path.exists(output_file):
            return None
        with open(output_file, "r", encoding="utf-8", errors="ignore") as handle:
            lines = [line.strip() for line in handle.readlines() if line.strip()]
        if len(lines) < 2:
            return None
        header = lines[0].split(",")
        last_row = lines[-1].split(",")
        fps_index = None
        for i, name in enumerate(header):
            if name.lower() in ("averagefps", "fps"):
                fps_index = i
                break
        if fps_index is None or fps_index >= len(last_row):
            return None
        return float(last_row[fps_index])
    except Exception:
        return None


def read_gpu_stats(handle):
    try:
        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
        mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
        return {
            "gpu_temp_c": float(temp),
            "gpu_load": float(util.gpu),
            "gpu_mem_used_mb": float(mem.used) / (1024 * 1024),
            "gpu_mem_total_mb": float(mem.total) / (1024 * 1024),
        }
    except Exception:
        return {
            "gpu_temp_c": None,
            "gpu_load": None,
            "gpu_mem_used_mb": None,
            "gpu_mem_total_mb": None,
        }


def gather_stats(gpu_handle):
    cpu_temp = read_lhm_cpu_temp()
    cpu_load = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    fps = read_presentmon_fps()
    gpu_stats = read_gpu_stats(gpu_handle)

    return {
        "cpu_temp_c": cpu_temp,
        "cpu_load": float(cpu_load),
        "ram_used_mb": float(mem.used) / (1024 * 1024),
        "ram_total_mb": float(mem.total) / (1024 * 1024),
        "fps": fps,
        **gpu_stats,
    }


def fmt_temp(value):
    if value is None:
        return "--"
    return f"{value:.1f}C"


def fmt_percent(value):
    if value is None:
        return "--"
    return f"{value:.0f}%"


def fmt_fps(value):
    if value is None:
        return "--"
    return f"{value:.0f}"


def fmt_mem(used_mb, total_mb):
    if used_mb is None or total_mb is None:
        return "--/--"
    return f"{used_mb:.0f}/{total_mb:.0f}MB"


def circle_text_offset(y, base_x=10, font_w=8, font_h=8, edge_padding=4):
    """Calculate horizontal offset for circular display."""
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 2
    line_center = y + (font_h // 2)
    dy = line_center - center_y

    if dy * dy >= radius * radius:
        return None

    max_half = int(math.sqrt((radius * radius) - (dy * dy)))
    left_x = center_x - max_half + edge_padding

    if left_x < base_x:
        left_x = base_x

    spaces_needed = (left_x - base_x + font_w - 1) // font_w
    return " " * spaces_needed


def send_command(ser, cmd, *args):
    """Send CSV command to device."""
    line = ",".join([cmd] + [str(arg) for arg in args]) + "\n"
    ser.write(line.encode("utf-8"))


def draw_stats(ser, stats):
    """Send drawing commands to device."""
    send_command(ser, "fill", COLOR_WHITE)

    cpu_temp = fmt_temp(stats["cpu_temp_c"])
    gpu_temp = fmt_temp(stats["gpu_temp_c"])
    fps = fmt_fps(stats["fps"])
    cpu_load = fmt_percent(stats["cpu_load"])
    gpu_load = fmt_percent(stats["gpu_load"])
    ram = fmt_mem(stats["ram_used_mb"], stats["ram_total_mb"])

    lines = [
        ("PC STATS", 10),
        (f"CPU T: {cpu_temp}", 40),
        (f"GPU T: {gpu_temp}", 60),
        (f"FPS:   {fps}", 80),
        (f"CPU %: {cpu_load}", 100),
        (f"GPU %: {gpu_load}", 120),
        (f"RAM:   {ram}", 140),
    ]

    for text, y in lines:
        offset = circle_text_offset(y)
        if offset is not None:
            send_command(ser, "text", offset + text, 10, y, COLOR_BLACK)

    send_command(ser, "show")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True, help="Serial port (e.g., COM8)")
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD)
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_SEC)
    args = parser.parse_args()

    pynvml.nvmlInit()
    gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)

    with serial.Serial(args.port, args.baud, timeout=1) as ser:
        time.sleep(2)
        while True:
            stats = gather_stats(gpu_handle)
            draw_stats(ser, stats)
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
