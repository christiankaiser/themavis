##!/usr/bin/env python
"""
Some functions useful all over the module.
"""

from random import choice


def parse(val):
    """
    Tries to convert the value to a integer or a float if possible.
    If this is not possible, convert it to a string.
    """
    try: 
        v = int(val)
        return v
    except: 
        pass
    try: 
        v = float(val)
        return v
    except: 
        pass
    try: 
        v = str(val)
        return v
    except:
        pass
    return v


def random_string(length=10):
    s = ''
    while len(s) < length:
        s += choice('abcdefghijklmnopqrstuvwxyz')
    return s


def mm_to_px(mm, dpi=72):
    """
    Converts millimeters to pixels.
    Resolution can be adapted using the dpi argument.
    """
    return mm / 25.4 * dpi


def px_to_mm(px, dpi=72):
    """
    Converts pixels to millimeters.
    Resolution can be adapted using the dpi argument.
    """
    return px / dpi * 25.4


def mm_to_px_int(mm, dpi=72):
    """
    Converts millimeters to pixels and round to an integer value.
    """
    return int(round(mm_to_px(mm, dpi)))


def px_to_mm_int(px, dpi=72):
    """
    Converts pixels to millimeters and round to an integer value.
    """
    return int(round(px_to_mm(px, dpi)))

