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

    def val(self):
        return math.sin(self.phase)

    def nextpahse(self):
        self.phase += 1

class Square():

    def __init__(self, name, owner):
        self.image = Image.new("RGB", (32, 32))
        self.imagearr = self.image.load()
        self.name = name
        self.owner = owner
        self.time = 0
        self.pa = PulseAnim(1)

    def draw(self, gravity):


        w = 32
        h = 32
        p = self.pa.val()
        if self.name not in ["Up", "Ba"]:
            return
        for x in range(w):
            for y in range(h):
                hue = 4.0 + math.sin(x / 19.0 + p) + math.sin(y / 9.0 - p) \
                      + math.sin((x + y) / 25.0 + p) + math.sin(math.sqrt(x ** 2.0 + y ** 2.0) / (8.0-p))
                hsv = colorsys.hsv_to_rgb(hue / 8.0, 1, 1)
                self.imagearr[x, y] = tuple([int(round(c * 255.0)) for c in hsv])

        self.pa.nextpahse()

class LEDCube(SampleBase):
    def __init__(self, *args, **kwargs):
        self.kill = False
        self.squares = []
        self.reset()
        self.preg = [0 ,0 , 0]
        self.shakec = 0
        self.frame = 0
        super(LEDCube, self).__init__(*args, **kwargs)

    def reset(self):
        for n in ["Ba", "Up", "Fr", "Ri", "Do", "Le"]:
            self.squares.append(Square(n, self))

    def run(self):
        image = Image.new("RGB", (96, 64))

        vects = [
            [[-1, 0], [-1, 2], [1, 1], [ROTATE_270]],
            [[-1, 0], [1, 1], [1, 2], [ROTATE_270]],
            [[1, 0], [-1, 2], [-1, 1], [ROTATE_90]],
            [[-1, 1], [-1, 2], [-1, 0], [ROTATE_90]],
            [[-1, 0], [-1, 1], [-1, 2], [ROTATE_180]],
            [[1, 1], [-1, 2], [1, 0], [ROTATE_270]]
        ]

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
                    v = vects[j*3+i]

                    g = []
                    for k in range(0, 3):
                        g.append(gravity[v[k][1]]*v[k][0])

                    s.draw(g)

                    tile = s.image
                    for t in v[3]:
                        tile = tile.transpose(t)

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