#!/bin/bash

set -x

mkdir tmp

python3 world_bbox.py -o tmp/bbox.shp

python3 build_voronoi.py -o tmp/voronoi.shp

ogr2ogr -clipsrc tmp/bbox.shp tmp/base.shp tmp/voronoi.shp

python3 build_landmass.py -o tmp/landmass.shp


python3 spatial_join.py -f1 tmp/landmass.shp -f2 tmp/base.shp -o tmp/world.shp


# rm tmp/bbox.*
# rm tmp/voronoi.*
