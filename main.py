from urllib import request
import Image
import sys, io, os

if __name__ == '__main__':
    baseUrl = "http://h0.ortho.tiles.virtualearth.net/tiles/h{0}.jpeg?g=131"
    quadKey = "023131022213211200"
    with request.urlopen(baseUrl.format(quadkey)) as file:
        Image.open(file)
