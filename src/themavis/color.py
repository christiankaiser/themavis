#!/usr/bin/env python

from json import load
from os import sep
from os.path import dirname, abspath, exists


class Color(object):
    """
    A RGB color.
    """
    def __init__(self, rgb=(255,255,255)):
        self.r, self.g, self.b = rgb
    
    def __repr__(self):
        return "{red: %i, green: %i, blue: %i}" % (self.r, self.g, self.b)
    
    @property
    def hex(self):
        return '#%02x%02x%02x' % (self.r, self.g, self.b)




class ColorMap(object):
    """
    A color map is a set of colors that go together.
    """
    cmap_id = None
    cmap_name = None
    cmap_type = None        # Type: qualitative [qual], sequential [seq], 
                            # divergent [div]
    crit_val = None         # Critical value for divergent color maps
    colors = []             # Array of colors

    def __init__(self, cmap_id=None, colors=None):
        if cmap_id is None and colors is None: return
        if cmap_id is not None and colors is None: 
            self.load(cmap_id)
            return
        self.set_rgb(colors)
        self.cmap_id = cmap_id
    
    def set_rgb(colors):
        self.colors = []
        for c in colors: 
            self.colors.append(Color(c))
    
    def load(cmap_id):
        cm_dir = dirname(abspath(__file__)) + sep + 'colormaps'
        cm_path = cm_dir + sep + cmap_id
        if not exists(cm_path):
            raise Exception("Color map '%s' not found" % name)
            return
        f = open(cm_path)
        cm_json = load(f)
        self.cmap_id = cmap_id
        self.cmap_name = cm_json['name']
        self.cmap_type = cm_json['type']
        self.crit_val = cm_json['crit_val']
        self.set_rgb(cm_json['colors'])
    


