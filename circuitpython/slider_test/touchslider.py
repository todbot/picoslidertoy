## pylint: disable=invalid-name
# SPDX-FileCopyrightText: Copyright (c) 2024 Tod Kurt
# SPDX-License-Identifier: MIT
"""
`touchslider`
================================================================================

Create linear (TouchSlider) and rotary (TouchWheel) capacative touch sliders
 using three `touchio` pins and special pad geometry. 

Originally part of the 'touchwheels' project: https://github.com/todbot/touchwheels/
2023 - @todbot / Tod Kurt

"""

import touchio

class TouchWheel():
    """Simple capacitive touchweel made from three captouch pads """
    def __init__(self, touch_pins, offset = -0.333/2, sector_scale=0.333, wrap_value=True):
        self.touchins = []
        self.offset = offset # physical design is rotated 1/2 a sector anti-clockwise
        self.scale = sector_scale
        self.wrap_value = wrap_value
        for p in touch_pins:
            touchin = touchio.TouchIn(p)
            self.touchins.append(touchin)

    def pos(self):
        """
        Given three touchio.TouchIn pads, compute wheel position 0-1
        or return None if wheel is not pressed
        """
        a = self.touchins[0]
        b = self.touchins[1]
        c = self.touchins[2]

        # compute raw percentages
        a_pct = (a.raw_value - a.threshold) / a.threshold
        b_pct = (b.raw_value - b.threshold) / b.threshold
        c_pct = (c.raw_value - c.threshold) / c.threshold
        #print( "%+1.2f  %+1.2f  %+1.2f" % (a_pct, b_pct, c_pct), end="\t")

        pos = None

        # cases when finger is touching two pads
        if a_pct >= 0 and b_pct >= 0:  #
            pos = self.scale * (0 + (b_pct / (a_pct + b_pct)))
        elif b_pct >= 0 and c_pct >= 0:  #
            pos = self.scale * (1 + (c_pct / (b_pct + c_pct)))
        elif c_pct >= 0 and a_pct >= 0 and self.wrap_value:  #
            pos = self.scale * (2 + (a_pct / (c_pct + a_pct)))

        # special cases when finger is just on a single pad.
        elif a_pct > 0 and b_pct <= 0 and c_pct <= 0:
            pos = 0 * self.scale
        elif a_pct <= 0 and b_pct > 0 and c_pct <= 0:
            pos = 1 * self.scale
        elif a_pct <= 0 and b_pct <= 0 and c_pct > 0 and self.wrap_value:
            pos = 2 * self.scale

        # wrap pos around the 0-1 circle if offset puts it outside that range
        return (pos + self.offset) % 1 if pos is not None else None

class TouchSlider(TouchWheel):
    """A TouchSlider is a linearized TouchWheel """
    def __init__(self, touch_pins, offset=0, sector_scale=0.5, wrap_value=False):
        super().__init__(touch_pins, offset, sector_scale, wrap_value)
