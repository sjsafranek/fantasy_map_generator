#!/bin/bash

set -x

mkdir tmp

python3 bbox_generator.py

python3 voronoi_generator.py

ogr2ogr -clipsrc tmp/bbox.shp tmp/mesh.shp tmp/voronoi.shp

python3 perlin_noise.py
