import os
from osgeo import ogr
import argparse

parser = argparse.ArgumentParser(description='Creates shapefile for earth bounding box')
parser.add_argument('-o', type=str, help='out file', required=True)
args = parser.parse_args()

outfile = args.o
if ".shp" != outfile[-4:]:
    outfile += '.shp'

# Save extent to a new Shapefile
# outShapefile = "tmp/bbox.shp"
outShapefile = outfile
outDriver = ogr.GetDriverByName("ESRI Shapefile")

# Remove output shapefile if it already exists
if os.path.exists(outShapefile):
    outDriver.DeleteDataSource(outShapefile)

# Create the output shapefile
outDataSource = outDriver.CreateDataSource(outShapefile)
outLayer = outDataSource.CreateLayer("bbox", geom_type=ogr.wkbPolygon)
featureDefn = outLayer.GetLayerDefn()

feature = ogr.Feature(featureDefn)

ring = ogr.Geometry(ogr.wkbLinearRing)
ring.AddPoint(-180,  85)
ring.AddPoint( 180,  85)
ring.AddPoint( 180, -85)
ring.AddPoint(-180, -85)
ring.AddPoint(-180,  85)
poly = ogr.Geometry(ogr.wkbPolygon)
poly.AddGeometry(ring)

feature.SetGeometry(poly)
outLayer.CreateFeature(feature)

feature = None

# Save and close DataSource
outDataSource = None
