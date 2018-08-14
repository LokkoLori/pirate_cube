from samplebase import SampleBase
from rgbmatrix import graphics
import time
import sys
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL.Image import FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM, ROTATE_90, ROTATE_180, ROTATE_270
from accelero import get_accelvector
from mazemap import parsemap, charimage, Hero
import math
from colors import getcolor, setColorChema


arialfont = ImageFont.truetype("arial.ttf", 18)

D = 0.9

def treshold(x, mina, maxa):
    if math.fabs(x) < mina:
        return 0
    if x < 0:
        x += mina
        if x < -maxa:
            x = -maxa

    else:
        x -= mina
        if maxa < x:
            x = maxa

    return x

HEROES = []

tickcount = 8

prints = ""

class Square():

    def __init__(self, name):
        global HEROES
        self.image = Image.new("RGB", (32, 32))
        self.name = name
        self.map, heroes = parsemap("{}.map".format(self.name), owner=self)
        HEROES += heroes

        self.mazeImage = Image.new("RGB", (32, 32))
        self.mazeWalls = charimage(32, 32)

        self.last_colorscheme = ""
        self.colorscheme = "b"

        self.tick = 0
        self.tock = 0

    def drawmaze(self):

        for row in self.map:
            for sect in row:
                sect.drawToWallmap(self.mazeWalls)

        d = ImageDraw.Draw(self.mazeImage)
        d.rectangle((0, 0, 31, 31), fill=(0, 0, 0))
        self.mazeWalls.drawOnImage(self.mazeImage, ["|","-","w"])

    def drawhero(self, hero):

        d = ImageDraw.Draw(self.image)

        x = hero.x
        y = hero.y
        d.rectangle((x + 1, y + 1, x + 2, y + 2), fill=getcolor("h", 0))
        f = getcolor("h", 1)
        d.line((x + 1, y, x + 2, y ), fill=f)
        d.line((x + 3, y + 1, x + 3, y + 2), fill=f)
        d.line((x + 2, y + 3, x + 1, y + 3), fill=f)
        d.line((x, y + 2, x, y + 1), fill=f)

    def handleHero(self, hero, gravity):

        if hero.loc != self.name:
            return

        self.drawhero(hero)

        if hero.copyof:
            return

        gx = gravity[0]
        gy = gravity[1]
        gz = gravity[2]

        gl = math.sqrt(gx * gx + gy * gy + gz * gz)

        dx = gx / gl
        dy = gy / gl

        if hero.y < 0:
            if not hero.copy:
                newfacet = "Fr"
                if hero.loc == "Fr":
                    newfacet = "Up"
                hero.copy = Hero(newfacet, 0, 0, "h")
                hero.copy.copyof = hero
            hero.copy.x = 28 - int(hero.x)
            hero.copy.y = - 4 - int(hero.y)

            if hero.y <= -2 and math.fabs(dy) > 0.7:

                #add to other side
                HEROES.remove(hero)
                hero.copy.copyof = None
                HEROES.append(hero.copy)
                hero.copy = None
        else:
            hero.copy = None

        dx = D * treshold(dx, 0.1, 0.5)
        dy = D * treshold(dy, 0.1, 0.5)

        l = self.mazeWalls.getline(int(hero.x) - 1, int(hero.y), 4, vertical=True).replace(self.colorscheme, "")
        r = self.mazeWalls.getline(int(hero.x) + 4, int(hero.y), 4, vertical=True).replace(self.colorscheme, "")
        t = self.mazeWalls.getline(int(hero.x), int(hero.y) - 1, 4).replace(self.colorscheme, "")
        b = self.mazeWalls.getline(int(hero.x), int(hero.y) + 4, 4).replace(self.colorscheme, "")

        if False:
            global prints
            s = "l '{}' r '{}' t '{}' b '{}'".format(l, r, t, b)
            if prints != s:
                print s
                prints = s

        if dx < 0 and l:
            dx = 0
        if dx > 0 and r:
            dx = 0
        if dy < 0 and t:
            dy = 0
        if dy > 0 and b:
            dy = 0

        # find the dominant direction
        if math.fabs(dx) < math.fabs(dy):
            dx = 0
        else:
            dy = 0

        for row in self.map:
            for sect in row:
                sect.action(hero)

        hero.x += dx
        hero.y += dy

        if hero.y < -2:
            hero.y = -2


    def draw(self, gravity):

        setColorChema(self.colorscheme)
        if self.colorscheme != self.last_colorscheme:
            self.last_colorscheme = self.colorscheme
            self.drawmaze()

        self.image.paste(self.mazeImage)

        self.tick += 1
        if self.tick == tickcount:
            self.tick = 0
            self.tock += 1

        for row in self.map:
            for sect in row:
                sect.renderFloor(self.image, self.tock)

        self.mazeWalls.drawOnImage(self.image, ["r", "g", "b"], self.tock)


        for hero in HEROES:
            self.handleHero(hero, gravity)
            if hero.copy:
                self.handleHero(hero.copy, gravity)

        return


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
            [[-1, 0], [-1, 2], [1, 1], [ROTATE_270]],
            [[-1, 0], [1, 1], [1, 2], [ROTATE_270]],
            [[1, 0], [-1, 2], [-1, 1], [ROTATE_90]],
            [[-1, 1], [-1, 2], [-1, 0], [ROTATE_90]],
            [[-1, 0], [-1, 1], [-1, 2], [ROTATE_180]],
            [[1, 1], [-1, 2], [1, 0], [ROTATE_270]]
        ]

        while True:

            gravity = get_accelvector()

            if gravity is None:
                continue

            for i in range(0, 3):
                for j in range(0, 2):
                    f = self.facets[j*3+i]
                    v = vects[j*3+i]

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