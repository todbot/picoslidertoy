## pylint: disable=invalid-name
# SPDX-FileCopyrightText: Copyright (c) 2024 Tod Kurt
# SPDX-License-Identifier: MIT
"""
`slider_display`
================================================================================

Create virtual displays for linear TouchSliders and rotary TouchWheels

Part of picoslidertoy
2024 - @todbot / Tod Kurt - github.com/todbot/picoslidertoy

Originally part of the 'touchwheels' project: https://github.com/todbot/touchwheels/
2023 - @todbot / Tod Kurt

"""

import math
import displayio
import vectorio

class FaderDisplay(displayio.Group):
    """Display a simple virtual fader with virtual 'knob' indicating position """
    def __init__(self, x,y, w,h, knob_w=10):
        super().__init__(x=x,y=y,scale=1)
        self.w, self.h, self.knob_w = w,h, knob_w
        pW = displayio.Palette(1)
        pB = displayio.Palette(1)
        pW[0], pB[0] = 0xffffff, 0x000000
        self.append(vectorio.Rectangle(pixel_shader=pW, width=1, height=h, x=w//2, y=0))
        self.knob = displayio.Group()
        knob_handle = vectorio.Rectangle(pixel_shader=pW, width=knob_w, height=knob_w, x=0, y=0)
        knob_touch =  vectorio.Rectangle(pixel_shader=pB, width=knob_w-2, height=knob_w-2, x=1, y=1)
        self.knob.append(knob_handle)
        self.knob.append(knob_touch)
        self.knob.y = h//2
        self.append(self.knob)
    def pos(self,v):
        """Set position of virtual fader"""
        self.knob.y = int(v * (self.h-self.knob_w/2))
    def touch(self,v):
        """Set to indicate if fader is being curerently touched"""
        self.knob[1].hidden = v


class WheelDisplay(displayio.Group):
    """Simple round display with 'knob' indicating wheel position"""
    def __init__(self, x,y, r, knob_w=8, phase_offset=0):
        super().__init__(x=x,y=y,scale=1)
        self.r = r
        self.phase_offset = phase_offset
        self.knob_w = knob_w
        pW = displayio.Palette(1)
        pB = displayio.Palette(1)
        pW[0], pB[0] = 0xffffff, 0x000000
        # the outer circle, with black covering up most to make a line
        self.append(vectorio.Circle(pixel_shader=pW, radius=r, x=0, y=0))
        self.append(vectorio.Circle(pixel_shader=pB, radius=r-1, x=0, y=0))
        self.knob = displayio.Group()
        knob_handle = vectorio.Circle(pixel_shader=pW, radius=knob_w//2, x=0, y=0)
        knob_touch = vectorio.Circle(pixel_shader=pB, radius=knob_w//2-1, x=0, y=0)
        self.knob.append(knob_handle)
        self.knob.append(knob_touch)
        self.append(self.knob)
        self.pos(0)
        
    def pos(self,v):
        v += 0.25 + self.phase_offset  # drawing is offset by 1/4 turn
        self.knob.x = int((self.r-self.knob_w/2) * math.sin(v*6.28))
        self.knob.y = int((self.r-self.knob_w/2) * math.cos(v*6.28))
        
    def touch(self,v):
        self.knob[1].hidden = v

class PadsDisplay(displayio.Group):
    """Simple list of on/off boxes representing touch pads"""
    def __init__(self, x,y, n, pad_h=8, pad_w=8):
        super().__init__(x=x,y=y,scale=1)
        self.n = n
        pW = displayio.Palette(1)
        pB = displayio.Palette(1)
        pW[0], pB[0] = 0xffffff, 0x000000
        self.append(vectorio.Rectangle(pixel_shader=pW, width=(pad_w)*n+2, height=pad_h, x=0, y=0))
        for i in range(n):
            self.append(vectorio.Rectangle(pixel_shader=pB, width=pad_w-2, height=pad_h-2, x=2+i*pad_w, y=1))
                
    def set(self,i,v):
        self[i+1].hidden = v
