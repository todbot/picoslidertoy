# picoslidertoy


<img src="./docs/picoslidertoy_photo1.jpg" width="400"><img src="./docs/picoslidertoy_photo2.jpg" width="400">
<a href="https://www.tindie.com/products/todbot/picoslidertoy-capsense-controller-for-pico/"><img src="https://d2ss6ovg47m0r5.cloudfront.net/badges/tindie-smalls.png" alt="I sell on Tindie" width="200" height="55"></a>

### What is it?

picoslidertoy is a control surface that uses 25 GPIO pins of the Raspberry Pi Pico to provide:

- three linear sliders
- two rotary sliders
- nine buttons
- all capacitive touch 

It also includes a cutout for a reverse-mounted SSD1306 I2C OLED display. The Raspberry Pi Pico SMD mounts to the back of the board to provide a clean look for the touch surface.  The entire PCB is 165 mm x 76 mm (6.5" x 3.0").

The picoslidertoy can be a USB MIDI control surface, a USB Macropad keyboard with "analog" controls, or even a USB gamepad.  It can be programmed in [CircuitPython](https://circuitpython.org/) and [`touchio`](https://docs.circuitpython.org/en/latest/shared-bindings/touchio/index.html) (my preference) or Arduino with my [`TouchyTouch library`](https://github.com/todbot/TouchyTouch).  Several example firmware apps are provided.

### Versions

There are two versions of the picoslidertoy available:

- black PCB – production version with proper alignment of the cutout for standard 0.91" I2C OLED, comes with all SMD resistors soldered down

- green PCB - prototype version with no components soldered down and where the I2C OLED cutout is a little off. Still usable, or mount the display on the face. 

There is also a nice minimal 3d-printable enclosure available in the github repo (and visible in the photos above).  You really want a case for capacitive touch projects like this to reduce spurious readings. 


### Soldering components

... Coming soon!   Very similar to [soldering the Pico on picotouch](https://github.com/todbot/picotouch?tab=readme-ov-file#how-to-solder-the-pico)


### Installing apps

... More details coming soon! 

In general, I'll try to make UF2 files available in the [Releases section](https://github.com/todbot/picoslidertoy/releases) for the differenet apps.   

To install the apps, hold the Pico's BOOTSEL button down while plugging in the board to your computer. 
This puts the board in bootloader mode.  Then drag the UF2 file to the "RPI-RP2" drive. 

#### CircuitPython apps

- [hwtest](https://github.com/todbot/picoslidertoy/blob/main/circuitpython/hwtest/code.py)
    -- a simple test of the touch sensors, no display needed. Use serial REPL to see results

- [hwtest display](https://github.com/todbot/picoslidertoy/blob/main/circuitpython/hwtest_display/code.py) -- like `hwtest` but also outputs simple feedback via the display
 
- [midi_sliders](https://github.com/todbot/picoslidertoy/blob/main/circuitpython/midi_sliders/) -- MIDI controller where the sliders emit CCs and the buttons send NoteOn/NoteOffs


### Why did you make it?

I wanted a way to experiment with linear and rotary touch sliders.  I made some [touchwheels](https://github.com/todbot/touchwheels) to give away for Hackaday Supercon 2023 and they were popular. I wanted a larger playground for experimenting with these controls. 

### What makes it special?

The 25 capacitive touch sensors are read directly by the Pico, either via CircuitPython's `touchio` library or the `TouchyTouch` Arduino library.  No external touch chip needed.  I think that's really cool!  Getting an "analog" value out of the three touch sensors that make up a linear or rotary touch slider is fairly simple but there are some tricks I'm developing to make the values stable.

picoslidertoy is also completely open source with schematic files in KiCad and software in CircuitPython and Arduino.

<img src="./docs/picoslidertoy_render2.jpg" width="400">
