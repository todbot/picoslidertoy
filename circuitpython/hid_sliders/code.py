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
#   circup install adafruit_displayio_ssd1306 adafruit_hid adafruit_display_text
# 2. Copy over files in this directory to CIRCUITPY:
#   cp circuitpython/hid_sliders/* /Volumes/CIRCUITPY/
#

import board
import touchio
import busio
import displayio
import i2cdisplaybus
import adafruit_displayio_ssd1306
import terminalio
from adafruit_display_text.label import Label
from adafruit_display_emoji_text import EmojiLabel

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

from touchslider import TouchWheel, TouchSlider
from slider_display import FaderDisplay, WheelDisplay, PadsDisplay

# slider config
SLIDER_SEGMENTS = 32 # increase/decrease for more/less sensitivity
MAX_REPEATS     = 3  # maximum number of repeats when using sliders

# hid modes
MODE_SHORTCUTS  = "Hotkey"
MODE_MEDIA      = "Media"
MODES           = (MODE_SHORTCUTS, MODE_MEDIA)
DEFAULT_MODE    = MODE_SHORTCUTS

# display config
DISPLAY_WIDTH, DISPLAY_HEIGHT = 128, 64
PAD_H, PAD_W = 11, 11

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
    FaderDisplay(10 + 15*0, 0, 10, 45),
    FaderDisplay(10 + 15*1, 0, 10, 45),
    FaderDisplay(10 + 15*2, 0, 10, 45),
    WheelDisplay(72 + 0*34, 30, 13, knob_w=6, phase_offset=-0.25),
    WheelDisplay(72 + 1*34, 30, 13, knob_w=6, phase_offset=-0.25),
)
PAD_X = (DISPLAY_WIDTH - ((len(pads) - 1) * PAD_W)) // 2
pad_displays = PadsDisplay(PAD_X, 50, n=8, pad_h=PAD_H, pad_w=PAD_W)

# labels
title_label = Label(terminalio.FONT, color=0x000000, background_color=0xffffff,
    anchor_point = (0.5, 0.0),
    anchored_position = (88, 0),
    padding_top = 1, padding_bottom = 1, padding_left = 3, padding_right = 3,
)

# set up usb hid
keyboard = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)

# map hid actions
# the "*" button is reserved for mode switching
hid_actions = {
    MODE_SHORTCUTS: {
        "button": (
            (keyboard, "", (Keycode.CONTROL, Keycode.F1,)), # 1
            (keyboard, "", (Keycode.CONTROL, Keycode.F2,)), # 2
            (keyboard, "", (Keycode.CONTROL, Keycode.F3,)), # 3
            (keyboard, "", (Keycode.CONTROL, Keycode.F4,)), # 4
            (keyboard, "", (Keycode.CONTROL, Keycode.F5,)), # 5
            (keyboard, "", (Keycode.CONTROL, Keycode.F6,)), # 6
            (keyboard, "", (Keycode.CONTROL, Keycode.F7,)), # 7
            (keyboard, "", (Keycode.CONTROL, Keycode.F8,)), # 8
        ),
        "slider": (
            (keyboard, "", (Keycode.CONTROL, Keycode.F9,),  (Keycode.CONTROL, Keycode.F10,)), # A
            (keyboard, "", (Keycode.CONTROL, Keycode.F11,), (Keycode.CONTROL, Keycode.F12,)), # B
            (keyboard, "", (Keycode.CONTROL, Keycode.F13,), (Keycode.CONTROL, Keycode.F14,)), # C
            (keyboard, "", (Keycode.CONTROL, Keycode.F15,), (Keycode.CONTROL, Keycode.F16,)), # X
            (keyboard, "", (Keycode.CONTROL, Keycode.F17,), (Keycode.CONTROL, Keycode.F18,)), # Y
        ),
    },
    MODE_MEDIA: {
        "button": (
            (keyboard, "",   (Keycode.CONTROL, Keycode.F1,)),             # 1
            (keyboard, "",   (Keycode.CONTROL, Keycode.F2,)),             # 2
            (keyboard, "",   (Keycode.CONTROL, Keycode.F3,)),             # 3
            (cc,       "🔇", (ConsumerControlCode.MUTE,)),                # 4
            (cc,       "⏏️", (ConsumerControlCode.EJECT,)),               # 5
            (cc,       "⏮️", (ConsumerControlCode.SCAN_PREVIOUS_TRACK,)), # 6
            (cc,       "⏭️", (ConsumerControlCode.SCAN_NEXT_TRACK,)),     # 7
            (cc,       "⏯️", (ConsumerControlCode.PLAY_PAUSE,)),          # 8
        ),
        "slider": (
            (keyboard, "",   (Keycode.CONTROL, Keycode.F9,),              (Keycode.CONTROL, Keycode.F10,)),             # A
            (keyboard, "",   (Keycode.CONTROL, Keycode.F11,),             (Keycode.CONTROL, Keycode.F12,)),             # B
            (cc,       "🔆", (ConsumerControlCode.BRIGHTNESS_DECREMENT,), (ConsumerControlCode.BRIGHTNESS_INCREMENT,)), # C
            (cc,       "⏩", (ConsumerControlCode.REWIND,),               (ConsumerControlCode.FAST_FORWARD,)),         # X
            (cc,       "🔊", (ConsumerControlCode.VOLUME_DECREMENT,),     (ConsumerControlCode.VOLUME_INCREMENT,)),     # Y
        ),
    },
}

