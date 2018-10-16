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
import gdal, ogr, os, osr


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
# shape = ( (180+180)*10, (85+85)*10 )
shape = ( (180+180)*10, (180+180)*10 )
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




print("Circular Gradient")
center_x, center_y = shape[0] // 2, shape[1] // 2
circle_grad = np.zeros_like(world)

for x in range(world.shape[0]):
    for y in range(world.shape[1]):
        distx = abs(x - center_x)
        disty = abs(y - center_y)
        dist = math.sqrt(distx*distx + disty*disty)
        circle_grad[x][y] = dist

# get it between -1 and 0
max_grad = np.max(circle_grad)
circle_grad = circle_grad / max_grad
circle_grad = -circle_grad


print("Circular Gradient + Noise")
world_noise = np.zeros_like(world)
for x in range(shape[0]):
    for y in range(shape[1]):
        world_noise[x][y] = (world[x][y] + circle_grad[x][y]) * 100




# Open file
tifffile = 'tmp/world.tif'
driver = gdal.GetDriverByName('GTiff')

origin = (-180.0,-85.0)
pxWidth = 0.04
pxHeight = 0.04

outRaster = driver.Create(tifffile, shape[0], shape[1], 1, gdal.GDT_Byte)

outRaster.SetGeoTransform((
    origin[0],
    pxWidth,
    0,
    origin[1],
    0,
    pxHeight
))

outband = outRaster.GetRasterBand(1)
outband.WriteArray(world_noise)

outRasterSRS = osr.SpatialReference()
outRasterSRS.ImportFromEPSG(4326)
outRaster.SetProjection(outRasterSRS.ExportToWkt())
outband.FlushCache()
