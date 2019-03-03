import sys, os

rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(rootdir)

from pixxlcube.cubecore import PiXXLSide, PiXXLCube, ShakeGestureHandler

from PIL import ImageDraw, ImageFont, Image
import math
from mazemap import parsemap, charimage, Hero
from colors import setColorChema


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


arialfont = ImageFont.truetype(os.path.join(os.path.dirname(__file__),"arial.ttf"), 10)

D = -0.9
tickcount = 4

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

class PaSide(PiXXLSide):

    def __init__(self, cube, data):
        super(PaSide, self).__init__(cube, data)
        self.reset()


    def reset(self):

        self.map, heroes = parsemap("{}.map".format(self.name), owner=self)
        self.cube.heroes += heroes
        self.mazeImage = Image.new("RGB", (32, 32))
        self.mazeWalls = charimage(32, 32)

        self.last_colorscheme = ""
        self.colorscheme = "b"

        self.tick = 0
        self.tock = 0
        self.showwelldone = False


    def drawmaze(self):

        for row in self.map:
            for sect in row:
                sect.drawToWallmap(self.mazeWalls)

        d = ImageDraw.Draw(self.mazeImage)
        d.rectangle((0, 0, 31, 31), fill=(0, 0, 0))
        self.mazeWalls.drawOnImage(self.mazeImage, ["|","-","w"])


    def edgeCase(self, hero, dx, dy):
        conv = None

        coords = [int(hero.x), int(hero.y)]
        dcoord = [dx, dy]

        if coords[1] < 0:
            conv = facematrix[self.name]["my"]
        if coords[1] > 28:
            conv = facematrix[self.name]["py"]
        if coords[0] < 0:
            conv = facematrix[self.name]["mx"]
        if coords[0] > 28:
            conv = facematrix[self.name]["px"]

        if not conv:
            hero.copy = None
            return

        if not hero.copy:

            hero.copy = Hero(conv[0], 0, 0, " ", hero.color)
            hero.copy.copyof = hero

        hero.copy.x = conv[4] + conv[5]*coords[conv[3]]
        hero.copy.y = conv[7] + conv[8]*coords[conv[6]]

        if (coords[conv[2]] <= -2 and not conv[1] and 0 < dcoord[conv[2]]) or (coords[conv[2]] >= 30 and conv[1] and dcoord[conv[2]] < 0):
            if D < 0 or math.fabs(dcoord[conv[2]]) > 0.9:
                #print "hopp"
                self.cube.heroes.remove(hero)
                hero.copy.copyof = None
                self.cube.heroes.append(hero.copy)
                hero.copy = None

    def handleHero(self, hero, gravity):

        if hero.loc != self.name:
            return

        hero.draw(self.image)

        if hero.copyof:
            return

        gx = gravity[0]
        gy = gravity[1]
        gz = gravity[2]

        gl = math.sqrt(gx * gx + gy * gy + gz * gz)

        dx = -gx / gl
        dy = gy / gl

        self.edgeCase(hero, dx, dy)

        dx = D * treshold(dx, 0.175, 0.5)
        dy = D * treshold(dy, 0.175, 0.5)

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

        # # find the dominant direction
        # if math.fabs(dx) < math.fabs(dy):
        #     dx = 0
        # else:
        #     dy = 0

        for row in self.map:
            for sect in row:
                sect.action(hero)

        hero.x += dx
        hero.y += dy

        if hero.y < -2:
            hero.y = -2
        if hero.y > 30:
            hero.y = 30
        if hero.x < -2:
            hero.x = -2
        if hero.x > 30:
            hero.x = 30


    def welldone(self):

        self.cube.aboutRestart(200)
        self.showwelldone = True


    def draw(self):

        setColorChema(self.colorscheme)
        if self.colorscheme != self.last_colorscheme:
            self.last_colorscheme = self.colorscheme
            self.drawmaze()

        self.image.paste(self.mazeImage)

        self.tick += 1
        if self.tick == tickcount:
            self.tick = 0
            self.tock += 1

        if self.cube.restartCounter:

            if self.cube.restartCounter % 3 == 0:
                cs = "r"
            if self.cube.restartCounter % 3 == 1:
                cs = "g"
            if self.cube.restartCounter % 3 == 2:
                cs = "b"

            self.colorscheme = cs

        for row in self.map:
            for sect in row:
                sect.renderFloor(self.image, self.tock)

        self.mazeWalls.drawOnImage(self.image, ["r", "g", "b", "y"], self.tock)

        for hero in self.cube.heroes:
            self.handleHero(hero, self.getAlignedGravity())
            if hero.copy:
                self.handleHero(hero.copy, self.getAlignedGravity())

        if self.showwelldone:
            d = ImageDraw.Draw(self.image)
            d.rectangle((1, 1, 30, 30), fill=(0, 0, 0))
            d.text((2, 3), "WELL", font=arialfont)
            d.text((2, 17), "DONE", font=arialfont)

        return

class PaCube(PiXXLCube):

    def __init__(self):
        self.heroes = []
        super(PaCube, self).__init__(PaSide)
        self.restartCounter = 0
        self.addGestureHandler(ShakeGestureHandler(self.shakeRestart))

    def reset(self):
        self.heroes = []
        for side in self.sides:
            side.reset()

    def aboutRestart(self, cicle):
        self.restartCounter = cicle

    def shakeRestart(self):
        print "shake_restart"
        self.aboutRestart(30)

    def preDrawHook(self):

        if self.restartCounter:
            self.restartCounter -= 1
            if self.restartCounter == 0:
                self.reset()


if __name__ == "__main__":
    cube = PaCube()
    cube.run()