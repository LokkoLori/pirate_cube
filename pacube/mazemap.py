from PIL import Image
from PIL import ImageDraw
import os

from colors import getcolor

potsect = ""

class Hero:
    def __init__(self, loc, x, y, s, c):
        self.loc = loc
        self.x = x
        self.y = y
        self.state = s
        self.color = c
        self.moved = False
        self.copyof = None
        self.copy = None

    def draw(self, image):
        d = ImageDraw.Draw(image)

        x = int(self.x)
        y = int(self.y)
        d.rectangle((x - 1, y, x + 4, y + 3), fill=(0, 0, 0))
        d.rectangle((x, y - 1, x + 3, y + 4), fill=(0, 0, 0))
        d.rectangle((x + 1, y + 1, x + 2, y + 2), fill=getcolor(self.color, 0))
        f = getcolor(self.color, 1)
        d.line((x + 1, y, x + 2, y), fill=f)
        d.line((x + 3, y + 1, x + 3, y + 2), fill=f)
        d.line((x + 2, y + 3, x + 1, y + 3), fill=f)
        d.line((x, y + 2, x, y + 1), fill=f)


class charimage:

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.map = []
        for h in range(0, self.height):
            row = [""] * width
            self.map.append(row)

    def fillrect(self, x1, y1, x2, y2, char):
        for y in range(y1,y2+1):
            for x in range(x1,x2+1):
                self.map[y][x] = char

    def getline(self, x, y, length, vertical=False):
        r = ""
        for i in range(0, length):
            if -1 < x and x < self.width and -1 < y and y < self.height:
                r += self.map[y][x].lower()
            if vertical:
                y += 1
            else:
                x += 1

        return r

    def drawOnImage(self, image, chars=None, tock=0):

        pixels = image.load()
        for y in range(0, self.height):
            for x in range(0, self.width):
                c = self.map[y][x]
                if c == "":
                    continue
                if chars and c.lower() not in chars:
                    continue

                pixels[x, y] = getcolor(c.lower(), tock)

    def totext(self):
        t = ""
        for y in range(0, self.height):
            for x in range(0, self.width):
                c = self.map[y][x]
                if c == "":
                    t += " "
                else:
                    t += c

            t += "\n"
        return t

