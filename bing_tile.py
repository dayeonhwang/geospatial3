# <copyright company="Microsoft">
# Copyright (c) 2006-2009 Microsoft Corporation.  All rights reserved.
# </copyright>


import numpy as np

class TileSystem:
    EarthRadius = 6378137.
    MinLatitude = -85.05112878
    MaxLatitude = 85.05112878
    MinLongitude = -180
    MaxLongitude = 180


    ## <summary>
    ## Clips a number to the specified minimum and maximum values.
    ## </summary>
    ## <param name="n">The number to clip.</param>
    ## <param name="minValue">Minimum allowable value.</param>
    ## <param name="maxValue">Maximum allowable value.</param>
    ## <returns>The clipped value.</returns>
    def Clip(self, n, minValue, maxValue):
        return min(max(n, minValue), maxValue)

    ## <summary>
    ## Determines the map width and height (in pixels) at a specified level
    ## of detail.
    ## </summary>
    ## <param name="levelOfDetail">Level of detail, from 1 (lowest detail)
    ## to 23 (highest detail).</param>
    ## <returns>The map width and height in pixels.</returns>
    def MapSize(self, levelOfDetail):
        return 256 << levelOfDetail

    ## <summary>
    ## Determines the ground resolution (in meters per pixel) at a specified
    ## latitude and level of detail.
    ## </summary>
    ## <param name="latitude">Latitude (in degrees) at which to measure the
    ## ground resolution.</param>
    ## <param name="levelOfDetail">Level of detail, from 1 (lowest detail)
    ## to 23 (highest detail).</param>
    ## <returns>The ground resolution, in meters per pixel.</returns>
    def GroundResolution(latitude, levelOfDetail):
        latitude = self.Clip(latitude, self.MinLatitude, self.MaxLatitude)
        return np.cos(latitude * np.pi / 180.) * 2 * np.pi * self.EarthRadius / self.MapSize(levelOfDetail)

    ## <summary>
    ## Determines the map scale at a specified latitude, level of detail,
    ## and screen resolution.
    ## </summary>
    ## <param name="latitude">Latitude (in degrees) at which to measure the
    ## map scale.</param>
    ## <param name="levelOfDetail">Level of detail, from 1 (lowest detail)
    ## to 23 (highest detail).</param>
    ## <param name="screenDpi">Resolution of the screen, in dots per inch.</param>
    ## <returns>The map scale, expressed as the denominator N of the ratio 1 : N.</returns>
    def MapScale(self, latitude, levelOfDetail, screenDpi):
        return GroundResolution(latitude, levelOfDetail) * screenDpi / 0.0254



    ## <summary>
    ## Converts a point from latitude/longitude WGS-84 coordinates (in degrees)
    ## into pixel XY coordinates at a specified level of detail.
    ## </summary>
    ## <param name="latitude">Latitude of the point, in degrees.</param>
    ## <param name="longitude">Longitude of the point, in degrees.</param>
    ## <param name="levelOfDetail">Level of detail, from 1 (lowest detail)
    ## to 23 (highest detail).</param>
    ## <param name="pixelX">Output parameter receiving the X coordinate in pixels.</param>
    ## <param name="pixelY">Output parameter receiving the Y coordinate in pixels.</param>
    def LatLongToPixelXY(self, latitude, longitude,levelOfDetail):
        latitude = self.Clip(latitude, self.MinLatitude, self.MaxLatitude)
        longitude = self.Clip(longitude, self.MinLongitude, self.MaxLongitude)

        x = (longitude + 180) / 360
        sinLatitude = np.Sin(latitude * np.pi / 180)
        y = 0.5 - np.Log((1 + sinLatitude) / (1 - sinLatitude)) / (4 * np.pi)

        mapSize = self.MapSize(levelOfDetail)
        pixelX = self.Clip(x * mapSize + 0.5, 0, mapSize - 1)
        pixelY = self.Clip(y * mapSize + 0.5, 0, mapSize - 1)

        return int(pixelX), int(pixelY)



    ## <summary>
    ## Converts a pixel from pixel XY coordinates at a specified level of detail
    ## into latitude/longitude WGS-84 coordinates (in degrees).
    ## </summary>
    ## <param name="pixelX">X coordinate of the point, in pixels.</param>
    ## <param name="pixelY">Y coordinates of the point, in pixels.</param>
    ## <param name="levelOfDetail">Level of detail, from 1 (lowest detail)
    ## to 23 (highest detail).</param>
    ## <param name="latitude">Output parameter receiving the latitude in degrees.</param>
    ## <param name="longitude">Output parameter receiving the longitude in degrees.</param>
    def PixelXYToLatLong(self, pixelX, pixelY, levelOfDetail):
        mapSize = self.MapSize(levelOfDetail)
        x = (self.Clip(pixelX, 0, mapSize - 1) / mapSize) - 0.5
        y = 0.5 - (self.Clip(pixelY, 0, mapSize - 1) / mapSize)

        latitude = 90. - 360. * np.arctan(np.exp(-y * 2 * np.pi)) / np.pi
        longitude = 360. * x

        return latitude, longitude




    ## <summary>
    ## Converts pixel XY coordinates into tile XY coordinates of the tile containing
    ## the specified pixel.
    ## </summary>
    ## <param name="pixelX">Pixel X coordinate.</param>
    ## <param name="pixelY">Pixel Y coordinate.</param>
    ## <param name="tileX">Output parameter receiving the tile X coordinate.</param>
    ## <param name="tileY">Output parameter receiving the tile Y coordinate.</param>
    def PixelXYToTileXY(self, pixelX, pixelY):
        tileX = pixelX / 256
        tileY = pixelY / 256

        return int(tileX), int(tileY)



    ## <summary>
    ## Converts tile XY coordinates into pixel XY coordinates of the upper-left pixel
    ## of the specified tile.
    ## </summary>
    ## <param name="tileX">Tile X coordinate.</param>
    ## <param name="tileY">Tile Y coordinate.</param>
    ## <param name="pixelX">Output parameter receiving the pixel X coordinate.</param>
    ## <param name="pixelY">Output parameter receiving the pixel Y coordinate.</param>
    def TileXYToPixelXY(self, tileX, tileY):
        pixelX = tileX * 256
        pixelY = tileY * 256

        return int(pixelX), int(pixelY)



    ## <summary>
    ## Converts tile XY coordinates into a QuadKey at a specified level of detail.
    ## </summary>
    ## <param name="tileX">Tile X coordinate.</param>
    ## <param name="tileY">Tile Y coordinate.</param>
    ## <param name="levelOfDetail">Level of detail, from 1 (lowest detail)
    ## to 23 (highest detail).</param>
    ## <returns>A string containing the QuadKey.</returns>
    def TileXYToQuadKey(self, tileX, tileY, levelOfDetail):
        quadKey = ''
        for i in range(levelOfDetail, 0, -1):
            digit = 0
            mask = 1 << (i - 1)
            if ((tileX & mask) != 0):
                digit += 1
            if ((tileY & mask) != 0):
                digit += 1
                digit += 1
            quadKey += str(digit)
        return quadKey

    ## <summary>
    ## Converts a QuadKey into tile XY coordinates.
    ## </summary>
    ## <param name="quadKey">QuadKey of the tile.</param>
    ## <param name="tileX">Output parameter receiving the tile X coordinate.</param>
    ## <param name="tileY">Output parameter receiving the tile Y coordinate.</param>
    ## <param name="levelOfDetail">Output parameter receiving the level of detail.</param>
    def QuadKeyToTileXY(self, quadKey):
        tileX = tileY = 0
        levelOfDetail = len(quadKey)
        for i in range(levelOfDetail, 0, -1):
            mask = 1 << (i - 1)
            qk = quadKey[levelOfDetail - i]
            if qk == '0':
                pass
            elif qk == '1':
                tileX |= mask
            elif qk == '2':
                tileY |= mask
            elif qk == '3':
                tileX |= mask
                tileY |= mask
            else:
                raise Exception('Invalid QuadKey digit sequence.')
        return tileX, tileY
