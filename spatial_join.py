# http://rexdouglass.com/fast-spatial-joins-in-python-with-a-spatial-index/
import os
from osgeo import ogr
import argparse

parser = argparse.ArgumentParser(description='Joins to shapefile features')
parser.add_argument('-f1', type=str, help='shapefile to filter with', required=True)
parser.add_argument('-f2', type=str, help='shapefile to select features from', required=True)
parser.add_argument('-o', type=str, help='out file', required=True)
args = parser.parse_args()


def openShapefile(shapefile):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    return driver.Open(shapefile, 0)


ds1 = openShapefile(args.f1)
ds2 = openShapefile(args.f2)

lyr1 = ds1.GetLayer()
lyr2 = ds2.GetLayer()

# matched = []
# for i in range(lyr2.GetFeatureCount()):
#     feat2 = lyr2.GetFeature(i)
#     geom2 = feat2.GetGeometryRef()
#     # for feat1 in lyr1:
#     for j in range(lyr1.GetFeatureCount()):
#         feat1 = lyr1.GetFeature(j)
#         geom1 = feat1.GetGeometryRef()
#         # print(dir(geom1))
#         if geom2.Intersects(geom1):
#             matched.append(geom2)
#         if geom2.Within(geom1):
#             matched.append(geom2)
#         if geom2.Overlaps(geom1):
#             matched.append(geom2)
#         # print(geom1, geom2)
#         # matched.append(feat2)
#
# print(len(matched))
#


wkts = []
for feat1 in lyr1:
    print(len(wkts))
    geom1 = feat1.GetGeometryRef()
    wkt = geom1.ExportToWkt()
    lyr2.SetSpatialFilter( ogr.CreateGeometryFromWkt(wkt) )
    # for i in range(lyr2.GetFeatureCount()):
        # feat2 = lyr2.GetFeature(i)
    for feat2 in lyr2:
        geom2 = feat2.GetGeometryRef()
        wkts.append(geom2.ExportToWkt())




outShapefile = args.o

if not outShapefile:
    raise ValueError("outShapefile cannot be `None`")

# Save extent to a new Shapefile
if ".shp" not in outShapefile:
    outShapefile += ".shp"
outDriver = ogr.GetDriverByName("ESRI Shapefile")

# Remove output shapefile if it already exists
if os.path.exists(outShapefile):
    outDriver.DeleteDataSource(outShapefile)

# Create the output shapefile
outDataSource = outDriver.CreateDataSource(outShapefile)
# TODO
#  - get geometry type from data
outLayer = outDataSource.CreateLayer("world", geom_type=ogr.wkbPolygon)

# Add fields
geoidField = ogr.FieldDefn("geoid", ogr.OFTInteger)
outLayer.CreateField(geoidField)

# Create the feature and set values
featureDefn = outLayer.GetLayerDefn()

i = 0
for wkt in wkts:
    # wkt = geometry.wkt
    feature = ogr.Feature(featureDefn)
    geom = ogr.CreateGeometryFromWkt(wkt)
    feature.SetGeometry(geom)
    feature.SetField("geoid", i)
    outLayer.CreateFeature(feature)
    i+=1
