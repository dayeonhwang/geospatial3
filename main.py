import requests
import re
import cv2
from bing_tile import TileSystem
from PIL import Image
import sys, io, os
import json
import pprint

if __name__ == '__main__':
    # arg = sys.argv[:]
	# if len(arg) < 5:
	# 	print('Not enough arguments!\n')
	# 	print('python main.py <top_lat> <top_long> <bot_lat> <bot_long>')
	# 	exit(0)
	# tl_lat = float(arg[1])
	# tl_lon = float(arg[2])
	# br_lat = float(arg[3])
	# br_lon = float(arg[4])
    # TODO: Check if the top left and bottom right coordinates are correct

    # boundBox = [(tl_lat, tl_lon), (br_lat, tl_lon), (tl_lat, br_lon), (br_lat, br_lon)]
    t = TileSystem()
    detail = 15
    px, py = t.LatLongToPixelXY(42.05780619999999, -87.67587739999999, detail)
    tx, ty = t.PixelXYToTileXY(px, py)
    quadKey = t.TileXYToQuadKey(tx, ty, detail)

    baseUrl = "https://dev.virtualearth.net/REST/v1/Imagery/Metadata/Aerial?key="
    bingKey = "AuL4N1YXVUkjZYd0uY9LKs4z1TluN-6GAZY9VKEj6zVSP_Q402Dm37QWPiG_0b06"
    r = requests.get(baseUrl+bingKey)
    j = r.json()
    #pprint.pprint(j)
    imageUrl = j['resourceSets'][0]['resources'][0]['imageUrl']
    imageUrlSubdomain = j['resourceSets'][0]['resources'][0]['imageUrlSubdomains'][0]
    imageUrlStr = re.split('{|}', imageUrl)
    if len(imageUrlStr) == 5:
        finalUrl = imageUrlStr[0] + imageUrlSubdomain + imageUrlStr[2] + str(quadKey) + imageUrlStr[4]
    elif len(imageUrlStr) == 3:
        finalUrl = imageUrlStr[0] + quadKey + imageUrlStr[2]

    file = open('Images/test.jpeg', 'wb')
    imgResp = requests.get(finalUrl, stream=True)
    pprint.pprint(imgResp)
    for block in imgResp.iter_content(1024):
        file.write(block)
    file.close()
    curImage = cv2.imread('Images/test.jpeg',0)
    cv2.imshow('Test Image',curImage)
    cv2.waitKey(0)
