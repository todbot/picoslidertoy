# picoslidertoy boot.py

import supervisor
import usb_midi

supervisor.set_usb_identification(manufacturer="todbot",
                                  product="picoslidertoy")
# only for CircuitPython 9.1+ 
usb_midi.set_names(streaming_interface_name="picoslidertoy",
                   in_jack_name="midi in", out_jack_name="midi out")

print("set usb and midi ident to 'picoslidertoy'")

# paste this lines into the REPL (without the '#') to put the board into UF2 bootloader mode
# import microcontroller; microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER); microcontroller.reset()
