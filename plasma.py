import colorsys
from samplebase import SampleBase
import sys
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter
from PIL import ImageChops
from PIL import ImageFont
from PIL.Image import ROTATE_90, ROTATE_180, ROTATE_270
from accelero import get_accelvector
import math
import random


# CCUBEIMAGE = Image.open("ccube.png")
# QCUBEIMAGE = Image.open("qcube.png")
# GRANDPIXIMAGE = Image.open("grandpix.png")

IMAGES = [
    ["ccube.png", None],
    ["qcube.png", None],
    ["grandpix.png", None]
]

for i in IMAGES:
    i[1] = Image.open(i[0])

s15font = ImageFont.truetype("square-deal.ttf", 15)

TEXTS = [
    ["Ri", "WHAT IF I TOLD YOU, THIS CUBE IS A DEMO PLATFORM?", 0, 18, s15font],
    ["Ba", "WHAT IF I TOLD YOU, THIS CUBE IS A DEMO PLATFORM?", 0, 18, s15font],
    ["Le", "WHAT IF I TOLD YOU, THIS CUBE IS A DEMO PLATFORM?", 0, 18, s15font]
]

class RunningPhase():

    def __init__(self, step):
        self.phase = 0
        self.step = step

    def nextpahse(self):
        self.phase += self.step


def drawSubpixelPoint(d, x, y, cl):

    env = []
    for ry in range(int(y), int(y) + 2):
        for rx in range(int(x), int(x) + 2):
            dx = math.fabs(x - rx)
            dy = math.fabs(y - ry)

            dc = (1 - dx) * (1 - dy)

            env.append([rx, ry, dc])

    for e in env:

        fillc = []
        for c in cl:
            fillc.append(c)

        fillc[3] = int(255*e[2])

        d.point((e[0],e[1],e[0],e[1]), fill=tuple(fillc))


class FreeFly():

    freeflies = []

    def __init__(self, color, loc=[16, 16, 32], svelo=0.5, lurk=0.05):

        self.loc = loc
        self.vel = [random.uniform(-svelo, svelo), random.uniform(-svelo, svelo), 0]
        self.lurk = lurk
        self.color = color

    def onSquare(self, square):
        for coi in range(0,3):
            if square.coordtrs[coi][0] == -1:
                if self.loc[coi] != square.coordtrs[coi][2]:
                    return False

        return True

    def draw(self, square, grav):

        if not self.onSquare(square):
            return

        stick_coord = square.getStickCoord()

        for coi in range(0,3):
            if square.coordtrs[coi][0] == 0:
                xco = self.loc[coi] * square.coordtrs[coi][1] + square.coordtrs[coi][2]

            if square.coordtrs[coi][0] == 1:
                yco = self.loc[coi] * square.coordtrs[coi][1] + square.coordtrs[coi][2]

        drawSubpixelPoint(square.fliesImageDraw, xco, yco, self.color)

        top = -1
        if not self.loc[stick_coord]:
            top = 1

        D = - 0.0000005

        sgrav = list(grav)

        sgrav[0] = D * grav[0]
        sgrav[1] = D * grav[1]
        sgrav[2] = - D * grav[2]

        for coi in range(0,3):
            if coi != stick_coord:
                self.vel[coi] += random.uniform(-self.lurk, self.lurk) + sgrav[coi]

            self.vel[coi] *= 0.998

            if self.vel[coi] > 1:
                self.vel[coi] = 1
            elif self.vel[coi] < -1:
                self.vel[coi] = -1


        self.loc[0] += self.vel[0]
        self.loc[1] += self.vel[1]
        self.loc[2] += self.vel[2]

        firstonsqare = None

        for other in FreeFly.freeflies:
            if other == self or not other.onSquare(square):
                continue

            firstonsqare = other
            break

        if firstonsqare:
            for v in range(0, 3):
                self.vel[v] += 0.005 * (firstonsqare.vel[v] - self.vel[v])
                self.vel[v] += 0.005 * (firstonsqare.loc[v] - self.loc[v])


        for i in range(0, 3):

            if i == stick_coord:
                continue

            if self.loc[i] < 0:
                self.loc[stick_coord] += self.loc[i]
                self.loc[i] = 0
                self.vel[stick_coord] = top * math.fabs(self.vel[i])
                self.vel[i] = 0
            if 32 < self.loc[i]:
                self.loc[stick_coord] += 32 - self.loc[i]
                self.loc[i] = 32
                self.vel[stick_coord] = top * math.fabs(self.vel[i])
                self.vel[i] = 0


