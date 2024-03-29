#
# picoslidertoy_midi_sliders_code.py -- turn picoslidertoy into MIDI controller
# 2024 - @todbot / Tod Kurt - github.com/todbot/picoslidertoy
#
# based off of "picotouch_test.py":
# picotouch_test.py -- Testing for tiny capsense controller using Pico,
# 2021 - @todbot / Tod Kurt - github.com/todbot/picotouch
#
# To use:
#
# 1. Install needed libraries:
#   circup install adafruit_displayio_ssd1306 adafruit_midi
# 2. Copy over files in this directory to CIRCUITPY:
#   cp circuitpython/midi_sliders/* /Volumes/CIRCUITPY/
#

import time
import board
import touchio
import busio
import displayio
import adafruit_displayio_ssd1306
import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

from touchslider import TouchWheel, TouchSlider
from slider_display import FaderDisplay, WheelDisplay, PadsDisplay

# midi cc and note definitions
midi_ccs = [ 73, 1, 72, 74, 71 ]
midi_notes = [ 34, 35, 36, 37,  38, 39, 40, 41,  24 ]  # FIXME
midi_chan = 1

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

# set up midi out
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=midi_chan-1)

# set up the display
dw,dh = 128, 64
displayio.release_displays()
i2c = busio.I2C(scl=i2c_sda_pin, sda=i2c_scl_pin, frequency=1_000_000)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=dw, height=dh)
maingroup = displayio.Group()
display.root_group = maingroup

for s in slider_displays:
    maingroup.append(s)
maingroup.append(pad_displays)

# used to keep track of which note pads are curerntly pressed
pad_state = [False] * len(pads)

while True:
    for i, slider in enumerate(sliders):
        pos = slider.pos()
        if pos is not None:   # touched!
            slider_displays[i].pos(pos)   # fixme: need ".pos(pos-0.5)" for fader
            slider_displays[i].touch(True)
            cc_val = int((1-pos) * 127)
            midi.send(ControlChange(midi_ccs[i], cc_val))
            print("slider:%d: %1.2f cc:%d ccval:%d" % (i,pos,midi_ccs[i],cc_val))
        else:
            slider_displays[i].touch(False)
            
    for i, pad in enumerate(pads):
        v = pad.value
        pad_displays.set(i, v)
        if pad_state[i] != v:
            n = midi_notes[i]
            msg = NoteOn(n, 127) if v else NoteOff(n,0)
            midi.send(msg)
            pad_state[i] = v
            print("pad:%d: note:" % i, msg)

    #time.sleep(0.01)

