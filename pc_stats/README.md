# PC Stats Display (RP2350-LCD-1.28)

This sends CSV drawing commands over USB serial (CDC) to the RP2350-LCD-1.28 to render PC stats on the circular LCD.

The host gathers stats and sends framebuffer commands like:
- `fill,65535` (clear screen)
- `text,CPU T: 45.0C,10,40,0` (draw text with circular offset)
- `show` (flush to display)

The device parses CSV and calls `lcd.{method}(*args)` for rapid prototyping.

## What will be displayed

- CPU temperature (via LibreHardwareMonitor web server)
- GPU temperature (via NVIDIA NVML)
- FPS (optional, via PresentMon CLI)
- CPU load percent (via psutil)
- GPU load percent (via NVIDIA NVML)
- RAM used / total (via psutil)

## Host setup (Windows)

1. Install LibreHardwareMonitor and enable its Remote Web Server.

2. Install PresentMon (optional, for FPS).

3. Create a `.env` file in `pc_stats/` with your configuration:
   - Copy `.env.example` to `.env` and edit the values:
   ```
   LHM_URL=http://localhost:8085/data.json
   PRESENTMON_PATH=C:/path/to/presentmon.exe
   PRESENTMON_PROCESS_NAME=YourGame.exe
   ```

4. Create and use the venv (already configured in this workspace).

5. Install Python dependencies:
   - `D:/Documents/git/RP2350/.venv/Scripts/python.exe -m pip install -r pc_stats/requirements-host.txt`

6. Run the host sender:
   - `D:/Documents/git/RP2350/.venv/Scripts/python.exe pc_stats/host/pc_stats_sender.py --port COM8`

## Device setup (MicroPython)

1. Flash a MicroPython UF2 for RP2350 from Waveshare (see docs).
2. Copy these files to the board:
   - `pc_stats/device/lcd_1in28.py`
   - `pc_stats/device/pc_stats_display.py` (rename to `main.py` if you want auto-start)
3. Reset the board.

## Deploy (mpremote)

- Copy the files to a board on COM8:
   - `mpremote connect COM8 fs cp pc_stats/device/lcd_1in28.py :lcd_1in28.py`
   - `mpremote connect COM8 fs cp pc_stats/device/pc_stats_display.py :pc_stats_display.py`
   - Optional auto-start: `mpremote connect COM8 fs cp pc_stats/device/pc_stats_display.py :main.py`
   - Reset: `mpremote connect COM8 reset`

- Or use the helper script:
   - `powershell -ExecutionPolicy Bypass -File pc_stats/deploy.ps1 -Port COM8`
   - The script creates `pc_stats/.venv-deploy` and installs `requirements-deploy.txt` automatically.
   - Add `-AsMain` to also copy `main.py`.

## Architecture

- **Host**: Gathers stats, formats text, calculates circular display offsets, sends CSV commands
- **Device**: Parses CSV lines, calls `lcd.{method}(*args)` using `getattr`, minimal logic

This "remote framebuffer" approach keeps the device simple and makes iteration fast - you can manually send commands via Serial terminal for debugging.

## Notes

- FPS collection depends on PresentMon output format and may need flag tweaks.
- If CPU temp is missing, confirm LibreHardwareMonitor web server is enabled and the URL is correct.
- Text lines near top/bottom are padded with spaces to fit the circular display.

## Configuration (.env)

The `.env` file in `pc_stats/` lets you customize:

- **LHM_URL**: LibreHardwareMonitor web server URL (for CPU stats)
- **PRESENTMON_PATH**: Path to PresentMon executable (for FPS)
- **PRESENTMON_PROCESS_NAME**: Name of the game/process to monitor FPS
- **UI_BG**: Background color for the display, as `R,G,B` (e.g. `0,0,0` for black)
- **UI_FG**: Foreground/text color, as `R,G,B` (e.g. `255,255,255` for white)

Example `.env`:
```
LHM_URL=http://localhost:8085/data.json
PRESENTMON_PATH=C:/path/to/presentmon.exe
PRESENTMON_PROCESS_NAME=YourGame.exe
UI_BG=0,0,0
UI_FG=255,255,255
```

If `UI_BG` and `UI_FG` are not set, the display defaults to black text on a white background.

Restart the sender after changing `.env` to apply new colors.

## Layouts

Display layouts are defined in `host/layouts.py` as Python dictionaries. Each layout specifies a set of widgets and their positions/types:

- **Overview**: Text and bar widgets for CPU/GPU stats, FPS, RAM.
- **Detailed CPU/GPU**: Colored bars for temperatures, standard bars for load, FPS.
- **Circle Gauges**: Circular gauge widgets for CPU/GPU temps.
- **Gaming Focus**: Large FPS circle gauge, GPU temp/load bars.

Each widget entry includes:
- `type`: Widget type (`text`, `bar`, `colored_bar`, `circle_gauge`)
- `stat`: Stat key (e.g. `cpu_temp`, `gpu_load`)
- `label`: Display label
- Positioning: `row`, `center_y`, `radius`, `width`, `height`, etc.

Layouts are selected in the host code and determine what stats are shown and how they are rendered on the display.

Stat formatting and extraction is handled by `STAT_FORMATTERS` and `STAT_VALUES` in `layouts.py`.
