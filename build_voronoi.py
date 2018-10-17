import os
import random
from osgeo import ogr
import numpy as np
from scipy.spatial import Voronoi
import shapely.geometry
import shapely.ops
import argparse


parser = argparse.ArgumentParser(description='Creates voronoi shapefile from random points')
parser.add_argument('-o', type=str, help='out file', required=True)
args = parser.parse_args()

outfile = args.o
if ".shp" != outfile[-4:]:
    outfile += '.shp'


def newLongitude():
    return random.uniform(-180, 180)

def newLatitude():
    return random.uniform(-85, 85)

# Save extent to a new Shapefile
# outShapefile = "tmp/voronoi.shp"
outShapefile = outfile
outDriver = ogr.GetDriverByName("ESRI Shapefile")

# Remove output shapefile if it already exists
if os.path.exists(outShapefile):
    outDriver.DeleteDataSource(outShapefile)

# Create the output shapefile
outDataSource = outDriver.CreateDataSource(outShapefile)
outLayer = outDataSource.CreateLayer("points", geom_type=ogr.wkbPolygon)

# Add fields
idField = ogr.FieldDefn("id", ogr.OFTInteger)
outLayer.CreateField(idField)

# Create the feature and set values
featureDefn = outLayer.GetLayerDefn()


points = np.random.random((100000, 2))
for i in range(len(points)):
    points[i][0] = (points[i][0] * (180 + 180)) - 180
    points[i][1] = (points[i][1] * (85  + 85))  - 85

vor = Voronoi(points)

lines = [
    shapely.geometry.LineString(vor.vertices[line])
    for line in vor.ridge_vertices
    if -1 not in line
]

i = 0
for poly in shapely.ops.polygonize(lines):
    wkt = poly.wkt
    feature = ogr.Feature(featureDefn)
    poly = ogr.CreateGeometryFromWkt(wkt)
    feature.SetGeometry(poly)
    feature.SetField("id", i)
    outLayer.CreateFeature(feature)
    i+=1

feature = None

# Save and close DataSource
outDataSource = None
