import os
from osgeo import ogr

# Save extent to a new Shapefile
outShapefile = "tmp/bbox.shp"
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
