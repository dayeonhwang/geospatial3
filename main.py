import requests
from bing_tile import TileSystem
from PIL import Image
import sys, io, os, time

if __name__ == '__main__':
    # Request base url
    r = requests.get("http://dev.virtualearth.net/REST/V1/Imagery/Metadata/Road?output=json&include=ImageryProviders&key=AuL4N1YXVUkjZYd0uY9LKs4z1TluN-6GAZY9VKEj6zVSP_Q402Dm37QWPiG_0b06')
    baseUrl = "http://h0.ortho.tiles.virtualearth.net/tiles/h{0}.jpeg?g=131"
    quadKey = "023131022213211200"
    with request.urlopen(baseUrl.format(quadKey)) as file:
        Image.open(file)
