# RP2350-LCD-1.28 Demo Map

This maps the extracted demos by language and points to the main entry files.

## demo/ (non-LVGL)

### MicroPython
- Entry script: [docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/Python/RP2350-LCD-1.28/RP2350-LCD-1.28.py](docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/Python/RP2350-LCD-1.28/RP2350-LCD-1.28.py)
- README (EN): [docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/Python/RP2350-LCD-1.28/ReadmeEN.txt](docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/Python/RP2350-LCD-1.28/ReadmeEN.txt)
- Prebuilt UF2: [docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/Python/WAVESHARE-RP2350-LCD-1.28.uf2](docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/Python/WAVESHARE-RP2350-LCD-1.28.uf2)

### C/C++ (Pico SDK)
- Entry point: [docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/C/main.c](docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/C/main.c)
- CMake: [docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/C/CMakeLists.txt](docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/C/CMakeLists.txt)
- Example source: [docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/C/examples/LCD_1in28_test.c](docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/C/examples/LCD_1in28_test.c)
- Prebuilt UF2: [docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/C/uf2/RP2350-LCD-1.28.uf2](docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/C/uf2/RP2350-LCD-1.28.uf2)

### Arduino
- Entry sketch: [docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/Arduino/RP2350-LCD-1.28/RP2350-LCD-1.28.ino](docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/Arduino/RP2350-LCD-1.28/RP2350-LCD-1.28.ino)
- Core display driver: [docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/Arduino/RP2350-LCD-1.28/LCD_1in28.cpp](docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/Arduino/RP2350-LCD-1.28/LCD_1in28.cpp)
- IMU driver: [docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/Arduino/RP2350-LCD-1.28/QMI8658.cpp](docs/waveshare-rp2350/RP2350-LCD-1.28/demo/RP2350-LCD-1.28/Arduino/RP2350-LCD-1.28/QMI8658.cpp)

## lvgl-demo/

### MicroPython (LVGL)
- Example runner: [docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/Python/examples/LCD_1in28_LVGL_test.py](docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/Python/examples/LCD_1in28_LVGL_test.py)
- Example UI: [docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/Python/examples/LVGL_example.py](docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/Python/examples/LVGL_example.py)
- LVGL wrapper: [docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/Python/lib/LVGL.py](docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/Python/lib/LVGL.py)
- LCD driver: [docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/Python/lib/LCD_1in28.py](docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/Python/lib/LCD_1in28.py)
- IMU driver: [docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/Python/lib/QMI8658.py](docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/Python/lib/QMI8658.py)
- Prebuilt UF2: [docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/Python/WAVESHARE-RP2350-LCD-1.28.uf2](docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/Python/WAVESHARE-RP2350-LCD-1.28.uf2)

### C/C++ (LVGL)
- Entry point: [docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/C/main.c](docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/C/main.c)
- CMake: [docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/C/CMakeLists.txt](docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/C/CMakeLists.txt)
- Example source: [docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/C/examples/src/LCD_1in28_LVGL_test.c](docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/C/examples/src/LCD_1in28_LVGL_test.c)
- LVGL config: [docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/C/examples/inc/lv_conf.h](docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/C/examples/inc/lv_conf.h)
- Bundled LVGL library: [docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/C/lib/lvgl](docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/C/lib/lvgl)
- Prebuilt UF2: [docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/C/uf2/RP2350-LCD-1.28.uf2](docs/waveshare-rp2350/RP2350-LCD-1.28/lvgl-demo/RP2350-LCD-1.28-LVGL/C/uf2/RP2350-LCD-1.28.uf2)
