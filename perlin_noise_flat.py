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


import math
import noise
import random
import numpy as np
from osgeo import ogr


# Open file
print("Opening shapefile")
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


print("Perlin Noise")
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



print("Colorized Circular Gradient + Noise")
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




feature.Destroy()
feature = None

datasource.Destroy()
layer = None