class Square():

    def __init__(self, data, owner):
        self.plasmaimage = Image.new("RGBA", (32, 32))
        self.plasmaimagearr = self.plasmaimage.load()
        self.fliesImage = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        self.fliesImageDraw = ImageDraw.Draw(self.fliesImage, mode="RGBA")
        self.image = Image.new("RGBA", (32, 32))

        self.name = data[0]
        self.coordtrs =  data[1:-1]
        self.owner = owner
        self.pa = RunningPhase(0.05)
        self.ic = 0
        self.nc = 0
        self.trans = data[-1]

        self.loadedimages = []

        for i in IMAGES:
            si = list(i)
            if self.trans:
                si[1] = si[1].transpose(self.trans)
            self.loadedimages.append(si)


    def getStickCoord(self):

        for coi in range(0,3):
            if self.coordtrs[coi][0] == -1:
                return coi

        return -1


    def drawplasma(self, vect):

        o = 2
        interlaced = [True, True]
        huedrifting = False
        satdrifting = False
        valuedrifting = False

        for i in xrange(32/o):
            if interlaced[0] and (i + self.ic) % 2 != 0:
                continue
            for n in xrange(32/o):
                if interlaced[1] and (n + self.nc) % 2 != 0:
                    continue
                ian = [i*o, n*o]
                crs = []
                for cin in range(0, 3):
                    c = self.coordtrs[cin]
                    ci = c[0]
                    if ci < 0:
                        ci = 0
                    crs.append(ian[ci]*c[1]+c[2] + vect[cin])

                x, y, z = crs
                p = self.pa.phase

                hue = math.sin(x * 0.3) + math.cos(y * 0.5) + math.sin(z * 0.25) + math.cos((x+y+z) * 0.16) + 0.5*math.sin(p)
                hue = hue / 3.0
                if hue < -1:
                    hue = -1
                elif 1 < hue:
                    hue = 1
                hue = (hue + 1) / 2.0

                if huedrifting:
                    sp = p / 10.0
                    sp = sp - int(sp)

                    shue = hue + sp

                    if shue < 0:
                        shue = 1 + shue
                    elif shue > 1:
                        shue = shue - 1
                else:
                    shue = hue

                if satdrifting:
                    sat = (math.sin(p * 4) + 1.0) * 0.5
                else:
                    sat = 1.0

                if valuedrifting:
                    value = (1 - hue) * (0.25 + (math.sin(p) + 1.0) * 0.5)
                else:
                    value = (1 - hue)

                hsv = colorsys.hsv_to_rgb(shue, sat, value)

                pix = tuple([int(round(c * 255.0)) for c in hsv])

                if o == 1:
                    self.plasmaimagearr[ian[0], ian[1]] = pix
                elif o == 2:
                    self.plasmaimagearr[ian[0] + 0, ian[1] + 0] = pix
                    self.plasmaimagearr[ian[0] + 1, ian[1] + 0] = pix
                    self.plasmaimagearr[ian[0] + 0, ian[1] + 1] = pix
                    self.plasmaimagearr[ian[0] + 1, ian[1] + 1] = pix

        self.image = self.plasmaimage.filter(ImageFilter.GaussianBlur())

        self.pa.nextpahse()
        self.ic += 1
        if self.ic % 2 == 0:
            self.nc += 1


    def drawfreeflies(self, gravity):

        fliesfade = False
        blurflies = True

        simage = None
        if fliesfade:
            if self.ic % 3 == 0:
                fader = Image.new("RGBA", (32, 32))
                fader = Image.blend(fader, self.fliesImage, alpha=0.8)
                self.fliesImage.paste(fader)
                del fader
            simage = self.fliesImage.copy()
            self.fliesImage = Image.new("RGBA", (32, 32))
            self.fliesImageDraw = ImageDraw.Draw(self.fliesImage)

        elif blurflies:
            simage = self.fliesImage.filter(ImageFilter.GaussianBlur(radius=1))
            self.fliesImage = Image.new("RGBA", (32, 32))
            self.fliesImageDraw = ImageDraw.Draw(self.fliesImage)
        else:
            self.fliesImageDraw.rectangle((0, 0, 31, 31), fill=(0, 0, 0, 0))

        for ff in FreeFly.freeflies:
            ff.draw(self, gravity)

        s2image = None
        if fliesfade or blurflies:
            simage.paste(self.fliesImage, (0, 0), self.fliesImage)
            s2image = self.fliesImage
            self.fliesImage = simage

        self.image = ImageChops.difference(self.image, self.fliesImage)
        if s2image:
            self.image.paste(s2image, (0, 0), s2image)
            del s2image


    def drawtext(self):

        textbmp = Image.new("RGBA", (32,32))
        d = ImageDraw.Draw(textbmp)

        for t in TEXTS:
            if t[0] == self.name:
                d.text((t[2], t[3]), t[1], font=t[4])

        if self.trans:
            textbmp = textbmp.transpose(self.trans)
        self.image.paste(textbmp, (0, 0), textbmp)

        del textbmp


    def draw(self, vect, gravity):

        drawplasma = False
        drawfreefiles = True
        showimages = ["qcube.png"]
        showimages = []

        if drawplasma:
            self.drawplasma(vect)
        else:
            d = ImageDraw.Draw(self.image)
            d.rectangle((0,0, 31, 31), fill=(0,0,0))

        #fireflies

        if drawfreefiles:
            self.drawfreeflies(gravity)

        for si in showimages:
            for i in self.loadedimages:
                if i[0] == si:
                    self.image.paste(i[1], (0,0), i[1])
                    break


        self.drawtext()


