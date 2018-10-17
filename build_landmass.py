'''
https://jakevdp.github.io/PythonDataScienceHandbook/05.11-k-means.html
https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Delaunay.html

'''


# import json
# import math
import random
# import hashlib
import statistics
import os
from osgeo import ogr
# import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Delaunay
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
import shapely.ops
from sklearn.datasets.samples_generator import make_blobs
import scipy.interpolate
# from sklearn.datasets import make_gaussian_quantiles


import argparse

parser = argparse.ArgumentParser(description='Creates voronoi shapefile from random points')
parser.add_argument('-o', type=str, help='out file', required=True)
args = parser.parse_args()

outfile = args.o
if ".shp" != outfile[-4:]:
    outfile += '.shp'



# def distance(pt1, pt2):
#     x1 = pt1[0]
#     y1 = pt1[1]
#     x2 = pt2[0]
#     y2 = pt2[1]
#     return math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )


# def perimeter(shape):
#     dist = 0
#     for i in range(len(shape)):
#         if 0 == i:
#             continue
#         pt1 = shape[i-1]
#         pt2 = shape[i]
#         dist += distance(pt1, pt2)
#     dist += distance(pt2, shape[0])
#     return dist

# def getPointCluster(samples, std, center):


def getRandomPointCluster(cluster_std):
    if not cluster_std:
        cluster_std = random.uniform(0.0, 30.0)
    points, y_true = make_blobs(
        n_samples=random.randint(100, 150),
        centers=1,
        # cluster_std=random.uniform(0.0, 30.0),
        cluster_std=cluster_std,
        center_box=(-80, 80)
    )
    return points


def buildTINFromPoints(points):
    mesh = []
    triangles = Delaunay(points)
    for triangle in triangles.simplices:
        geom = []
        for idx in triangle:
            point = points[idx]
            geom.append((point[0], point[1]))
        polygon = Polygon(geom)
        mesh.append(polygon)
    return mesh


def exportToShapefile(features, outShapefile):
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
    outLayer = outDataSource.CreateLayer("mesh", geom_type=ogr.wkbPolygon)

    # Add fields
    geoidField = ogr.FieldDefn("geoid", ogr.OFTInteger)
    outLayer.CreateField(geoidField)

    # Create the feature and set values
    featureDefn = outLayer.GetLayerDefn()

    i = 0
    for geometry in features:
        wkt = geometry.wkt
        feature = ogr.Feature(featureDefn)
        geom = ogr.CreateGeometryFromWkt(wkt)
        feature.SetGeometry(geom)
        feature.SetField("geoid", i)
        outLayer.CreateFeature(feature)
        i+=1



# def curveGeometries(geometries):
#     polygons = []
#     for geometry in geometries:
#         newGeometry = []
#         line = geometry.exterior
#         coords = np.array([list(point) for point in line.coords[1:]])
#         f = scipy.interpolate.interp1d(coords[:,0], coords[:,1], kind='quadratic')
#         # f = scipy.interpolate.interp1d(coords[:,0], coords[:,1], kind='cubic')
#         new_x = np.linspace( np.min(coords[:,0]), np.max(coords[:,0]), 10)
#         new_y = f(new_x)
#         for i in range(len(new_x)):
#             newGeometry.append((new_x[i], new_y[i]))
#         newGeometry.append(newGeometry[0])
#         polygons.append(Polygon(newGeometry))
#     return polygons


# def curveGeometries(geometries):
#     polygons = []
#     for geometry in geometries:
#         newGeometry = []
#         line = geometry.exterior
#         last = line.coords[0]
#         prev = line.coords[1]
#         for point in line.coords[2:]:
#             coords = np.array([
#                 list(last),
#                 list(prev),
#                 list(point)
#             ])
#             f = scipy.interpolate.interp1d(coords[:,0], coords[:,1], kind='quadratic')
#             # f = scipy.interpolate.interp1d(coords[:,0], coords[:,1], kind='cubic')
#             new_x = np.linspace( np.min(coords[:,0]), np.max(coords[:,0]), 10)
#             new_y = f(new_x)
#             for i in range(len(new_x)):
#                 newGeometry.append((new_x[i], new_y[i]))
#             last = prev
#             prev = point
#         newGeometry.append(newGeometry[0])
#         polygons.append(Polygon(newGeometry))
#     return polygons


def blurGeometries(geometries):
    polygons = []
    for geometry in geometries:
        newGeometry = []
        line = geometry.exterior
        coords = np.array([list(point) for point in line.coords])
        f = scipy.interpolate.interp1d(coords[:,0], coords[:,1])
        new_x = np.linspace( np.min(coords[:,0]), np.max(coords[:,0]), 10)
        new_y = f(new_x)
        for i in range(len(new_x)):
            newGeometry.append((new_x[i], new_y[i]))
        newGeometry.append(newGeometry[0])
        polygons.append(Polygon(newGeometry))
    return polygons




def getIslandCluster():
    return getRandomPointCluster( random.uniform(0.0, 1.5) )


def getContinentCluster():
    return getRandomPointCluster( random.uniform(8, 25) )


master = None


# islands
for i in range(25):
    # points    = getRandomPointCluster()
    points = getIslandCluster()
    polygons  = buildTINFromPoints(points)
    distances = [polygon.length for polygon in polygons]

    min_d     = min(distances)
    max_d     = max(distances)
    mean_d    = statistics.mean(distances)
    stdev_d   = statistics.stdev(distances)

    collection = []
    for polygon in polygons:
        if polygon.length < (mean_d + stdev_d):
            collection.append(polygon)

    # exportToShapefile(collection, "test.shp")
    # exit()

    # dissolve geometries
    if not master:
        master = collection[0]
    for polygon in collection:
        master = master.union(polygon)


# continents
for i in range(4):
    # points    = getRandomPointCluster()
    points = getContinentCluster()
    polygons  = buildTINFromPoints(points)
    distances = [polygon.length for polygon in polygons]

    min_d     = min(distances)
    max_d     = max(distances)
    mean_d    = statistics.mean(distances)
    stdev_d   = statistics.stdev(distances)

    collection = []
    for polygon in polygons:
        if polygon.length < (mean_d + stdev_d):
            collection.append(polygon)

    # exportToShapefile(collection, "test.shp")
    # exit()

    # dissolve geometries
    if not master:
        master = collection[0]
    for polygon in collection:
        master = master.union(polygon)



# write to file
if "MultiPolygon" == master.geom_type:
    exportToShapefile([geom for geom in master.geoms], outfile)
else:
    exportToShapefile([master], outfile)