hid_mode = DEFAULT_MODE

def do_hid_action(group:str, index:int, option:int = 0, repeats:int = 1) -> bool:
    if not group in hid_actions[hid_mode] or index >= len(hid_actions[hid_mode][group]):
        return False
    
    action = hid_actions[hid_mode][group][index]
    if len(action) < 3 + option:
        return False
    
    device = action[0]
    if not type(device) in (Keyboard, ConsumerControl):
        return False
    
    command = action[2 + option]
    if not type(command) is tuple:
        return False
    
    repeats = int(min(max(repeats, 1), MAX_REPEATS))
    for i in range(repeats):
        device.send(*command)
    return True

# set up the display
displayio.release_displays()
i2c = busio.I2C(scl=i2c_sda_pin, sda=i2c_scl_pin, frequency=1_000_000)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
maingroup = displayio.Group()
display.root_group = maingroup

for s in slider_displays:
    maingroup.append(s)
maingroup.append(pad_displays)
maingroup.append(title_label)

labelgroup = displayio.Group()
maingroup.append(labelgroup)

def update_labels() -> None:
    title_label.text = hid_mode

    # clear out old button labels
    while len(labelgroup):
        label = labelgroup.pop()
        del label
    
    # add button labels
    for i in range(len(pads) - 1):
        if i >= len(hid_actions[hid_mode]["button"]):
            break
        text = hid_actions[hid_mode]["button"][i][1]
        if text:
            label = EmojiLabel(text, scale=1)
            label.anchor_point = (0.5, 0.5)
            label.anchored_position = (PAD_X+(PAD_W*(i+0.5)+1), 52)
            labelgroup.append(label)

    # update rotary slider labels
    for i, slider in enumerate(slider_displays):
        if i >= len(hid_actions[hid_mode]["slider"]):
            break
        slider.emoji(hid_actions[hid_mode]["slider"][i][1])
update_labels()

# used to keep track of which note pads are curerntly pressed
pad_state = [False] * len(pads)
slider_state = [None] * len(sliders)

while True:
    for i, slider in enumerate(sliders):
        pos = slider.pos()
        if pos is not None:   # touched!
            slider_displays[i].pos(pos)   # fixme: need ".pos(pos-0.5)" for fader
            slider_displays[i].touch(True)

            val = int((1-pos) * SLIDER_SEGMENTS)
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
                if i == len(pads) - 1: # *
                    hid_mode = MODES[(MODES.index(hid_mode) + 1) % len(MODES)]
                    update_labels()
                else:
                    do_hid_action("button", i)
            pad_state[i] = v
            print("pad:%d: v:%d" % (i,v))
