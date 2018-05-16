import requests
from PIL import Image
import sys, io, os
import json
import pprint

if __name__ == '__main__':
    baseUrl = "https://dev.virtualearth.net/REST/v1/Imagery/Metadata/Aerial?key="
    bingKey = "AuL4N1YXVUkjZYd0uY9LKs4z1TluN-6GAZY9VKEj6zVSP_Q402Dm37QWPiG_0b06"
    r = requests.get(baseUrl+bingKey)
    j = r.json()
    #pprint.pprint(j)
    imageUrl = j['resourceSets'][0]['resources'][0]['imageUrl']
    print (imageUrl)
