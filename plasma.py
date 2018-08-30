import math
import colorsys


from samplebase import SampleBase
import time
import sys
from PIL import Image
from PIL import ImageDraw
from PIL.Image import FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM, ROTATE_90, ROTATE_180, ROTATE_270
from accelero import get_accelvector
import math
import os
import numpy
import random



facematrix = {
    "Up" : {
        "my": ["Fr",0,1, 0,28,-1, 1,-4,-1], #ok
        "py": ["Ba",1,1, 0,0,1, 1,-32,1], #ok ?
        "mx": ["Le",0,0, 1,0,1, 0,-4,-1], #ok ?
        "px": ["Ri",1,0, 1,28,-1, 0,-32,1] #ok ?
    },
    "Fr" : {
        "my": ["Up",0,1, 0,28,-1, 1,-4,-1], #ok
        "py": ["Do",1,1, 0,28,-1, 1,60,-1], #ok
        "px": ["Le",1,0, 0,-32,1, 1,0,1], #ok
        "mx": ["Ri",0,0, 0,32,1, 1,0,1] #ok
    },
    "Le" : {
        "my": ["Up",0,1, 1,-4,-1, 0,0,1], #ok
        "py": ["Do",1,1, 1,-32,1, 0,28,-1],#ok
        "mx": ["Fr",0,0, 0,32,1, 1,0,1], #ok
        "px": ["Ba",1,0, 0,-32,1, 1,0,1] #ok
    },
    "Ri": {
        "my": ["Up",0,1, 1,32,1, 0,28,-1], #ok
        "py": ["Do",1,1, 1,60,-1, 0,0,1], #ok
        "mx": ["Ba",0,0, 0,32,1, 1,0,1], #ok
        "px": ["Fr",1,0, 0,-32,1, 1,0,1] #ok
    },
    "Ba": {
        "my": ["Up",0,1, 0,0,1, 1,32,1], #ok
        "py": ["Do",1,1, 0,0,1, 1,-32,1],#ok
        "mx": ["Le",0,0, 0,32,1, 1,0,1], #ok
        "px": ["Ri",1,0, 0,-32,1, 1,0,1] #ok
    },
    "Do": {
        "my": ["Ba",0,1, 0,0,1, 1,32,1], #ok
        "py": ["Fr",1,1, 0,28,-1, 1,60,-1], #ok
        "mx": ["Le",0,0, 1,28,-1, 0,32,1], #ok
        "px": ["Ri",1,0, 1,0,1, 0,60,-1] #ok
    }
}


class PulseAnim():

    def __init__(self, step):
        self.phase = 0
        self.step = step

    def nextpahse(self):
        self.phase += self.step

class Square():

    def __init__(self, data, owner):
        self.image = Image.new("RGB", (32, 32))
        self.imagearr = self.image.load()
        self.d = ImageDraw.Draw(self.image)

        self.name = data[0]
        self.coordtrs =  data[1:]
        self.owner = owner
        self.time = 0
        self.renderstart = False
        self.rendering = False
        self.pa = PulseAnim(0.05)
        self.ic = 0
        self.nc = 0

    def draw(self, vect):

        # if self.name not in ["Up", "Ba", "Ri"]:
        #     return

        for i in xrange(32):
            if (i + self.ic) % 2 != 0:
                continue
            for n in xrange(32):
                if (n + self.nc) % 2 != 0:
                    continue
                ian = [i, n]
                crs = []
                for c in self.coordtrs:
                    crs.append(ian[c[0]]*c[1]+c[2])
                x, y, z = crs

                x += vect[0]
                y += vect[1]
                z += vect[2]
                p = self.pa.phase

                hue = math.sin(x * 0.3) + math.cos(y * 0.5) + math.sin(z * 0.25) + math.cos((x+y+z) * 0.16) + 0.5*math.sin(p)
                hue = hue / 3.0
                if hue < -1:
                    hue = -1
                elif 1 < hue:
                    hue = 1

                hue = (hue + 1) / 2.0
                hsv = colorsys.hsv_to_rgb(hue, 1, 1 - hue)

                pix = tuple([int(round(c * 255.0)) for c in hsv])

                self.imagearr[ian[0], ian[1]] = pix

                # r = random.randint(0,15)
                # if r & 1:
                #     self.imagearr[ian[0], ian[1]] = pix
                # if r & 2:
                #     self.imagearr[ian[0] + 1, ian[1] + 1] = pix
                # if r & 4:
                #     self.imagearr[ian[0]+1, ian[1]] = pix
                # if r & 8:
                #     self.imagearr[ian[0], ian[1]+1] = pix

                # self.imagearr[ian[0], ian[1]] = pix
                # self.imagearr[ian[0] + 1, ian[1] + 1] = pix
                # self.imagearr[ian[0] + 1, ian[1]] = pix
                # self.imagearr[ian[0], ian[1] + 1] = pix

        self.pa.nextpahse()
        self.ic += 1
        if self.ic % 2 == 0:
            self.nc += 1


class LEDCube(SampleBase):

    sidedata = [
        ("Ba", (1, 1, 0), (0, 0, 0), (0, 1, 0)),
        ("Up", (1, 1, 0), (0, 1, 0), (0, 0, 32)),
        ("Fr", (1, 1, 0), (0, 0, 32), (0, -1, 32)),
        ("Ri", (0, 0, 32), (1, -1, 32), (0, -1, 32)),
        ("Do", (0, -1, 32), (1, -1, 32), (0, 0, 0)),
        ("Le", (0, 0, 0), (1, -1, 32), (0, 1, 0))

    ]

    def __init__(self, *args, **kwargs):
        self.kill = False
        self.squares = []
        self.reset()
        self.preg = [0 ,0 , 0]
        self.shakec = 0
        self.frame = 0
        super(LEDCube, self).__init__(*args, **kwargs)

    def reset(self):
        for n in LEDCube.sidedata:
            s = Square(n, self)
            self.squares.append(s)

    def run(self):
        image = Image.new("RGB", (96, 64))

        vect = [0,0,0]

        while True:

            if self.kill:
                self.reset()
                self.kill = False

            gravity = get_accelvector()

            if gravity is None:
                continue

            pdx = gravity[0]-self.preg[0]
            pdy = gravity[1]-self.preg[1]
            pdz = gravity[2]-self.preg[2]

            diffv = math.sqrt(pdx*pdx + pdy*pdy + pdz*pdz)
            self.preg  = list(gravity)
            if 1500 < diffv:
                self.shakec += 1

                if 40 < self.shakec:
                    self.squares[0].restart()

            else:
                self.shakec -= 2
                if self.shakec < 0:
                    self.shakec = 0

            for i in range(0, 3):
                for j in range(0, 2):
                    s = self.squares[j*3+i]

                    s.draw(vect)

                    D = 0.000005

                    vect[0] += -D * gravity[0]
                    vect[1] += -D * gravity[1]
                    vect[2] += D * gravity[2]


                    tile = s.image

                    image.paste(tile, (i*32, j*32))

            self.matrix.SetImage(image)

            self.frame += 1
            print self.frame

# Main function
if __name__ == "__main__":
    sys.argv += ["--led-chain", "3", "--led-parallel", "2", "--led-brightness", "75", "--led-slowdown-gpio", "2"]
    graphics_test = LEDCube()
    if (not graphics_test.process()):
        graphics_test.print_help()