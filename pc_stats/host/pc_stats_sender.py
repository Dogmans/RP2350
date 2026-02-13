import argparse
import json
import os
import time
import urllib.request
import subprocess

import psutil
import serial
import pynvml


DEFAULT_BAUD = 115200
DEFAULT_INTERVAL_SEC = 1.0

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


def build_payload(gpu_handle):
    cpu_temp = read_lhm_cpu_temp()
    cpu_load = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    fps = read_presentmon_fps()
    gpu_stats = read_gpu_stats(gpu_handle)

    payload = {
        "cpu_temp_c": cpu_temp,
        "cpu_load": float(cpu_load),
        "ram_used_mb": float(mem.used) / (1024 * 1024),
        "ram_total_mb": float(mem.total) / (1024 * 1024),
        "fps": fps,
    }
    payload.update(gpu_stats)
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True, help="Serial port (e.g., COM5)")
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD)
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL_SEC)
    args = parser.parse_args()

    pynvml.nvmlInit()
    gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)

    with serial.Serial(args.port, args.baud, timeout=1) as ser:
        while True:
            payload = build_payload(gpu_handle)
            line = json.dumps(payload, separators=(",", ":")) + "\n"
            ser.write(line.encode("utf-8"))
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
