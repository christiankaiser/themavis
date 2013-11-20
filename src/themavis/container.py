#!/usr/bin/env python

from pysvg.builders import ShapeBuilder, StyleBuilder
from pysvg.structure import g
from pysvg.shape import rect, path
from pysvg.text import text

import numpy as np
import re
from math import floor

from utils import mm_to_px
from layer import Layer


class Container(object):
    """
    A container is an empty box. Subclasses can specify the content by overriding
    the draw_*() methods.
    """
    def __init__(self, x, y, width, height):
        self.needs_clipping = False
        self.has_background = False
        self.has_content = False
        self.has_labels = False
        self.has_contour = False
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.sb = ShapeBuilder()
        # Create a default background style
        self.bg_style = StyleBuilder({
            'fill': 'none', 'stroke-width': 0, 'stroke': 'none'
        })
        # Create a default contour style
        self.contour_style = StyleBuilder({
            'fill': 'none', 'stroke-width': 0, 'stroke': 'none'
        })
    
    def draw_background(self, elem):
        """
        Draws the background of the container.
        elem is a SVG element, and we should add our content to this element.
        The method doesn't return anything.
        """
        bg_rect = rect(
            x = mm_to_px(self.x), 
            y = mm_to_px(self.y),
            width = mm_to_px(self.width),
            height = mm_to_px(self.height)
        )
        bg_rect.set_style(self.bg_style.getStyle())
        elem.addElement(bg_rect)
    
    def draw_content(self, elem):
        """
        Draws the content of the container.
        elem is a SVG element, and we should add our content to this element.
        The method doesn't return anything.
        """
        pass
    
    def draw_labels(self, elem):
        """
        Draws the labels of the container.
        elem is a SVG element, and we should add our content to this element.
        The method doesn't return anything.
        """
        pass
    
    def draw_contour(self, elem):
        """
        Draws a contour around the container.
        """
        contour_rect = rect(
            x = mm_to_px(self.x), 
            y = mm_to_px(self.y),
            width = mm_to_px(self.width),
            height = mm_to_px(self.height)
        )
        contour_rect.set_style(self.contour_style.getStyle())
        elem.addElement(contour_rect)




class Map(Container):
    """
    A map container with layers.
    """
    def __init__(self, x, y, width, height, bbox):
        Container.__init__(self, x, y, width, height)
        self.needs_clipping = True
        self.has_content = True
        self.has_contour = True
        self.bg_style.setStroke('none')     # No border for our map
        self.layers = []    # The list of layers
        self.bbox = np.array(bbox, dtype=np.float64)

    def adjusted_bbox(self):
        """
        Returns a bbox corresponding to the dimensions of the view frame.
        """
        bbox_width = abs(self.bbox[2] - self.bbox[0])
        bbox_height = abs(self.bbox[3] - self.bbox[1])
        if (bbox_width / bbox_height) > (self.width / self.height):
            # We should adjust according to the width and increase the height
            reduction_factor = bbox_width / self.width
            adj_bbox_height = self.height * reduction_factor
            return [
                self.bbox[0], 
                self.bbox[1] - ((adj_bbox_height - bbox_height) / 2),
                self.bbox[2], 
                self.bbox[3] + ((adj_bbox_height - bbox_height) / 2)
            ]
        else:
            # We adjust according to the height and increase the width
            reduction_factor = bbox_height / self.height
            adj_bbox_width = self.width * reduction_factor
            return [
                self.bbox[0] - ((adj_bbox_width - bbox_width) / 2), 
                self.bbox[1],
                self.bbox[2] + ((adj_bbox_width - bbox_width) / 2), 
                self.bbox[3]
            ]

    def add_layer(self, layer):
        self.layers.append(layer)

    def draw_content(self, elem):
        for lyr in self.layers:
            lyr.draw_content(elem, self)

    def draw_labels(self, elem):
        for lyr in self.layers:
            lyr.draw_labels(elem, self)

    def geo_to_local_coords(self, coords):
        """
        Converts a list of geographic coordinates into local coordinates.
        Each coordinate is specified as tuple (x, y)
        """
        # If we have a tuple, we assume it is a single coordinate.
        # Convert it to a list.
        if type(coords) == tuple:
            coords = [coords]
        bb = self.adjusted_bbox()
        out_coords = []
        for c in coords:
            x = ((c[0] - bb[0]) / (bb[2] - bb[0]) * self.width) + self.x
            y = ((c[1] - bb[1]) / (bb[3] - bb[1]) * self.height) + self.y
            # y coordinate needs to be swaped (small is top)
            y = self.y + self.height - (y - self.y)
            out_coords.append((x,y))
        return out_coords

    def local_to_geo_coords(self, coords):
        return coords



