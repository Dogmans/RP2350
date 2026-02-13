import sys
sys.path.append('.')
import lvgl as lv
import lv_utils
import time
import uctypes
import machine
import rp2
import gc
import random

lv.deinit()
lv_utils.event_loop().deinit()

group = None

class LVGL(object):
    def disp_drv_flush_cb(self,disp_drv,area,color_p):

        # pos and data
        w = area.x2 - area.x1 + 1
        h = area.y2 - area.y1 + 1
        size = w * h
        data_view = color_p.__dereference__(size * self.pixel_size)
        self.rgb565_swap_func(data_view, size)
        
        # Set windows
        self.LCD.setWindows(area.x1, area.y1, area.x2+1, area.y2+1)
        self.LCD.cs.value(0)
        self.LCD.dc.value(1)
        
        # send data
        SPI1_BASE = 0x40088000 # FIXME: will be different for another SPI bus?
        SSPDR     = 0x008
        self.dma.config( 
            read   = uctypes.addressof(data_view),
            write  = SPI1_BASE+SSPDR,
            count  = len(data_view),
            ctrl   = self.dma.pack_ctrl(size=0, treq_sel=26, inc_read=True, inc_write=False),
            trigger= True
        )

        while self.dma.active():
            pass
        
        self.LCD.cs.value(1)
        self.disp_drv.flush_ready()
        gc.collect()
        
    def indev_drv_read_cb( self, indev_drv, data):
        
        ud_diff = 0
        lr_diff = 0

        for i in range(3):
            xyz = self.IMU.Read_XYZ()
            ud_diff += xyz[4]  
            lr_diff += xyz[3]

        ud_diff /= 3
        lr_diff /= 3

        # up or down
        if ud_diff > self.IMU.offset and ud_diff > 0 and self.IMU.but_flag:
            self.IMU.encoder_diff -= 2
            self.IMU.but_flag = False
        elif ud_diff < -self.IMU.offset and ud_diff < 0 and self.IMU.but_flag:
            self.IMU.encoder_diff += 2
            self.IMU.but_flag = False
        else:
            self.IMU.encoder_diff = 0
            self.IMU.but_flag = True

        # left or right
        if lr_diff > self.IMU.offset_x:
            self.IMU.encoder_act = lv.INDEV_STATE.PRESSED 
        else:
            self.IMU.encoder_act = lv.INDEV_STATE.RELEASED  
        
        data.enc_diff = self.IMU.encoder_diff
        data.state    = self.IMU.encoder_act
     
        gc.collect()
        
        
    def __init__(self,LCD=None,IMU=None):
        # Init parameter
        self.LCD = LCD
        self.IMU = IMU
        
        # Set color format
        color_format = lv.COLOR_FORMAT.RGB565
        self.pixel_size = lv.color_format_get_size(color_format)
        self.rgb565_swap_func = lv.draw_sw_rgb565_swap
        
        if not lv.is_initialized(): lv.init()

        # create event loop if not yet present
        if not lv_utils.event_loop.is_running(): event_loop=lv_utils.event_loop()

        # Init LVGL display
        self.buf1 = lv.draw_buf_create(self.LCD.width, self.LCD.height // 3, color_format, 0)
        self.buf2 = lv.draw_buf_create(self.LCD.width, self.LCD.height // 3, color_format, 0)   
        self.disp_drv = lv.display_create(self.LCD.width, self.LCD.height)
        self.disp_drv.set_color_format(color_format)
        self.disp_drv.set_draw_buffers(self.buf1, self.buf2)
        self.disp_drv.set_render_mode(lv.DISPLAY_RENDER_MODE.PARTIAL)
        self.disp_drv.set_flush_cb(self.disp_drv_flush_cb)
        
        # Init imu as input device
        self.indev_drv = lv.indev_create()
        self.indev_drv.set_type(lv.INDEV_TYPE.ENCODER)
        self.indev_drv.set_read_cb(self.indev_drv_read_cb)
        
        global group
        group = lv.group_create()
        self.indev_drv.set_group(group)
        
        # Init DMA
        self.dma = rp2.DMA() 








