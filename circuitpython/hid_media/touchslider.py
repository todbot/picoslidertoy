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
    #def __init__(self, touch_pins, offset = -0.333 * (3/4), sector_scale=0.333, wrap_value=True):
    def __init__(self, touch_pins, offset = 0, sector_scale=0.333, wrap_value=True):
        # note: sector_scale & offset determined from len(touch_pins)?
        self.touchins = [touchio.TouchIn(p) for p in touch_pins]
        self.offset = offset  # physical design is rotated anti-clockwise
        self.scale = sector_scale
        self.wrap_value = wrap_value
        self.last_pos = 0
        self.pos_filt = 0.1

    def pos(self):
        """
        Given three touchio.TouchIn pads, compute wheel position 0-1
        or return None if wheel is not pressed
        """
        a = self.touchins[0]
        b = self.touchins[1]
        c = self.touchins[2]

        # compute raw percentages of how much each pad is touched
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
        elif c_pct >= 0 and a_pct >= 0 and self.wrap_value:  # i.e. is wheel
            pos = self.scale * (2 + (a_pct / (c_pct + a_pct)))

        # special cases when finger is just on a single pad.
        elif a_pct > 0 and b_pct <= 0 and c_pct <= 0:
            pos = 0 * self.scale
        elif a_pct <= 0 and b_pct > 0 and c_pct <= 0:
            pos = 1 * self.scale
        elif a_pct <= 0 and b_pct <= 0 and c_pct > 0 and self.wrap_value:
            pos = 2 * self.scale

        if pos is not None:  # i.e. if touched
            # filter noise
            if abs(pos - self.last_pos) > 0.5:
                print("bonk", pos, self.last_pos)
                self.last_pos = pos
            #pos = self.pos_filt * pos + (1-self.pos_filt) * self.last_pos
            self.last_pos = pos
            # wrap pos around the 0-1 circle if offset puts it outside that range
            pos = (pos + self.offset) % 1
        return pos
    
class TouchSlider(TouchWheel):
    """A TouchSlider is a linearized TouchWheel """
    def __init__(self, touch_pins, offset=0, sector_scale=0.5, wrap_value=False):
        super().__init__(touch_pins, offset, sector_scale, wrap_value)
