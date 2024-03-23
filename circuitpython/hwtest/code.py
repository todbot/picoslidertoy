#
# picoslidertoy_test.py -- Testing for tiny capsense controller using Pico,
# 2024 - @todbot / Tod Kurt - github.com/todbot/picoslidertoy
#
# based off of "picotouch_test.py":
# picotouch_test.py -- Testing for tiny capsense controller using Pico,
# 2021 - @todbot / Tod Kurt - github.com/todbot/picotouch
#
# To use:
#
# 2. Copy over this file as code.py:
#   cp circuitpython/hwtest/code.py /Volumes/CIRCUITPY/code.py
#
# Need 1M pull-down on each input
#

import time
import board
import touchio

touch_threshold_adjust = 100

touch_pins = (
    board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5,
    board.GP6, board.GP7, board.GP8, board.GP9, board.GP10, board.GP11,
    board.GP12, board.GP13,  board.GP16, board.GP17, board.GP18, board.GP19,
    board.GP20, board.GP21, board.GP22, board.GP26, board.GP27, board.GP28
)

touchins = [] 
for pin in touch_pins:
    print("pin:", pin)
    touchin = touchio.TouchIn(pin)
    touchin.threshold += touch_threshold_adjust
    touchins.append(touchin)  # for debug
num_touch_pads = len(touch_pads)

print("\n----------")
print("picoslidertoy hwtest hello")
while True:
    for i in range(len(touchins)):
        touch = touchins[i]
        print("%d  " % touch.value, end='')
    print()
