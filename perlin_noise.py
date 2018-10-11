'''
Fantasy Map Generator
---------------------

## Fantasy Map Generators
http://mewo2.com/notes/terrain/
https://github.com/Azgaar/Fantasy-Map-Generator

## Voronoi
http://www-cs-students.stanford.edu/~amitp/game-programming/polygon-map-generation/

## Perlin Noise
https://medium.com/@yvanscher/playing-with-perlin-noise-generating-realistic-archipelagos-b59f004d8401


https://github.com/amitp/mapgen2/blob/master/Map.as

'''


import noise
import random
import numpy as np
from osgeo import ogr


shapefile = 'tmp/mesh.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
datasource = driver.Open(shapefile, 1)  # 0 means read-only. 1 means writeable.


# Check to see if shapefile is found.
if datasource is None:
    print('Could not open {0}'.format(shapefile))
    exit()

layer = datasource.GetLayer()


# Add Fields
classField = ogr.FieldDefn("class", ogr.OFTString)
layer.CreateField(classField)

perlinField = ogr.FieldDefn("perlin", ogr.OFTReal)
layer.CreateField(perlinField)

scaleField = ogr.FieldDefn("scale", ogr.OFTReal)
layer.CreateField(scaleField)

# slopeField = ogr.FieldDefn("slope", ogr.OFTReal)
# layer.CreateField(slopeField)

# elevationField = ogr.FieldDefn("elevation", ogr.OFTReal)
# layer.CreateField(elevationField)
#.end


# defaults
# scale: number that determines at what distance to view the noisemap.
scale = 100.0
# octaves: the number of levels of detail you want you perlin noise to have.
octaves = 6
# persistence: number that determines how much each octave contributes to the overall shape (adjusts amplitude).
persistence = 0.5
# lacunarity: number that determines how much detail is added or removed at each octave (adjusts frequency).
lacunarity = 2.0
# base = 0
base = random.randint(0,1000)



print("generating perlin noise")
shape = ( (180+180)*10, (85+85)*10 )
world = np.zeros(shape)
for i in range(shape[0]):
    for j in range(shape[1]):
        world[i][j] = noise.pnoise2(i/scale,
                                    j/scale,
                                    octaves=octaves,
                                    persistence=persistence,
                                    lacunarity=lacunarity,
                                    repeatx=shape[0],
                                    repeaty=shape[1],
                                    base=base)


print("annotating voronoi polygons")
count = layer.GetFeatureCount()
for i in range(count):
    feature = layer.GetFeature(i)
    geom = feature.GetGeometryRef()
    point = geom.Centroid()
    lon = point.GetX()
    x = int(lon+180*10)
    lat = point.GetY()
    y = int(lat+85*10)
    perlin = world[x][y]
    feature.SetField("perlin", perlin)
    # set land type classification
    if perlin < -0.025:
        feature.SetField("class", "deep_water")
    elif perlin < 0.05:
        feature.SetField("class", "shallow_water")
    elif perlin < 0.055:
        feature.SetField("class", "sandy")
    elif perlin < 0.07:
        feature.SetField("class", "beach")
    elif perlin < 0.1:
        feature.SetField("class", "plains")
    elif perlin < 0.2:
        feature.SetField("class", "forest")
    elif perlin < 0.285:
        feature.SetField("class", "mountain")
    else:
        feature.SetField("class", "snow")
    #.end
    layer.SetFeature(feature)

'''
lightblue = [0,191,255]
blue = [65,105,225]
green = [34,139,34]
darkgreen = [0,100,0]
sandy = [210,180,140]
beach = [238, 214, 175]
snow = [255, 250, 250]
mountain = [139, 137, 137]
'''


feature.Destroy()
feature = None

datasource.Destroy()
layer = None


#     layer.SetFeature(feature)
#
#
# print("classifying voronoi polygons")
# for i in range(count):
#     feature = layer.GetFeature(i)
#     perlin = feature.GetField("perlin")
#     scale = (perlin-pmin)/(pmax-pmin)
#     feature.SetField("scale", scale)
#     feature.SetField("elevation", (scale * perlin))





'''

# find max distance
sw = ogr.Geometry(ogr.wkbPoint)
sw.AddPoint(-180.0, -85.0)
ne = ogr.Geometry(ogr.wkbPoint)
ne.AddPoint(180.0, 85.0)
max_distance = sw.Distance(ne)


def formLandMass(source=None):
    # random landmass if none supplied
    island = None
    if not source:
        num = random.randint(0, count)
        island = layer.GetFeature(num)
    else:
        island = source

    # get source elevation
    source_elevation = random.uniform(0.1, 1.0)
    if island.GetField("elevation"):
        source_elevation = (island.GetField("elevation") + source_elevation) / 2
    island.SetField("elevation", source_elevation)
    layer.SetFeature(island)
    geomI = island.GetGeometryRef()

    # generate radius of influence
    radius = random.uniform(
            max_distance*(source_elevation/24),
            max_distance*(source_elevation/12)
        )

    # loop through features
    for i in range(count):
        feature = layer.GetFeature(i)
        geomF = feature.GetGeometryRef()
        dist = geomI.Distance(geomF)
        if dist < radius:
            elev = feature.GetField("elevation")
            target_elevation = 0
            if not elev or elev > 0.1:
                perc = (dist + -0.2)/(radius + -0.2)
                target_elevation = source_elevation / (1+perc)
                # randomize
                perlin = feature.GetField("perlin")
                scale  = feature.GetField("scale")
                target_elevation = target_elevation + (scale * perlin)
                #.end
            else:
                target_elevation = (source_elevation + elev)/2
                if 0 != random.randint(0,3):
                    target_elevation += random.uniform(-0.1, 0.05)
            if 1 < target_elevation:
                target_elevation = 1.0
            elif 0 > target_elevation:
                target_elevation = 0.0
            feature.SetField("elevation", target_elevation)
            layer.SetFeature(feature)
            # spawn new
            if 0  == random.randint(0, 30) and not source:
                formLandMass(feature)


for i in range(30):
    print("Seed: {0}".format(i))
    formLandMass()





# TODO
#  - store elevations in cache
#  - write features at once
# arr = [0.0 for i in range(0, count)]


'''
