from pixxlcube.cubecore import PiXXLSide, PiXXLCube
from PIL import ImageDraw, ImageFont
import os

if os.path.dirname(__file__):
    os.chdir(os.path.dirname(__file__))

arialfont = ImageFont.truetype("arial.ttf", 18)

class CalibratorSide(PiXXLSide):

    def __init__(self, cube, data):
        super(CalibratorSide, self).__init__(cube, data)

    def draw(self):
        d = ImageDraw.Draw(self.image)
        d.rectangle((0, 0, self.res-1, self.res-1), fill=(0, 0, 0), outline=(0, 0, 255))

        #show name of the side
        d.text((5, 6), self.name, font=arialfont)

        #show 2D axies on the side
        r = 3
        #left bottom (origo)
        d.ellipse((0 - r, self.res - 1 - r, 0 + r, self.res - 1 + r), fill=(255, 0, 0))
        #right bottom (x axis)
        d.ellipse((self.res - 1 - r, self.res - 1  - r, self.res - 1 + r, self.res - 1 + r), fill=(0, 255, 0))
        #top left (y axis)
        d.ellipse((0 - r, 0 - r, 0 + r, 0 + r), fill=(0, 0, 255))


        #draw graviti attack point, blue on top red on bottom
        gx, gy, gz = self.getAlignedGravity()

        try:
            x = gx/gz
        except Exception as e:
            x = 0

        try:
            y = gy/gz
        except Exception as e:
            y = 0

        fill = (0, 0, 255)
        if 0 < gz:
            fill = (255, 0, 0)

        rp2 = self.res*0.5
        px, py = self.coordsRTD(x*rp2 + rp2, y*rp2 + rp2)

        d.ellipse((px-2, py-2, px+2, py+2), fill=fill, outline=(0, 0, 0))


class CalibratorCube(PiXXLCube):

    def __init__(self):
        super(CalibratorCube, self).__init__(CalibratorSide)

if __name__ == "__main__":
    cube = CalibratorCube()
    cube.run()