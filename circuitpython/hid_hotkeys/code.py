#
# code.py -- turn picoslidertoy into HID controller
# 2025 - @relic-se / Cooper Dalrymple - github.com/relic-se/picoslidertoy
# 2024 - @todbot / Tod Kurt - github.com/todbot/picoslidertoy
#
# based off of "picotouch_test.py":
# picotouch_test.py -- Testing for tiny capsense controller using Pico,
# 2021 - @todbot / Tod Kurt - github.com/todbot/picotouch
#
# To use:
#
# 1. Install needed libraries:
#   circup install adafruit_displayio_ssd1306 adafruit_hid
# 2. Copy over files in this directory to CIRCUITPY:
#   cp circuitpython/hid_hotkeys/* /Volumes/CIRCUITPY/
#

import board
import touchio
import busio
import displayio
import i2cdisplaybus
import adafruit_displayio_ssd1306

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

from touchslider import TouchWheel, TouchSlider
from slider_display import FaderDisplay, WheelDisplay, PadsDisplay

# slider config
MAX_REPEATS = 1  # maximum number of repeats when using sliders

# display config
DISPLAY_WIDTH, DISPLAY_HEIGHT = 128, 64

# pin definitions
faderA_pins = (board.GP4, board.GP0, board.GP28)
faderB_pins = (board.GP5, board.GP1, board.GP27)
faderC_pins = (board.GP3, board.GP2, board.GP26)
wheelX_pins = (board.GP7, board.GP8, board.GP9)
wheelY_pins = (board.GP10, board.GP11, board.GP12)
pad_pins = (board.GP22, board.GP21, board.GP20, board.GP19,
            board.GP18, board.GP17, board.GP16, board.GP6, board.GP13)
i2c_sda_pin, i2c_scl_pin = board.GP15, board.GP14

# set up the touch controls
sliders = (
    TouchSlider(faderA_pins),
    TouchSlider(faderB_pins),
    TouchSlider(faderC_pins),
    TouchWheel(wheelX_pins, offset=0.25),
    TouchWheel(wheelY_pins, offset=0.25),
)
pads = [touchio.TouchIn(pin) for pin in pad_pins]

# virtual on-screen displays of controls
slider_displays = (
    FaderDisplay(10 + 15*0, 10, 8, 35),
    FaderDisplay(10 + 15*1, 10, 8, 35),
    FaderDisplay(10 + 15*2, 10, 8, 35),
    WheelDisplay(70 + 0*35, 25, 15, knob_w=9, phase_offset=-0.25),
    WheelDisplay(70 + 1*35, 25, 15, knob_w=9, phase_offset=-0.25),
)
pad_displays = PadsDisplay(20, 50, n=9, pad_h=10, pad_w=10)

# set up usb hid
keyboard = Keyboard(usb_hid.devices)

# map hid actions
# the "*" button is reserved for mode switching
hid_actions = {
    "button": (
        (Keycode.CONTROL, Keycode.F1,), # 1
        (Keycode.CONTROL, Keycode.F2,), # 2
        (Keycode.CONTROL, Keycode.F3,), # 3
        (Keycode.CONTROL, Keycode.F4,), # 4
        (Keycode.CONTROL, Keycode.F5,), # 5
        (Keycode.CONTROL, Keycode.F6,), # 6
        (Keycode.CONTROL, Keycode.F7,), # 7
        (Keycode.CONTROL, Keycode.F8,), # 8
        (Keycode.CONTROL, Keycode.F9,), # *
    ),
    "slider": ( # (sensitivity, decrement, increment,),
        (16, (Keycode.CONTROL, Keycode.F10,),  (Keycode.CONTROL, Keycode.F11,),), # A
        (16, (Keycode.CONTROL, Keycode.F12,), (Keycode.CONTROL, Keycode.F13,),), # B
        (16, (Keycode.CONTROL, Keycode.F14,), (Keycode.CONTROL, Keycode.F15,),), # C
        (16, (Keycode.CONTROL, Keycode.F16,), (Keycode.CONTROL, Keycode.F17,),), # X
        (16, (Keycode.CONTROL, Keycode.F18,), (Keycode.CONTROL, Keycode.F19,),), # Y
    ),
}

def do_hid_action(group:str, index:int, option:int = 0, repeats:int = 1) -> bool:
    if not group in hid_actions or index >= len(hid_actions[group]):
        return False
    
    action = hid_actions[group][index]
    if not type(action) is tuple:
        return False

    if group is "slider":
        if len(action) < 2 + option:
            return False
        command = action[1 + option]
    else:
        command = action
    
    if not type(command) is tuple or not type(command[0]) is int:
        return False
    
    repeats = int(min(max(repeats, 1), MAX_REPEATS))
    for i in range(repeats):
        keyboard.send(*command)
    return True

# set up the display
dw,dh = 128, 64
displayio.release_displays()
i2c = busio.I2C(scl=i2c_sda_pin, sda=i2c_scl_pin, frequency=1_000_000)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=dw, height=dh)
maingroup = displayio.Group()
display.root_group = maingroup

for s in slider_displays:
    maingroup.append(s)
maingroup.append(pad_displays)

# used to keep track of which note pads are curerntly pressed
pad_state = [False] * len(pads)
slider_state = [None] * len(sliders)

while True:
    for i, slider in enumerate(sliders):
        pos = slider.pos()
        if pos is not None:   # touched!
            slider_displays[i].pos(pos)   # fixme: need ".pos(pos-0.5)" for fader
            slider_displays[i].touch(True)

            segments = hid_actions["slider"][i][0]
            val = int((1-pos) * segments)
            chng = 0
            if slider_state[i] is not None and val != slider_state[i]:
                chng = val - slider_state[i]
                # BUG: jumps when crossing from 0.99 to 0.01
                do_hid_action("slider", i, int(chng > 0), abs(chng))
            slider_state[i] = val

            print("slider:%d: %1.2f val:%d chng:%d" % (i,pos,val,chng))
        else:
            slider_displays[i].touch(False)
            slider_state[i] = None
            
    for i, pad in enumerate(pads):
        v = pad.value
        if i < 8:
            pad_displays.set(i, v)
        if pad_state[i] != v:
            if v:
                do_hid_action("button", i)
            pad_state[i] = v
            print("pad:%d: v:%d" % (i,v))
