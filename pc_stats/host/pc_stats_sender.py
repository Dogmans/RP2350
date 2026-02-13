import argparse
import json
import math
import os
import time
import urllib.request
import subprocess
from pathlib import Path

import psutil
import serial
import pynvml
from dotenv import load_dotenv

from layouts import LAYOUTS, STAT_FORMATTERS, STAT_VALUES

# Load environment variables from .env file in pc_stats directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


DEFAULT_BAUD = 115200
DEFAULT_INTERVAL_SEC = 1.0
LAYOUT_CYCLE_SEC = 10.0
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 240
TOP_PAD = 14
COLOR_ORDER = os.environ.get("COLOR_ORDER", "RGB").upper()


def rgb565(r, g, b):
    order = COLOR_ORDER
    if order not in {"RGB", "RBG", "GRB", "GBR", "BRG", "BGR"}:
        order = "RGB"
    components = {"R": r, "G": g, "B": b}
    r, g, b = components[order[0]], components[order[1]], components[order[2]]
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


COLOR_WHITE = rgb565(255, 255, 255)
COLOR_BLACK = rgb565(0, 0, 0)
COLOR_RED = rgb565(255, 0, 0)
COLOR_YELLOW = rgb565(255, 255, 0)
COLOR_GREEN = rgb565(0, 255, 0)
COLOR_GRAY = rgb565(180, 180, 180)

# LibreHardwareMonitor web server JSON URL
LHM_URL = os.environ.get("LHM_URL", "")

# PresentMon settings (optional)
PRESENTMON_PATH = os.environ.get("PRESENTMON_PATH", "")
PRESENTMON_PROCESS_NAME = os.environ.get("PRESENTMON_PROCESS_NAME", "")

CPU_TEMP_LABELS = [
    "CCDs Average (Tdie)",      # AMD Ryzen average CCD temp
    "Core (Tctl/Tdie)",          # AMD Ryzen core temp
    "CPU Package",               # Intel
    "CPU (Tctl/Tdie)",
    "CCD1 (Tdie)",
]


def parse_float_from_text(text):
    if text is None:
        return None
    # Skip if it's a voltage reading
    if "V" in text and "°C" not in text:
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
        temp = find_value_by_labels(data, CPU_TEMP_LABELS)
        if temp is not None and temp < 10:
            # Likely found wrong sensor, print debug info
            print(f"DEBUG: Found suspiciously low temp: {temp}C")
        return temp
    except Exception as e:
        print(f"DEBUG: LHM error: {e}")
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


def interpolate_color(value, min_val, max_val):
    """Return color interpolated from green -> yellow -> red based on value."""
    ratio = max(0, min(1, (value - min_val) / (max_val - min_val)))

    if ratio < 0.5:
        # Interpolate from green to yellow (increase red, keep green at max)
        t = ratio * 2  # 0.0 to 1.0
        r = int(255 * t)
        g = 255
        b = 0
    else:
        # Interpolate from yellow to red (decrease green, keep red at max)
        t = (ratio - 0.5) * 2  # 0.0 to 1.0
        r = 255
        g = int(255 * (1 - t))
        b = 0

    return rgb565(r, g, b)


def draw_text_widget(ser, widget, stats, y):
    """Draw a text widget."""
    stat = widget["stat"]
    label = widget.get("label", "")
    text = STAT_FORMATTERS.get(stat, lambda s: "N/A")(stats)
    full_text = f"{label}: {text}" if label else text
    
    offset = circle_text_offset(y)
    if offset is not None:
        send_command(ser, "text", offset + full_text, 10, y, COLOR_BLACK)


