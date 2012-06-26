#!/usr/bin/env python

from pysvg.builders import StyleBuilder
from copy import deepcopy

from color import Color
from stats import quantile



class SimpleSurfaceStyle(object):
    """
    A simple style for polygons.
    """
    def __init__(self, style=None):
        # Provide a default style if none is specified
        if style == None:
            style = {
                'fill': '#cccccc',
                'fill-opacity': 0.7,
                'stroke': 'black',
                'stroke-width': 0.3
            }
        self.style = StyleBuilder(style)
    
    def style_feature(self, feature, elem):
        """
        Styles the provided feature.
        """
        elem.set_style(self.style.getStyle())
    
    def needs_statistics(self):
        return False
    
    def init_statistics(self):
        pass
    
    def update_statistics(self, feat):
        pass
    




class DiscreteSurfaceStyle(SimpleSurfaceStyle):
    """
    Chooses a discrete color for a feature based on the value of an
    attribute. For each value there is a unique color.
    """
    def __init__(self, attr, colors={}, default_color=Color((220,220,220)), style=None):
        self.attr = attr
        # Provide a default style if none is specified
        if style == None:
            style = {
                'fill-opacity': 0.7,
                'stroke': 'black',
                'stroke-width': 0.3,
            }
        style['fill'] = default_color.hex
        self.default_style = StyleBuilder(deepcopy(style))
        self.styles = {}
        for val in colors:
            style['fill'] = colors[val].hex
            self.styles[val] = StyleBuilder(deepcopy(style))
        
        
    def style_feature(self, feature, elem):
        """
        Styles the provided feature.
        """
        v = feature['properties'][self.attr]
        try: 
            v = int(v)
        except: 
            v = str(v)
        elem.set_style(self.styles.get(v, self.default_style).getStyle())



