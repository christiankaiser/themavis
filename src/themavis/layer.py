#!/usr/bin/env python


import json
import shapely

from style import SimpleSurfaceStyle
from utils import mm_to_px, parse

from pysvg.structure import g
import pysvg.structure
import pysvg.shape



class Layer(object):
    """
    A layer as in a GIS, typically a geometry layer, or a raster layer.
    """
    def __init__(self, name):
        self.name = name
    
    def draw_content(self, elem, map):
        pass
    
    def draw_labels(self, elem, map):
        pass




class VectorLayer(Layer):
    """
    VectorLayer represents any GeoJSON vector dataset.
    """
    def __init__(self, name, datasource, style=None):
        Layer.__init__(self, name)
        self.datasource = datasource
        # Open the GeoJson datasource
        f = open(self.datasource)
        try:
            fc = json.load(f)
        except:
            raise Exception('Error. Unable to read datasource. Make sure the file encoding is UTF-8.')
        f.close()
        if fc is None:
            print "Error. Unable to open datasource %s" % self.datasource
            return
        self.features = fc['features']
        self.style = style or SimpleSurfaceStyle()
    
    def join(self, layer_attr, data_table, data_attr, prefix=''):
        """
        Joins a data table to this feature collection.
        """
        # Build first a dictionary for the layer attribute
        idx = {}
        for feat in self.features:
            idx[parse(feat['properties'][layer_attr])] = feat
        # Now go through the data table and retrieve all data one by one
        for d in data_table:
            feat = idx.get(parse(d[data_attr]), None)
            if feat is None: continue
            for k in d:
                feat['properties'][prefix+k] = parse(d[k])
    
    def draw_content(self, elem, map_container):
        # Check if the style needs to update some statistics
        if self.style.needs_statistics():
            self.style.init_statistics()
            for feat in self.features:
                self.style.update_statistics(feat)
            self.style.finalize_statistics()
        # Read all features
        for feat in self.features:
            geom_elem = self.geometry_for_feature(feat, map_container)
            if geom_elem is not None: elem.addElement(geom_elem)
    
    def geometry_for_feature(self, feat, map_container):
        """
        Returns an SVG geometry element for the provided feature.
        """
        # Get the geometry from the feature
        geom = feat['geometry']
        if geom is None: return None
        if (geom['type'] == 'MultiPolygon' or geom['type'] == 'Polygon'):
            # Convert the polygon to a SVG element
            geom_elem = self.polygon_to_elem(geom, map_container)
            if geom_elem == None: 
                print "Warning. One geometry could not be converted to SVG."
                return None
            # Style the polygon
            self.style.style_feature(feat, geom_elem)
            return geom_elem
        # If the geometry type is not handled, return None
        return None
    
    def polygon_to_elem(self, geom, map_container, path=None):
        # Create a new path if none is provided
        if path is None:
            p = pysvg.shape.path()
        else:
            p = path
        if geom['type'] == 'MultiPolygon':
            for i in range(len(geom['coordinates'])):
                p2 = self.polygon_to_elem({
                    'type':'Polygon', 
                    'coordinates': geom['coordinates'][i]
                }, map_container, p)
        else:
            ring = geom['coordinates'][0]
            if ring is None: return None
            npts = len(ring)
            x, y = map_container.geo_to_local_coords((ring[0][0], ring[0][1]))[0]
            p.appendMoveToPath(mm_to_px(x), mm_to_px(y), relative=False)
            for i in range(1, npts):
                x, y = map_container.geo_to_local_coords((ring[i][0], ring[i][1]))[0]
                p.appendLineToPath(mm_to_px(x), mm_to_px(y), relative=False)
            p.appendCloseCurve()
        return p
        


class DataTable(object):
    """
    A data table created from a CSV file
    """
    def __init__(self, path, sep="\t", header=True):
        f = open(path)
        self.header = None
        if header:
            self.header = f.readline().strip().split(sep)
        self.data = []
        for l in f:
            self.data.append(l.strip().split(sep))
        
    def __iter__(self):
        for data in self.data:
            d = {}
            for fld, val in zip(self.header, data):
                d[fld] = val
            yield d




        