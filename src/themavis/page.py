#!/usr/bin/env python

from pysvg.shape import rect
from pysvg.structure import svg, g, clipPath, defs

from container import Container
from utils import mm_to_px, random_string


class Page(object):
    """
    One page that can contain one or more maps.
    """
    def __init__(self, width=297, height=210):
        """
        Initialises a new page in A4 landscape format.
        """
        self.set_size(width, height)
        self.containers = []      # The list of containers
        # Add an empty container in the background.
        # self.containers.append(Container(
        #             x=10, y=10, 
        #             width = (self.width - 20), 
        #             height = (self.height - 20)
        #         ))
    
    def set_size(self, width, height):
        self.width = width
        self.height = height
    
    def write(self, path):
        """
        Writes the page to the SVG file with the provided path.
        """
        # Create a new SVG document
        doc = svg(
            x=0, y=0, 
            width=mm_to_px(self.width), height=mm_to_px(self.height)
        )
        # Draw all the content: first the background, then the content,
        # and finally the labels
        background_group = g()
        background_group.setAttribute('id', 'background')
        content_group = g()
        content_group.setAttribute('id', 'content')
        label_group = g()
        label_group.setAttribute('id', 'labels')
        contour_group = g()
        contour_group.setAttribute('id', 'contours')
        my_defs = defs()
        for c in self.containers:
            if c.has_background: c.draw_background(background_group)
            if c.needs_clipping and (c.has_content or c.has_labels):
                path_id = random_string(16)
                clprect = rect(
                    x=mm_to_px(c.x), y=mm_to_px(c.y),
                    width=mm_to_px(c.width), height=mm_to_px(c.height)
                )
                clppath = clipPath(id=path_id)
                clppath.addElement(clprect)
                my_defs.addElement(clppath)
                # Draw content with clipping path
                if c.has_content:
                    container_grp = g()
                    container_grp.set_clip_path('url(#%s)' % path_id)
                    c.draw_content(container_grp)
                    content_group.addElement(container_grp)
                # The labels on top of the content
                if c.has_labels:
                    container_grp = g()
                    container_grp.set_clip_path('url(#%s)' % path_id)
                    c.draw_labels(container_grp)
                    label_group.addElement(container_grp)
            else:
                if c.has_content: c.draw_content(content_group)
                if c.has_labels: c.draw_labels(label_group)
            if c.has_contour: c.draw_contour(contour_group)
        # Add each of the base groups
        doc.addElement(my_defs)
        doc.addElement(background_group)
        doc.addElement(content_group)
        doc.addElement(label_group)
        doc.addElement(contour_group)
        # Write the SVG document to the file
        doc.save(path)
    
