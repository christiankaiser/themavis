#!/usr/bin/env python

from pysvg.builders import StyleBuilder
from pysvg.shape import rect, line
from pysvg.text import text
from copy import deepcopy

from color import Color
from stats import quantile
from utils import mm_to_px

import numpy as np
import re


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
    
    def finalize_statistics(self):
        pass
    
    def legend(self, elem, x, y, width, height, label_style):
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




class QuantileSurfaceStyle(SimpleSurfaceStyle):
    """
    Chooses a discrete color for a feature based on the quantiles.
    For n colors, we need to have n-1 quantile limits.
    """
    def __init__(self, attr, colors, quantiles, default_color=Color((220,220,220)), style=None):
        # Store the attributes
        self.attr = attr
        self.colors = colors
        self.quantiles = np.array(quantiles)
        self.quantiles.sort()
        self.mark_style = {'fill': 'none', 'stroke-width': 0.25, 'stroke': 'black'}
        self.mark_length = 1
        self.ndecimals = 4
        # Provide a default style if none is specified
        if style == None:
            style = {
                'fill-opacity': 0.7,
                'stroke': 'black',
                'stroke-width': 0.3,
            }
        style['fill'] = default_color.hex
        self.default_style = StyleBuilder(deepcopy(style))
        self.styles = []
        for c in self.colors.colors:
            style['fill'] = c.hex
            self.styles.append(StyleBuilder(deepcopy(style)))
    
    def style_feature(self, feature, elem):
        """
        Styles the provided feature.
        """
        v = feature['properties'][self.attr]
        if v == None:
            elem.set_style(self.default_style.getStyle())
            return
        for i in range(len(self.limits)):
            l = self.limits[i]
            if v < l:
                elem.set_style(self.styles[i].getStyle())
                return
        elem.set_style(self.styles[i+1].getStyle())
    
    def needs_statistics(self):
        return True
    
    def init_statistics(self):
        self.values = []
    
    def update_statistics(self, feat):
        if feat['properties'][self.attr] != None:
            self.values.append(feat['properties'][self.attr])
    
    def finalize_statistics(self):
        self.values = np.array(self.values, dtype=np.float32)
        self.limits = [np.percentile(self.values, q*100) for q in self.quantiles]
        self.limits.sort()
    
    def legend(self, elem, x, y, width, height, label_style):
        n = len(self.colors.colors)
        box_height = int(np.floor(float(height) / (n+2)))
        box_width = min(8, width/2)
        mark_style = StyleBuilder(self.mark_style)
        textsize = int(re.findall('([0-9]+)',
            label_style.get('font-size', "8")
        )[0])
        label_x = x + box_width + self.mark_length + 1
        for i in range(n):
            box = rect(
                x = mm_to_px(x), 
                y = mm_to_px(y + (n-i-1)*box_height),
                width = mm_to_px(box_width),
                height = mm_to_px(box_height)
            )
            s = deepcopy(self.styles[i].style_dict)
            s['stroke'] = 'black'
            box.set_style(StyleBuilder(s).getStyle())
            elem.addElement(box)
            
            if i < (n-1):
                mark = line(
                    X1=mm_to_px(x+box_width), 
                    Y1=mm_to_px(y+(n-i-1)*box_height),
                    X2=mm_to_px(x+box_width+self.mark_length),
                    Y2=mm_to_px(y+(n-i-1)*box_height)
                )
                mark.set_style(mark_style.getStyle())
                elem.addElement(mark)
                label = text(
                    content="%0.*f" % (self.ndecimals, self.limits[i]), 
                    x=mm_to_px(label_x), y=mm_to_px(y+(n-i-1)*box_height)+(textsize/2)
                )
                label.set_style(StyleBuilder(label_style).getStyle())
                elem.addElement(label)
         
        label = text(
            content="Min: %0.*f" % (self.ndecimals, np.min(self.values)), 
            x=mm_to_px(label_x), y=mm_to_px(y+n*box_height)+(textsize/2)
        )
        label.set_style(StyleBuilder(label_style).getStyle())
        elem.addElement(label)
        
        label = text(
            content="Max: %0.*f" % (self.ndecimals, np.max(self.values)), 
            x=mm_to_px(label_x), y=mm_to_px(y+0*box_height)+(textsize/2)
        )
        label.set_style(StyleBuilder(label_style).getStyle())
        elem.addElement(label)
        