def draw_bar_widget(ser, widget, stats, y):
    """Draw a horizontal bar widget."""
    stat = widget["stat"]
    label = widget.get("label", "")
    min_val = widget.get("min", 0)
    max_val = widget.get("max", 100)
    width = widget.get("width", 100)
    height = widget.get("height", 10)
    
    value = STAT_VALUES.get(stat, lambda s: 0)(stats)
    ratio = max(0, min(1, (value - min_val) / (max_val - min_val)))
    fill_width = int(width * ratio)
    
    # Calculate position with circular offset
    offset_spaces = circle_text_offset(y, font_w=8)
    if offset_spaces is None:
        return
    x_offset = len(offset_spaces) * 8
    x = 10 + x_offset
    
    # Draw label to the left of bar if provided
    if label:
        send_command(ser, "text", offset_spaces + label, 10, y + 1, COLOR_BLACK)
        label_width = len(label) * 8
        x = x + label_width + 8  # Add spacing after label
    
    # Draw bar outline
    send_command(ser, "rect", x, y, width, height, COLOR_BLACK)
    # Draw fill
    if fill_width > 2:
        send_command(ser, "fill_rect", x + 1, y + 1, fill_width - 2, height - 2, COLOR_BLACK)
    
    # Draw value text inside bar
    value_text = f"{value:.0f}%"
    text_x = x + (width // 2) - (len(value_text) * 4)
    text_y = y + 1
    send_command(ser, "text", value_text, text_x, text_y, COLOR_WHITE)


def draw_colored_bar_widget(ser, widget, stats, y):
    """Draw a colored bar widget with gradient."""
    stat = widget["stat"]
    label = widget.get("label", "")
    min_val = widget.get("min", 0)
    max_val = widget.get("max", 100)
    width = widget.get("width", 100)
    height = widget.get("height", 10)
    
    value = STAT_VALUES.get(stat, lambda s: 0)(stats)
    ratio = max(0, min(1, (value - min_val) / (max_val - min_val)))
    fill_width = int(width * ratio)
    color = interpolate_color(value, min_val, max_val)
    
    # Calculate position
    offset_spaces = circle_text_offset(y)
    if offset_spaces is None:
        return
    x_offset = len(offset_spaces) * 8
    x = 10 + x_offset
    
    # Draw label to the left of bar
    if label:
        send_command(ser, "text", offset_spaces + label, 10, y + 1, COLOR_BLACK)
        label_width = len(label) * 8
        x = x + label_width + 8  # Add spacing after label
    
    # Draw bar
    send_command(ser, "rect", x, y, width, height, COLOR_BLACK)
    if fill_width > 2:
        send_command(ser, "fill_rect", x + 1, y + 1, fill_width - 2, height - 2, color)
    
    # Draw value text inside bar
    value_text = f"{value:.0f}"
    text_x = x + (width // 2) - (len(value_text) * 4)
    text_y = y + 1
    send_command(ser, "text", value_text, text_x, text_y, COLOR_BLACK)


def draw_circle_gauge_widget(ser, widget, stats):
    """Draw a circular gauge (arc) with center value."""
    stat = widget["stat"]
    label = widget.get("label", "")
    center_y = widget.get("center_y", SCREEN_HEIGHT // 2)
    radius = widget.get("radius", 40)
    thickness = widget.get("thickness", 15)
    min_val = widget.get("min", 0)
    max_val = widget.get("max", 100)
    
    center_x = SCREEN_WIDTH // 2
    value = STAT_VALUES.get(stat, lambda s: 0)(stats)
    ratio = max(0, min(1, (value - min_val) / (max_val - min_val)))
    
    # Draw ring background
    draw_arc(ser, center_x, center_y, radius, 135, -135, COLOR_GRAY, thickness=thickness)

    # Draw value arc
    sweep = 270
    end_angle = 135 - (sweep * ratio)
    draw_arc(ser, center_x, center_y, radius, 135, end_angle, interpolate_color(value, min_val, max_val), thickness=thickness)
    
    # Draw center value
    text_value = f"{value:.0f}"
    text_x = center_x - len(text_value) * 4  # Approximate center
    text_y = center_y - 4
    send_command(ser, "text", text_value, text_x, text_y, COLOR_BLACK)
    
    # Draw label below
    if label:
        label_x = center_x - len(label) * 4
        label_y = center_y + 10
        send_command(ser, "text", label, label_x, label_y, COLOR_BLACK)


def draw_arc(ser, cx, cy, radius, start_deg, end_deg, color, thickness=1):
    """Draw an arc using short line segments."""
    step = 4
    if end_deg > start_deg:
        step = abs(step)
    else:
        step = -abs(step)

    def point_at(r, deg):
        rad = math.radians(deg)
        return (int(cx + r * math.cos(rad)), int(cy - r * math.sin(rad)))

    for t in range(thickness):
        r = radius - t
        angle = start_deg
        while True:
            next_angle = angle + step
            if (step > 0 and next_angle > end_deg) or (step < 0 and next_angle < end_deg):
                next_angle = end_deg
            x1, y1 = point_at(r, angle)
            x2, y2 = point_at(r, next_angle)
            send_command(ser, "line", x1, y1, x2, y2, color)
            if next_angle == end_deg:
                break
            angle = next_angle


def draw_layout(ser, layout, stats):
    """Draw a complete layout."""
    send_command(ser, "fill", COLOR_WHITE)
    
    # Draw layout name at top
    title = layout["name"]
    title_y = TOP_PAD
    title_offset = circle_text_offset(title_y)
    if title_offset is not None:
        send_command(ser, "text", title_offset + title, 10, title_y, COLOR_BLACK)
    
    # Process widgets
    row_y = [25 + TOP_PAD, 45 + TOP_PAD, 65 + TOP_PAD, 90 + TOP_PAD, 110 + TOP_PAD,
             130 + TOP_PAD, 150 + TOP_PAD, 170 + TOP_PAD, 190 + TOP_PAD, 210 + TOP_PAD]
    
    for widget in layout["widgets"]:
        widget_type = widget["type"]
        
        if widget_type == "text":
            row = widget.get("row", 0)
            y = row_y[row] if row < len(row_y) else TOP_PAD + 20 + row * 20
            draw_text_widget(ser, widget, stats, y)
            
        elif widget_type == "bar":
            row = widget.get("row", 0)
            y = row_y[row] if row < len(row_y) else TOP_PAD + 20 + row * 20
            draw_bar_widget(ser, widget, stats, y)
            
        elif widget_type == "colored_bar":
            row = widget.get("row", 0)
            y = row_y[row] if row < len(row_y) else TOP_PAD + 20 + row * 20
            draw_colored_bar_widget(ser, widget, stats, y)
            
        elif widget_type == "circle_gauge":
            draw_circle_gauge_widget(ser, widget, stats)
    
    send_command(ser, "show")


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
        ("PC STATS", 10 + TOP_PAD),
        (f"CPU T: {cpu_temp}", 40 + TOP_PAD),
        (f"GPU T: {gpu_temp}", 60 + TOP_PAD),
        (f"FPS:   {fps}", 80 + TOP_PAD),
        (f"CPU %: {cpu_load}", 100 + TOP_PAD),
        (f"GPU %: {gpu_load}", 120 + TOP_PAD),
        (f"RAM:   {ram}", 140 + TOP_PAD),
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
    parser.add_argument("--no-cycle", action="store_true", help="Don't cycle layouts, stay on first")
    args = parser.parse_args()

    pynvml.nvmlInit()
    gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)

    current_layout_idx = 0
    last_layout_switch = time.time()

    with serial.Serial(args.port, args.baud, timeout=1) as ser:
        time.sleep(2)
        pid = os.getpid()
        print(f"Sender PID: {pid}")
        pid_path = Path(__file__).with_name("sender.pid")
        pid_path.write_text(f"{pid}\n", encoding="utf-8")
        while True:
            # Check if we should cycle layouts
            if not args.no_cycle and time.time() - last_layout_switch >= LAYOUT_CYCLE_SEC:
                current_layout_idx = (current_layout_idx + 1) % len(LAYOUTS)
                last_layout_switch = time.time()
            
            stats = gather_stats(gpu_handle)
            layout = LAYOUTS[current_layout_idx]
            draw_layout(ser, layout, stats)
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
