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
