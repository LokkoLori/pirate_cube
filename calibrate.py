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
        d.text((10, 10), self.name, font=arialfont)

class CalibratorCube(PiXXLCube):

    def __init__(self):
        super(CalibratorCube, self).__init__(CalibratorSide)

if __name__ == "__main__":
    cube = CalibratorCube()
    cube.run()