class LEDCube(SampleBase):

    sidedata = [
        ("Ba", (1, 1, 0), (-1, 0, 0), (0, 1, 0), ROTATE_270),
        ("Up", (1, 1, 0), (0, 1, 0), (-1, 0, 32), ROTATE_270),
        ("Fr", (1, 1, 0), (-1, 0, 32), (0, -1, 32), ROTATE_90),
        ("Ri", (-1, 0, 32), (1, -1, 32), (0, -1, 32), ROTATE_90),
        ("Do", (0, -1, 32), (1, -1, 32), (-1, 0, 0), None),
        ("Le", (-1, 0, 0), (1, -1, 32), (0, 1, 0), ROTATE_270)
    ]

    def __init__(self, *args, **kwargs):
        self.kill = False
        self.squares = []
        self.reset()
        self.preg = [0, 0, 0]
        self.shakec = 0
        self.frame = 0

        fc = 30
        hue = 0
        colorflies = True
        for n in range(0, fc):
            if colorflies:
                hue += 1.0 / fc
                rgb = list(colorsys.hsv_to_rgb(hue, 1, 1))
                rgb.append(1)
                FreeFly.freeflies.append(FreeFly(
                    color=tuple([int(round(c * 255.0)) for c in rgb]),
                    loc=[random.randint(0,32),random.randint(0,32),32],
                    lurk=0.2
                ))
            else:
                FreeFly.freeflies.append(FreeFly(
                    color=(255,255,255,255),
                    loc=[random.randint(0,32),random.randint(0,32),32],
                    lurk=0.2)
                )

        super(LEDCube, self).__init__(*args, **kwargs)

    def reset(self):
        for n in LEDCube.sidedata:
            s = Square(n, self)
            self.squares.append(s)

    def run(self):
        image = Image.new("RGB", (96, 64))

        vect = [0,0,0]

        scroll = 0

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

            scroll += 1

            offs = 32
            for t in TEXTS:
                fo = offs - int(scroll)
                t[2] = fo
                offs += 32

            if scroll == 400:
                scroll = 0

            for i in range(0, 3):
                for j in range(0, 2):
                    s = self.squares[j*3+i]

                    s.draw(vect, gravity)

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