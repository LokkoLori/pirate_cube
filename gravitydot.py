from samplebase import SampleBase
from rgbmatrix import graphics
import time
import sys
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL.Image import FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM, ROTATE_90, ROTATE_180, ROTATE_270
from accelero import get_accelvector
import math


arialfont = ImageFont.truetype("arial.ttf", 18)

D = 1

def normtobox(x, val):
    if x < -val:
        x = -val
    if val < x:
        x = val

    return x

class Square():

    def __init__(self, name):
        self.image = Image.new("RGB", (32, 32))
        self.name = name
        self.creture = [0, 0]

    def draw(self, gravity):
        d = ImageDraw.Draw(self.image)
        d.rectangle((0, 0, 31, 31), fill=(0, 0, 0), outline=(0, 0, 255))

        d.text((0, 0), self.name, font=arialfont)

        gx = gravity[0]
        gy = gravity[1]
        gz = gravity[2]

        gl = math.sqrt(gx*gx + gy*gy + gz*gz)

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

        px = x*16 + 16
        py = -y*16 + 16

        d.ellipse((px-2, py-2, px+2, py+2), fill=fill, outline=(0, 0, 0))

        dx = gx / gl
        dy = gy / gl

        dx = D * normtobox(dx, 0.5)
        dy = -D * normtobox(dy, 0.5)

        self.creture[0] += dx
        self.creture[1] += dy

        self.creture[0] = normtobox(self.creture[0], 12)
        self.creture[1] = normtobox(self.creture[1], 12)

        cpx = self.creture[0] + 16
        cpy = self.creture[1] + 16
        d.ellipse((cpx - 3, cpy - 3, cpx + 3, cpy + 3), fill=(255, 255, 0), outline=(255, 128, 0))


class LEDCube(SampleBase):
    def __init__(self, *args, **kwargs):
        names = ["Ba", "Up", "Fr", "Ri", "Do", "Le"]
        self.facets = []
        for n in names:
            self.facets.append(Square(n))
        super(LEDCube, self).__init__(*args, **kwargs)

    def run(self):
        image = Image.new("RGB", (96, 64))

        vects = [
            [[1, 0], [1, 2], [-1, 1], [ROTATE_270]],
            [[1, 0], [1, 1], [1, 2], [ROTATE_270]],
            [[-1, 0], [1, 2], [1, 1], [ROTATE_90]],
            [[1, 1], [1, 2], [1, 0], [ROTATE_90]],
            [[1, 0], [-1, 1], [-1, 2], [ROTATE_180]],
            [[-1, 1], [1, 2], [-1, 0], [ROTATE_270]]
        ]

        while True:

            gravity = get_accelvector()

            if gravity is None:
                continue

            for i in range(0, 3):
                for j in range(0, 2):
                    f = self.facets[j*3+i]
                    v = vects[j*3+i]

                    #print "{0000:.2f}, {0000:.2f}, {0000:.2f}\x1b[A".format(gravity[0]/160, gravity[1]/160, gravity[2]/160)

                    g = []
                    for k in range(0, 3):
                        g.append(gravity[v[k][1]]*v[k][0])

                    f.draw(g)

                    tile = f.image
                    for t in v[3]:
                        tile = tile.transpose(t)

                    image.paste(tile, (i*32, j*32))

            self.matrix.SetImage(image)



# Main function
if __name__ == "__main__":
    sys.argv += ["--led-chain", "3", "--led-parallel", "2", "--led-brightness", "75", "--led-slowdown-gpio", "2"]
    graphics_test = LEDCube()
    if (not graphics_test.process()):
        graphics_test.print_help()