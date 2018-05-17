import requests
import re
import cv2
from bing_tile import TileSystem
from PIL import Image
import sys, io, os
import json
import pprint

MAXIMGSIZE = 8192*8192

def DownloadImage(imageUrlStr, imageUrlSubdomain, quadKey):
    if len(imageUrlStr) == 5:
        finalUrl = imageUrlStr[0] + imageUrlSubdomain + imageUrlStr[2] + str(quadKey) + imageUrlStr[4]
    elif len(imageUrlStr) == 3:
        finalUrl = imageUrlStr[0] + quadKey + imageUrlStr[2]
    file = requests.get(finalUrl)
    return Image.open(io.BytesIO(file.content))

def CheckValidImage(imageUrlStr,imageUrlSubdomain, image):
    if not os.path.exists('error.png'):
        errorImg = DownloadImage(imageUrlStr, imageUrlSubdomain, '11111111111111111111')
        errorImg.save('./error.png')
    return not (image == Image.open('./error.png'))

if __name__ == '__main__':
    arg = sys.argv[:]
    if len(arg) < 5:
        print("Not enough arguments\n")
    tl_lat = float(arg[1])
    tl_lon = float(arg[2])
    br_lat = float(arg[3])
    br_lon = float(arg[4])
    # TODO: Check if the top left and bottom right coordinates are correct

    # boundBox = [(tl_lat, tl_lon), (br_lat, tl_lon), (tl_lat, br_lon), (br_lat, br_lon)]
    t = TileSystem()
    # detail = 15
    # px, py = t.LatLongToPixelXY(42.05780619999999, -87.67587739999999, detail)
    # tx, ty = t.PixelXYToTileXY(px, py)
    # quadKey = t.TileXYToQuadKey(tx, ty, detail)

    # Get current tile url
    baseUrl = "https://dev.virtualearth.net/REST/v1/Imagery/Metadata/Aerial?key="
    bingKey = "AuL4N1YXVUkjZYd0uY9LKs4z1TluN-6GAZY9VKEj6zVSP_Q402Dm37QWPiG_0b06"
    r = requests.get(baseUrl+bingKey)
    j = r.json()
    #pprint.pprint(j)
    imageUrl = j['resourceSets'][0]['resources'][0]['imageUrl']
    imageUrlSubdomain = j['resourceSets'][0]['resources'][0]['imageUrlSubdomains'][0]
    imageUrlStr = re.split('{|}', imageUrl)
    finalLvl = 23
    # Determine appropriate level to retrieve the image
    for lvl in range(23, 0, -1):
        px1, py1 = t.LatLongToPixelXY(tl_lat, tl_lon, lvl)
        px2, py2 = t.LatLongToPixelXY(br_lat, br_lon, lvl)
        # Check if image exceeds max image size
        if abs(px1-px2)*abs(py1-py2) > MAXIMGSIZE:
            print("Level {} exceeds maximum image size, skipping".format(lvl))
            continue

        tx1, ty1 = t.PixelXYToTileXY(px1, py1)
        tx2, ty2 = t.PixelXYToTileXY(px2, py2)

        # Stitch tile images together
        imageWidth = (tx2 - tx1 + 1) * 256
        imageHeight = (ty2 - ty1 + 1) * 256
        result = Image.new('RGB', (imageWidth, imageHeight))
        imgError = False
        print (tx1, tx2, ty1, ty2)
        for ty in range(ty1, ty2+1):
            for tx in range(tx1, tx2+1):
                print ("Current Tx, Ty", tx, ty)
                quadKey = t.TileXYToQuadKey(tx, ty, lvl)
                image = DownloadImage(imageUrlStr, imageUrlSubdomain, quadKey)
                if (CheckValidImage(imageUrlStr, imageUrlSubdomain, image)):
                    image.save('tile{0}{1}.jpeg'.format(tx,ty))
                    result.paste(image, ((tx-tx1)*256,(ty-ty1)*256))
                else:
                    print("Invalid tile image at level {0}, tile ({1},{2})".format(lvl,tx,ty))
                    imgError = True
                    break
            if imgError:
                break
        if imgError:
            continue

        result.save('raw_result.jpeg')
        # Crop image
        tlpx, brpy = t.TileXYToPixelXY(tx1, ty2)
        left = px1 - tlpx
        top = py2 - brpy
        width = px2 - tlpx
        height = py1 - brpy
        finalImage = result.crop((left, top ,left+width, top + height))

        finalImage.save('cropped_result.jpeg')
        finalLvl = lvl
        break

    res = (2**finalLvl)*256
    print('Final level: {0}, Image Resolution: {1}'.format(finalLvl, res))

    # # Retrieve and save image
    # file = open('Images/test.jpeg', 'wb')
    # imgResp = requests.get(finalUrl, stream=True)
    # imgResp.json()
    # pprint.pprint(imgResp)
    # for block in imgResp.iter_content(1024):
    #     file.write(block)
    # file.close()
    # curImage = cv2.imread('Images/test.jpeg',0)
    # cv2.imshow('Test Image',curImage)
    # cv2.waitKey(0)