class mapSect():

    def __init__(self):
        self.top = " "
        self.bottom = " "
        self.left = " "
        self.right = " "
        self.left_top = " "
        self.right_top = " "
        self.left_bottom = " "
        self.right_bottom = " "
        self.floor = " "
        self.owner = None
        self.i = -1
        self.j = -1
        self.x = 0
        self.y = 0

        self.tick = 0
        self.tack = 0

        self.inaction = ""

    def drawToWallmap(self, wallmap):

        ox = self.x
        oy = self.y

        if self.left != " ":
            wallmap.fillrect(ox - 2, oy, ox - 1, oy + 4, self.left)

        if self.top != " ":
            wallmap.fillrect(ox, oy - 2, ox + 4, oy - 1, self.top)

        if self.right != " ":
            wallmap.fillrect(ox + 4, oy, ox + 5, oy + 4, self.right)

        if self.bottom != " ":
            wallmap.fillrect(ox, oy + 4, ox + 4, oy + 5, self.bottom)

        if self.left_top == "o":
            wallmap.fillrect(ox - 2, oy - 2, ox - 1, oy - 1, "w")

        if self.right_top == "o":
            wallmap.fillrect(ox + 4, oy - 2, ox + 5, oy - 1, "w")

        if self.left_bottom == "o":
            wallmap.fillrect(ox - 2, oy + 4, ox - 1, oy + 5, "w")

        if self.right_bottom == "o":
            wallmap.fillrect(ox + 4, oy + 4, ox + 5, oy + 5, "w")



    def renderFloor(self, image, tick):

        d = ImageDraw.Draw(image)

        ox = self.x
        oy = self.y

        tock = tick % 4
        if self.floor not in [" ", "#"]:
            if tock == 0:
                d.rectangle((ox + 1, oy + 1, ox + 1, oy + 1), fill=getcolor(self.floor))
            elif tock == 1:
                d.rectangle((ox + 1, oy + 2, ox + 1, oy + 2), fill=getcolor(self.floor))
            elif tock == 2:
                d.rectangle((ox + 2, oy + 2, ox + 2, oy + 2), fill=getcolor(self.floor))
            elif tock == 3:
                d.rectangle((ox + 2, oy + 1, ox + 2, oy + 1), fill=getcolor(self.floor))

        tock = tick % 3
        if self.floor == "#":
            if tock == 0:
                d.rectangle((ox - 1, oy-1, ox + 4, oy + 4), fill=getcolor("h", 0))
                d.rectangle((ox, oy, ox + 3, oy + 3), fill=getcolor("h", 1))
                d.rectangle((ox+1, oy+1, ox + 2, oy + 2), fill=(0,0,0))
            if tock == 1:
                d.rectangle((ox - 1, oy - 1, ox + 4, oy + 4), fill=(0,0,0))
                d.rectangle((ox, oy, ox + 3, oy + 3), fill=getcolor("h", 0))
                d.rectangle((ox+1, oy+1, ox + 2, oy + 2), fill=getcolor("h", 1))
            if tock == 2:
                d.rectangle((ox - 1, oy-1, ox + 4, oy + 4), fill=getcolor("h", 1))
                d.rectangle((ox, oy, ox + 3, oy + 3), fill=(0,0,0))
                d.rectangle((ox+1, oy+1, ox + 2, oy + 2), fill=getcolor("h", 0))


    def action(self, hero):

        if self.floor == " ":
            return

        if int(hero.x) == self.x and int(hero.y) == self.y:

            if not self.inaction:

                if self.floor == "#":
                    self.inaction = "welldone"
                    self.owner.welldone()
                else:
                    self.inaction = hero
                    hero.state = self.owner.colorscheme
                    self.owner.colorscheme = self.floor.lower()

        else:
            if self.inaction == hero:
                #onleave event
                self.floor = hero.state
                self.inaction = None


def parsemap(filename, owner=None):
    try:
        with open(os.path.join(os.path.dirname(__file__),filename)) as f:
            mapstr = f.read()
    except Exception as e:
        return [], []

    rc = 0
    map = []
    heroes = []
    mapline = None
    lines = mapstr.split("\n")
    phase = 0

    while rc < len(lines):

        line = lines[rc]
        line = line.replace("\r", "").replace("\n", "")
        if phase == 0:
            mapline = []
            map.append(mapline)
        lc = 0
        mlc = 0
        while lc < len(line)-1:
            if phase == 0:
                ms = mapSect()
                ms.owner = owner
                ms.left_top = line[lc]
                ms.top = line[lc+1]
                ms.right_top = line[lc + 2]
                ms.i = len(mapline)
                ms.j = len(map) - 1
                ms.x = ms.i*6+2
                ms.y = ms.j*6+2
                mapline.append(ms)
            elif phase == 1:
                ms = mapline[mlc]
                ms.left = line[lc]
                ms.floor = line[lc + 1]

                if ms.floor in ["h", "d"]:
                    heroes.append(Hero(filename[:-4], ms.x, ms.y, s = " ", c = ms.floor))
                    ms.floor = " "

                ms.right = line[lc + 2]
                mlc += 1
            elif phase == 2:
                ms = mapline[mlc]
                ms.left_bottom = line[lc]
                ms.bottom = line[lc + 1]
                ms.right_bottom = line[lc + 2]
                mlc += 1
            lc += 2

        phase += 1
        if phase == 3:
            phase = 0
        else:
            rc += 1

    map = map[:-1]

    return map, heroes

if __name__ == "__main__":
    map, heroes = parsemap("Up.map")

    mazeWalls = charimage(32, 32)
    for row in map:
        for sect in row:
            sect.drawToWallmap(mazeWalls)

    print mazeWalls.totext()
    pass