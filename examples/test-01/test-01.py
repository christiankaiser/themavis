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

lyr = tm.layer.VectorLayer(
    name='Countries', 
    datasource=datadir + '/naturalearth/ne_110m_admin_0_countries.geojson'
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
