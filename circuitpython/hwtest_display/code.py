#
# picoslidertoy_hwtest_display_code.py -- Testing for tiny capsense controller using Pico,
# 2024 - @todbot / Tod Kurt - github.com/todbot/picoslidertoy
#
# based off of "picotouch_hwtest_code.py":
# picotouch_hwtest_code.py -- Testing for tiny capsense controller using Pico,
# 2021 - @todbot / Tod Kurt - github.com/todbot/picotouch
#
# To use:
#
# 1. Install needed libraries:
#   circup install adafruit_displayio_ssd1306
# 2. Copy over this file as code.py:
#   cp circuitpython/hwtest_display/code.py /Volumes/CIRCUITPY/code.py
#

import time
import board
import touchio
import busio
import displayio
import vectorio
import adafruit_displayio_ssd1306

touch_threshold_adjust = 100

faderA_pins = (board.GP4, board.GP0, board.GP28)
faderB_pins = (board.GP5, board.GP1, board.GP27)
faderC_pins = (board.GP3, board.GP2, board.GP26)
wheelX_pins = (board.GP7, board.GP8, board.GP9)
wheelY_pins = (board.GP10, board.GP11, board.GP12)
pad_pins = (board.GP22, board.GP21, board.GP20, board.GP19,
            board.GP18, board.GP17, board.GP16, board.GP6, board.GP13)

touch_pins = {
    'faderA': faderA_pins,
    'faderB': faderB_pins,
    'faderC': faderC_pins,
    'wheelX': wheelX_pins,
    'wheelY': wheelY_pins,
    'pads': pad_pins
}

touchins = {}  # raw touchio objs

for group_name, pin_group in touch_pins.items():
    touchin_group = []
    for pin in pin_group:
        print("pin:", pin)
        touchin = touchio.TouchIn(pin)
        touchin.threshold += touch_threshold_adjust
        touchin_group.append(touchin)
    touchins[group_name] = touchin_group

# display
displayio.release_displays()
i2c = busio.I2C(scl=board.GP15, sda=board.GP14, frequency=1_000_000)
dw,dh = 128, 64
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=dw, height=dh, rotation=0)
maingroup = displayio.Group()
display.root_group = maingroup

# set up display info
def make_fader_parts(pW,pB,x,y):
    g = displayio.Group()
    # surrounding white rect
    g.append(vectorio.Rectangle(pixel_shader=pW, width=8, height=37, x=x, y=y))
    # black squares to cover up that rect
    g.append(vectorio.Rectangle(pixel_shader=pB, width=6, height=10, x=x+1, y=y+1))
    g.append(vectorio.Rectangle(pixel_shader=pB, width=6, height=10, x=x+1, y=y+1+12))
    g.append(vectorio.Rectangle(pixel_shader=pB, width=6, height=10, x=x+1, y=y+1+12+12))
    return g

def make_wheel_parts(pW,pB,x,y):
    g = displayio.Group()
    # surrounding rect
    g.append(vectorio.Rectangle(pixel_shader=pW, width=8, height=37, x=x, y=y))
    g.append(vectorio.Rectangle(pixel_shader=pB, width=6, height=10, x=x+1, y=y+1))
    g.append(vectorio.Rectangle(pixel_shader=pB, width=6, height=10, x=x+1, y=y+1+12))
    g.append(vectorio.Rectangle(pixel_shader=pB, width=6, height=10, x=x+1, y=y+1+12+12))
    return g

def make_pad_parts(pW,pB,x,y,n):
    g = displayio.Group()
    g.append(vectorio.Rectangle(pixel_shader=pW, width=8*n, height=8, x=x, y=y))
    for i in range(n):
        g.append(vectorio.Rectangle(pixel_shader=pB, width=6, height=6, x=x+1+i*8, y=y+1))
    return g
        
    
pW = displayio.Palette(1)
pW[0] = 0xffffff
pB = displayio.Palette(1)
pB[0] = 0;
xo,yo = 5,10

fader_partsA = make_fader_parts(pW,pB, xo+0, yo)
fader_partsB = make_fader_parts(pW,pB, xo+12, yo)
fader_partsC = make_fader_parts(pW,pB, xo+24, yo)
wheel_partsX = make_fader_parts(pW,pB, xo+80, yo)
wheel_partsY = make_fader_parts(pW,pB, xo+100, yo)
pad_parts = make_pad_parts(pW,pB, xo+20, yo+40, len(touchins['pads']))
for g in (fader_partsA, fader_partsB, fader_partsC, wheel_partsX, wheel_partsY, pad_parts ):
    maingroup.append(g)


print("\n----------")
print("picoslidertoy hwtest_display hello")

while True:
    for i, touch in enumerate(touchins['faderA']):
        fader_partsA[i+1].hidden = touch.value
    for i, touch in enumerate(touchins['faderB']):
        fader_partsB[i+1].hidden = touch.value
    for i, touch in enumerate(touchins['faderC']):
        fader_partsC[i+1].hidden = touch.value
    for i, touch in enumerate(touchins['wheelX']):
        wheel_partsX[i+1].hidden = touch.value
    for i, touch in enumerate(touchins['wheelY']):
        wheel_partsY[i+1].hidden = touch.value
    for i, touch in enumerate(touchins['pads']):
        pad_parts[i+1].hidden = touch.value
    
    
