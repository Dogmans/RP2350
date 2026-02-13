import sys
sys.path.append('.')
sys.path.append('./examples')
import machine
import time
from machine import Pin, PWM
from LCD_1in28 import LCD_1in28
from QMI8658 import QMI8658
from LVGL import LVGL
from LVGL_example import WIDGETS

machine.freq(230_000_000)
    
if __name__=='__main__':
  
    print("LCD_1in28_LVGL_test Demo")
    # Init LCD
    LCD = LCD_1in28()
    LCD.set_bl_pwm(65535 * 60 // 100)
    print("Init LCD done")
    
    # Init IMU
    IMU = QMI8658()
    print("Init IMU done")
    
    # Init LVGL
    LVGL(LCD=LCD,IMU=IMU)
    print("Init LVGL done")
    
    # Init WIDGETS
    WIDGETS(LCD=LCD,IMU=IMU)
    print("Init WIDGETS done")

    while True:
        time.sleep(1)