class Text(Container):
    def __init__(self, x, y, width, height, text, style=None):
        Container.__init__(self, x, y, width, height)
        self.has_content = True
        self.text = text
        if style != None:
            self.style = StyleBuilder(style)
    
    def draw_content(self, elem):
        textsize = int(re.findall('([0-9]+)',
            self.style.style_dict.get('font-size', "12")
        )[0])
        txt = self.text.split('\n')
        for i in range(len(txt)):
            y = mm_to_px(self.y) + textsize + i*1.8*textsize
            t = text(
                content=txt[i], 
                x=mm_to_px(self.x), y=y
            )
            t.set_style(self.style.getStyle())
            elem.addElement(t)



class ScaleBar(Container):
    def __init__(self, x, y, width, height, map_container, unit, step=1, factor=1, style=None):
        Container.__init__(self, x, y, width, height)
        self.has_content = True
        self.map_container = map_container
        self.unit = unit
        self.step = step
        self.factor = factor
        self.style = StyleBuilder({'font-family': 'Helvetica', 'font-size': '8pt', 'font-weight': 'normal'})
        if style != None:
            self.style = StyleBuilder(style)
        self.style.style_dict['text-anchor'] = 'middle'
        self.style.style_dict['text-align'] = 'center'
    
    def draw_content(self, elem):
        # Create a new group
        grp = g()
        grp.setAttribute('id', 'scalebar')
        # Find the amount of available width
        bbox = self.map_container.bbox
        step_length = (float(self.step) * self.factor)
        c = [[bbox[0], 0], [bbox[0] + step_length, 0]]
        px = self.map_container.geo_to_local_coords(c)
        step_px = abs(px[1][0] - px[0][0])
        nsteps = int(floor(float(self.width) / step_px))
        # Draw the horizontal line
        l = path(pathData="M %f %f L %f %f" % (
            mm_to_px(self.x), mm_to_px(self.y + self.height),
            mm_to_px(self.x + nsteps*step_px), mm_to_px(self.y + self.height)
        ), style=StyleBuilder({'stroke': 'black', 'stroke-width': 0.3}).getStyle())
        grp.addElement(l)
        # Draw the vertical lines and write the text
        # textsize = int(re.findall('([0-9]+)',
        #             self.style.style_dict.get('font-size', "12")
        #         )[0])
        for i in range(nsteps+1):
            l = path(pathData="M %f %f L %f %f" % (
                mm_to_px(self.x + i*step_px), mm_to_px(self.y + self.height),
                mm_to_px(self.x + i*step_px), mm_to_px(self.y + self.height - 3)
            ), style=StyleBuilder({'stroke': 'black', 'stroke-width': 0.3}).getStyle())
            grp.addElement(l)
            content = str(i*self.step)
            if i == nsteps: content += ' ' + self.unit
            t = text(
                content=content, 
                x=mm_to_px(self.x + i*step_px), y=mm_to_px(self.y + self.height - 5)
            )
            t.set_style(self.style.getStyle())
            grp.addElement(t)
        elem.addElement(grp)



class Legend(Container):
    
    def __init__(self, x, y, width, height, style, title=None, name=None, units=None):
        Container.__init__(self, x, y, width, height)
        self.has_content = True
        self.style = style
        self.container_style = {'fill': 'none', 'stroke-width': 0, 'stroke': 'none'}
        self.title = title
        self.name = name
        self.units = units
        self.border = 3
        self.title_style = {'font-family': 'Helvetica', 'font-size': '11pt', 'font-weight': 'bold'}
        self.name_style = {
            'font-family': 'Helvetica',
            'font-size': '8pt',
            'font-weight': 'bold'
        }
        self.label_style = {
            'font-family': 'Helvetica',
            'font-size': '8pt',
            'font-weight': 'normal'
        }
    
    def draw_content(self, elem):
        contour = rect(
            x = mm_to_px(self.x), 
            y = mm_to_px(self.y),
            width = mm_to_px(self.width),
            height = mm_to_px(self.height)
        )
        contour.set_style(StyleBuilder(self.container_style).getStyle())
        elem.addElement(contour)
        x = self.x + self.border
        y = self.y + self.border
        width = self.width - (2*self.border)
        height = self.height - (2*self.border)
        if self.title is not None:
            textsize = int(re.findall('([0-9]+)',
                self.title_style.get('font-size', "11")
            )[0])
            t = text(
                content=self.title, 
                x=mm_to_px(x), y=mm_to_px(y) + textsize
            )
            t.set_style(StyleBuilder(self.title_style).getStyle())
            elem.addElement(t)
            y += int(round(textsize))
        if self.name is not None:
            textsize = int(re.findall('([0-9]+)',
                self.name_style.get('font-size', "11")
            )[0])
            t = text(
                content=self.name, 
                x=mm_to_px(x), y=mm_to_px(y) + textsize
            )
            t.set_style(StyleBuilder(self.name_style).getStyle())
            elem.addElement(t)
            y += int(round(textsize))
        self.style.legend(elem, x, y, width, height, self.label_style)


