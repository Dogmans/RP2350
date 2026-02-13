# Display layout configurations for PC stats
# Each layout defines widgets to display and their positioning

LAYOUTS = [
    {
        "name": "Overview",
        "widgets": [
            {"type": "text", "stat": "cpu_temp", "row": 0, "label": "CPU T"},
            {"type": "text", "stat": "gpu_temp", "row": 1, "label": "GPU T"},
            {"type": "text", "stat": "fps", "row": 2, "label": "FPS"},
            {"type": "bar", "stat": "cpu_load", "row": 3, "label": "CPU", "min": 0, "max": 100, "width": 100, "height": 10},
            {"type": "bar", "stat": "gpu_load", "row": 4, "label": "GPU", "min": 0, "max": 100, "width": 100, "height": 10},
            {"type": "text", "stat": "ram_usage", "row": 5, "label": "RAM"},
        ]
    },
    {
        "name": "Detailed CPU/GPU",
        "widgets": [
            {"type": "colored_bar", "stat": "cpu_temp", "row": 0, "label": "CPU T", "min": 30, "max": 90, "width": 120, "height": 12},
            {"type": "colored_bar", "stat": "gpu_temp", "row": 1, "label": "GPU T", "min": 30, "max": 90, "width": 120, "height": 12},
            {"type": "bar", "stat": "cpu_load", "row": 2, "label": "CPU%", "min": 0, "max": 100, "width": 120, "height": 10},
            {"type": "bar", "stat": "gpu_load", "row": 3, "label": "GPU%", "min": 0, "max": 100, "width": 120, "height": 10},
            {"type": "text", "stat": "fps", "row": 4, "label": "FPS"},
        ]
    },
    {
        "name": "Circle Gauges",
        "widgets": [
            {"type": "circle_gauge", "stat": "cpu_temp", "center_y": 80, "label": "CPU", "min": 30, "max": 90, "radius": 35},
            {"type": "circle_gauge", "stat": "gpu_temp", "center_y": 160, "label": "GPU", "min": 30, "max": 90, "radius": 35},
        ]
    },
    {
        "name": "Gaming Focus",
        "widgets": [
            {"type": "circle_gauge", "stat": "fps", "center_y": 70, "label": "FPS", "min": 0, "max": 144, "radius": 45},
            {"type": "bar", "stat": "gpu_temp", "row": 4, "label": "GPU T", "min": 30, "max": 90, "width": 120, "height": 10},
            {"type": "bar", "stat": "gpu_load", "row": 5, "label": "GPU %", "min": 0, "max": 100, "width": 120, "height": 10},
        ]
    },
]

# Stat formatting and value extraction
STAT_FORMATTERS = {
    "cpu_temp": lambda stats: f"{stats.get('cpu_temp_c') or 0:.0f}C",
    "gpu_temp": lambda stats: f"{stats.get('gpu_temp_c') or 0:.0f}C",
    "cpu_load": lambda stats: f"{stats.get('cpu_load') or 0:.0f}%",
    "gpu_load": lambda stats: f"{stats.get('gpu_load') or 0:.0f}%",
    "fps": lambda stats: f"{stats.get('fps') or 0:.0f}",
    "ram_usage": lambda stats: f"{stats.get('ram_used_mb') or 0:.0f}/{stats.get('ram_total_mb') or 0:.0f}MB",
}

STAT_VALUES = {
    "cpu_temp": lambda stats: stats.get('cpu_temp_c') or 0,
    "gpu_temp": lambda stats: stats.get('gpu_temp_c') or 0,
    "cpu_load": lambda stats: stats.get('cpu_load') or 0,
    "gpu_load": lambda stats: stats.get('gpu_load') or 0,
    "fps": lambda stats: stats.get('fps') or 0,
}
