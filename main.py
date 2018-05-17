import requests
import re
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
        exit(0)
    lat1 = float(arg[1])
    lon1 = float(arg[2])
    lat2 = float(arg[3])
    lon2 = float(arg[4])
    # Check if the top left and bottom right coordinates are correct
    if lat1 == lat2 or lon1 == lon2:
        print('Error: cannot accept equal latitude or longitude')
        exit(0)
    tl_lat = max(lat1,lat2)
    tl_lon = min(lon1,lon2)
    br_lat = min(lat1,lat2)
    br_lon = max(lon1,lon2)
    t = TileSystem()

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
        for ty in range(ty1, ty2+1):
            for tx in range(tx1, tx2+1):
                # print ("Current Tx, Ty", tx, ty)
                quadKey = t.TileXYToQuadKey(tx, ty, lvl)
<<<<<<< HEAD
                img = DownloadImage(imageUrlStr, imageUrlSubdomain, quadKey)
                if (CheckValidImage(imageUrlStr, imageUrlSubdomain, img)):
                    img.save('tile{0}{1}.jpeg'.format(tx,ty))
                    result.paste(img, ((tx-tx1)*256,(ty-ty1)*256))
=======
                image = DownloadImage(imageUrlStr, imageUrlSubdomain, quadKey)
                if (CheckValidImage(imageUrlStr, imageUrlSubdomain, image)):
                    # image.save('tile{0}{1}.jpeg'.format(tx,ty))
                    result.paste(image, ((tx-tx1)*256,(ty-ty1)*256))
>>>>>>> 2ccd8bd241afc30a56f0111442af1bdf68e6fdd8
                else:
                    print("Invalid tile image at level {0}, tile ({1},{2})".format(lvl,tx,ty))
                    imgError = True
                    break
            if imgError:
                break
        if imgError:
            continue

        if abs(px1 - px2) < 1 or abs(py1 - py2) < 1:
            print("Cannot find an image for your bounding box")

        result.save('raw_result.jpeg')
        # Crop image
<<<<<<< HEAD
        tlpx, brpy = t.TileXYToPixelXY(tx1, ty1)
        print ('tlpx:',tlpx, 'brpy:',brpy)
        print ('px1, px2, py1, py2',px1, px2, py1, py2)
        left = px1 - tlpx
        top = py1 - brpy
        width = px2-px1
        height = py2-py1
        print (left, top, width, height)
        finalImage = result.crop((left, top, width+left,top+height))
=======
        tlpx, tlpy = t.TileXYToPixelXY(tx1, ty1)
        left = px1 - tlpx
        top = py1 - tlpy
        width = px2 - px1
        height = py2 - py1
        finalImage = result.crop((left, top ,left+width, top+height))

>>>>>>> 2ccd8bd241afc30a56f0111442af1bdf68e6fdd8
        finalImage.save('cropped_result.jpeg')
        finalLvl = lvl
        break

    res = (2**finalLvl)*256
    print('Final level: {0}, Image Resolution: {1}'.format(finalLvl, res))
