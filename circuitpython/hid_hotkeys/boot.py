# picoslidertoy boot.py

import supervisor
import usb_hid

supervisor.set_usb_identification(manufacturer="todbot",
                                  product="picoslidertoy")

usb_hid.enable((
    usb_hid.Device.KEYBOARD,
))

print("set usb and hid ident to 'picoslidertoy'")

# paste this lines into the REPL (without the '#') to put the board into UF2 bootloader mode
# import microcontroller; microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER); microcontroller.reset()
