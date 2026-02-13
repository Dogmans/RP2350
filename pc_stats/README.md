# PC Stats Display (RP2350-LCD-1.28)

This sends PC stats over USB serial (CDC) to the RP2350-LCD-1.28 and renders them on the LCD.

## What will be displayed

- CPU temperature (easy with LibreHardwareMonitor web server)
- GPU temperature (easy with NVIDIA NVML)
- FPS (optional, via PresentMon CLI)
- CPU load percent (easy with psutil)
- GPU load percent (easy with NVIDIA NVML)
- RAM used / total (easy with psutil)

## Host setup (Windows)

1. Install LibreHardwareMonitor and enable its Remote Web Server.
   - Set the URL in `LHM_URL` (see host script).

2. Install PresentMon (optional, for FPS).
   - Set `PRESENTMON_PATH` and `PRESENTMON_PROCESS_NAME` in the host script.

3. Create and use the venv (already configured in this workspace).

4. Install Python dependencies:
   - `D:/Documents/git/RP2350/.venv/Scripts/python.exe -m pip install -r pc_stats/requirements-host.txt`

5. Run the host sender:
   - `D:/Documents/git/RP2350/.venv/Scripts/python.exe pc_stats/host/pc_stats_sender.py --port COM5`

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

## Notes

- FPS collection depends on PresentMon output format and may need flag tweaks.
- If CPU temp is missing, confirm LibreHardwareMonitor web server is enabled and the URL is correct.
