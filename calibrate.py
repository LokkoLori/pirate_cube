from cubecore import PiXXLSide, PiXXLCube
from PIL import ImageDraw, ImageFont
import os

if os.path.dirname(__file__):
    os.chdir(os.path.dirname(__file__))

arialfont = ImageFont.truetype("arial.ttf", 18)

class CalibratorSide(PiXXLSide):

    def draw(self):
        d = ImageDraw.Draw(self.image)
        d.rectangle((0, 0, self.res, self.res), fill=(0, 0, 0), outline=(0, 0, 255))
        d.text((10, 10), self.name, font=arialfont)

class CalibratorCube(PiXXLCube):

    def __init__(self):
        super(CalibratorCube, self).__init__(CalibratorSide)



if __name__ == "__main__":
