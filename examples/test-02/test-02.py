#!/usr/bin/env python

try:
    import themavis as tm
except:
    # themavis module is not installed. If this script is executed from inside
    # the examples folder, we can import it manually
    import os, sys
    tm_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../../src')
    sys.path.append(tm_path)
    import themavis as tm

import os
datadir = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../../data')

page = tm.page.Page()
m = tm.container.Map(x=20, y=30, width=297-40, height=210-50, bbox=(-110, -50, 70, 80))
page.containers.append(m)

countries_style = tm.style.DiscreteSurfaceStyle(
    attr = 'MAP_COLOR',
    colors = {
        1: tm.color.Color([0,170,0]),
        2: tm.color.Color([170,0,0]),
        3: tm.color.Color([170,0,127]),
        4: tm.color.Color([170,0,255]),
        5: tm.color.Color([255,0,0]),
        6: tm.color.Color([170,85,0]),
        7: tm.color.Color([170,170,0]),
        8: tm.color.Color([255,85,0]),
        9: tm.color.Color([255,85,255]),
        10: tm.color.Color([85,255,255]),
        11: tm.color.Color([255,255,0]),
        12: tm.color.Color([170,255,255]),
        13: tm.color.Color([170,127,127]),
    },
    default_color = tm.color.Color([255,255,255]),
    style = {'stroke': 'black', 'stroke-width': 0.3}
)
lyr = tm.layer.VectorLayer(
    name='Countries', 
    datasource=datadir + '/naturalearth/ne_110m_admin_0_countries.geojson',
    style=countries_style
)
m.add_layer(lyr)

title = tm.container.Text(
    x=20, y=20, width=297-40, height=80, 
    text="Countries of the world",
    style={
        'font-family': 'Helvetica',
        'font-size': '14pt',
        'font-weight': 'bold'
    }
)
page.containers.append(title)

page.write('ne_countries.svg')
