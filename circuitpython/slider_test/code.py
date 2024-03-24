#
# picoslidertoy_hwtest_slider_code.py -- Testing for tiny capsense controller using Pico,
# 2024 - @todbot / Tod Kurt - github.com/todbot/picoslidertoy
#
# based off of "picotouch_test.py":
# picotouch_test.py -- Testing for tiny capsense controller using Pico,
# 2021 - @todbot / Tod Kurt - github.com/todbot/picotouch
#
# To use:
#
# 1. Install needed libraries:
#   circup install adafruit_displayio_ssd1306
# 2. Copy over this file as code.py:
#   cp circuitpython/hwtest_display/code.py /Volumes/CIRCUITPY/code.py
#

import time, math
import board
import touchio
import busio
import displayio
import vectorio
import adafruit_displayio_ssd1306

from touchslider import TouchWheel, TouchSlider

faderA_pins = (board.GP4, board.GP0, board.GP28)
faderB_pins = (board.GP5, board.GP1, board.GP27)
faderC_pins = (board.GP3, board.GP2, board.GP26)
wheelX_pins = (board.GP7, board.GP8, board.GP9)
wheelY_pins = (board.GP10, board.GP11, board.GP12)
pad_pins = (board.GP22, board.GP21, board.GP20, board.GP19,
            board.GP18, board.GP17, board.GP16, board.GP6, board.GP13)

faders = (
    TouchSlider(faderA_pins),
    TouchSlider(faderB_pins),
    TouchSlider(faderC_pins),
)

wheelX = TouchWheel(wheelX_pins)
wheelY = TouchWheel(wheelY_pins)

pads = []
for pin in pad_pins:
    pads.append(touchio.TouchIn(pin))

# display
displayio.release_displays()
i2c = busio.I2C(scl=board.GP15, sda=board.GP14, frequency=1_000_000)
dw,dh = 128, 64
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=dw, height=dh, rotation=0)
maingroup = displayio.Group()
display.root_group = maingroup

class FaderDisplay(displayio.Group):
    """Display a simple virtual fader """
    def __init__(self, x,y, w,h, knob_w=10):
        super().__init__(x=x,y=y,scale=1)
        self.w, self.h, self.knob_w = w,h, knob_w
        pW = displayio.Palette(1)
        pB = displayio.Palette(1)
        pW[0], pB[0] = 0xffffff, 0x000000
        self.append(vectorio.Rectangle(pixel_shader=pW, width=1, height=h, x=w//2, y=0))
        self.knob = displayio.Group()
        knob_handle = vectorio.Rectangle(pixel_shader=pW, width=knob_w, height=knob_w, x=0, y=0)
        knob_touch =  vectorio.Rectangle(pixel_shader=pB, width=knob_w-2, height=knob_w-2, x=1, y=1)
        self.knob.append(knob_handle)
        self.knob.append(knob_touch)
        self.knob.y = h//2
        self.append(self.knob)
    def pos(self,v):
        self.knob.y = int(v * (self.h-self.knob_w/2))
    def touch(self,v):
        self.knob[1].hidden = v

class WheelDisplay(displayio.Group):
    def __init__(self, x,y, r, knob_w=8):
        super().__init__(x=x,y=y,scale=1)
        self.r = r
        self.knob_w = knob_w
        pW = displayio.Palette(1)
        pB = displayio.Palette(1)
        pW[0], pB[0] = 0xffffff, 0x000000
        # the outer circle, with black covering up most to make a line
        self.append(vectorio.Circle(pixel_shader=pW, radius=r, x=0, y=0))
        self.append(vectorio.Circle(pixel_shader=pB, radius=r-1, x=0, y=0))
        self.knob = displayio.Group()
        knob_handle = vectorio.Circle(pixel_shader=pW, radius=knob_w//2, x=0, y=0)
        knob_touch = vectorio.Circle(pixel_shader=pB, radius=knob_w//2-1, x=0, y=0)
        self.knob.append(knob_handle)
        self.knob.append(knob_touch)
        self.append(self.knob)
        self.pos(0.5)
    def pos(self,v):
        self.knob.x = int((self.r-self.knob_w/2) * math.sin(v*6.28))
        self.knob.y = int((self.r-self.knob_w/2) * math.cos(v*6.28))
    def touch(self,v):
        self.knob[1].hidden = v

class PadsDisplay(displayio.Group):
    def __init__(self, x,y, n, pad_h=8, pad_w=8):
        super().__init__(x=x,y=y,scale=1)
        self.n = n
        pW = displayio.Palette(1)
        pB = displayio.Palette(1)
        pW[0], pB[0] = 0xffffff, 0x000000
        self.append(vectorio.Rectangle(pixel_shader=pW, width=(pad_w)*n+2, height=pad_h, x=0, y=0))
        for i in range(n):
            self.append(vectorio.Rectangle(pixel_shader=pB, width=pad_w-2, height=pad_w-2, x=2+i*pad_w, y=1))
                
    def set(self,i,v):
        self[i+1].hidden = v
        

faders_disp = displayio.Group()
for i in range(len(faders)):
    fader_disp = FaderDisplay(10 + 15*i, 10, 8, 35)
    faders_disp.append(fader_disp)
maingroup.append(faders_disp)

wheelX_disp = WheelDisplay(70,25, 15, knob_w=9)
wheelY_disp = WheelDisplay(105,25, 15, knob_w=9)
maingroup.append(wheelX_disp)
maingroup.append(wheelY_disp)

pads_disp = PadsDisplay(25, 50, n=9, pad_h=8)
maingroup.append(pads_disp)

while True:
    for i,fader in enumerate(faders):
        pos = fader.pos()
        if pos is not None:   # touched!
            faders_disp[i].pos(pos)
            faders_disp[i].touch(True)
        else:
            faders_disp[i].touch(False)

    pos = wheelX.pos()
    if pos is not None:
        wheelX_disp.pos(pos-0.5)
        wheelX_disp.touch(True)
    else:
        wheelX_disp.touch(False)

    pos = wheelY.pos()
    if pos is not None:
        wheelY_disp.pos(pos-0.5)
        wheelY_disp.touch(True)
    else:
        wheelY_disp.touch(False)

    for i, pad in enumerate(pads):
        pads_disp.set(i,pad.value)
        
    time.sleep(0.05)


