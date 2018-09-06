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


s15font = ImageFont.truetype("square-deal.ttf", 15)
DEMO_CUBE = None

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

    def __init__(self, color, loc=[16, 16, 32]):

        self.loc = loc
        self.vel = [0, 0, 0]
        self.lurk = 0
        self.color = color
        self.blinking = False
        self.moving = False

    def onSquare(self, square):
        for coi in range(0,3):
            if square.coordtrs[coi][0] == -1:
                if self.loc[coi] != square.coordtrs[coi][2]:
                    return False

        return True

    def fitsoncube(self, cube):

        square = None
        for s in cube.squares:
            if self.onSquare(s):
                square = s
                break

        if not square:
            return

        stick_coord = square.getStickCoord()

        top = -1
        if not self.loc[stick_coord]:
            top = 1

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

    def move(self, oncube):

        # stick_coord = square.getStickCoord()
        #
        # D = - 0.0000005
        #
        # sgrav = list(grav)
        #
        # sgrav[0] = D * grav[0]
        # sgrav[1] = D * grav[1]
        # sgrav[2] = - D * grav[2]
        #
        # for coi in range(0, 3):
        #     if coi != stick_coord:
        #         self.vel[coi] += random.uniform(-self.lurk, self.lurk) + sgrav[coi]
        #
        #     self.vel[coi] *= 0.998
        #
        #     if self.vel[coi] > 1:
        #         self.vel[coi] = 1
        #     elif self.vel[coi] < -1:
        #         self.vel[coi] = -1
        #
        # firstonsqare = None
        #
        # for other in square.owner.freeflies:
        #     if other == self or not other.onSquare(square):
        #         continue
        #
        #     firstonsqare = other
        #     break
        #
        # if firstonsqare:
        #     for v in range(0, 3):
        #         self.vel[v] += 0.005 * (firstonsqare.vel[v] - self.vel[v])
        #         self.vel[v] += 0.005 * (firstonsqare.loc[v] - self.loc[v])

        self.loc[0] += self.vel[0]
        self.loc[1] += self.vel[1]
        self.loc[2] += self.vel[2]

        self.fitsoncube(oncube)



    def draw(self, square, grav):

        if not self.onSquare(square):
            return

        for coi in range(0,3):
            if square.coordtrs[coi][0] == 0:
                xco = self.loc[coi] * square.coordtrs[coi][1] + square.coordtrs[coi][2]

            if square.coordtrs[coi][0] == 1:
                yco = self.loc[coi] * square.coordtrs[coi][1] + square.coordtrs[coi][2]

        color = self.color
        if self.blinking and random.randint(0, 3) == 3:
            con = random.randint(-64, 64)
            color = []
            for c in self.color:
                c = c + con
                if c < 0:
                    c = 0
                if 255 < c:
                    c = 255
                color.append(c)

            color[3] = 255

        drawSubpixelPoint(square.fliesImageDraw, xco, yco, color)

        if self.moving:
            self.move(square, grav)


class Square():

    def __init__(self, data, owner):
        self.plasmaimage = Image.new("RGBA", (32, 32))
        self.plasmaimagearr = self.plasmaimage.load()
        self.fliesImage = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        self.fliesImageDraw = ImageDraw.Draw(self.fliesImage, mode="RGBA")
        self.image = Image.new("RGBA", (32, 32))
        self.drawlayer = Image.new("RGBA", (32, 32))
        self.darwer = ImageDraw.Draw(self.drawlayer, mode="RGBA")

        self.name = data[0]
        self.coordtrs =  data[1:-1]
        self.owner = owner
        self.pa = RunningPhase(0.05)
        self.ic = 0
        self.nc = 0
        self.trans = data[-1]

        self.plasma_offset = [0, 0, 0]
        self.plasma_flowing = False
        self.plasma_interlaced = False
        self.plasma_huedrifting = False
        self.plasma_satdrifting = False
        self.plasma_valuedrifting = False
        self.plasma_shown = False

        self.fly_tails_faded = False
        self.fly_tails_blurred = False
        self.flies_shown = False
        self.flies_diffblended = False

        self.images_shown = []

        self.texts = []

    def getStickCoord(self):

        for coi in range(0,3):
            if self.coordtrs[coi][0] == -1:
                return coi

        return -1


    def drawplasma(self, gravity):

        D = 0.00003
        if self.plasma_flowing:
            self.plasma_offset[0] += -D * gravity[0]
            self.plasma_offset[1] += -D * gravity[1]
            self.plasma_offset[2] += D * gravity[2]

        o = 2
        interlaced = [True, True]

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
                    crs.append(ian[ci]*c[1]+c[2] + self.plasma_offset[cin])

                x, y, z = crs
                p = self.pa.phase

                hue = math.sin(x * 0.3) + math.cos(y * 0.5) + math.sin(z * 0.25) + math.cos((x+y+z) * 0.16) + 0.5*math.sin(p)
                hue = hue / 3.0
                if hue < -1:
                    hue = -1
                elif 1 < hue:
                    hue = 1
                hue = (hue + 1) / 2.0

                if self.plasma_huedrifting:
                    sp = p / 10.0
                    sp = sp - int(sp)

                    shue = hue + sp

                    if shue < 0:
                        shue = 1 + shue
                    elif shue > 1:
                        shue = shue - 1
                else:
                    shue = hue

                if self.plasma_satdrifting:
                    sat = (math.sin(p * 4) + 1.0) * 0.5
                else:
                    sat = 1.0

                if self.plasma_valuedrifting:
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

        simage = None
        if self.fly_tails_faded:
            if self.ic % 3 == 0:
                fader = Image.new("RGBA", (32, 32))
                fader = Image.blend(fader, self.fliesImage, alpha=0.8)
                self.fliesImage.paste(fader)
                del fader
            simage = self.fliesImage.copy()
            self.fliesImage = Image.new("RGBA", (32, 32))
            self.fliesImageDraw = ImageDraw.Draw(self.fliesImage)

        elif self.fly_tails_blurred:
            simage = self.fliesImage.filter(ImageFilter.GaussianBlur(radius=1))
            self.fliesImage = Image.new("RGBA", (32, 32))
            self.fliesImageDraw = ImageDraw.Draw(self.fliesImage)
        else:
            self.fliesImageDraw.rectangle((0, 0, 31, 31), fill=(0, 0, 0, 0))

        for ff in self.owner.freeflies:
            ff.draw(self, gravity)

        s2image = None
        if self.fly_tails_faded or self.fly_tails_blurred:
            simage.paste(self.fliesImage, (0, 0), self.fliesImage)
            s2image = self.fliesImage
            self.fliesImage = simage

        if self.flies_diffblended:
            self.image = ImageChops.difference(self.image, self.fliesImage)
        else:
            self.image.paste(self.fliesImage, (0, 0), self.fliesImage)

        if s2image:
            self.image.paste(s2image, (0, 0), s2image)
            del s2image


    def drawtext(self):

        for t in self.texts:
            self.drawer.text((t[1], t[2]), t[0], font=t[3])


    def drawimages(self):

        for i in self.images_shown:
            self.drawlayer.paste(i[0], (i[1], i[2]), i[0])

    def draw(self, gravity):

        if self.plasma_shown:
            self.drawplasma(gravity)
        else:
            d = ImageDraw.Draw(self.image)
            d.rectangle((0,0, 31, 31), fill=(0,0,0))

        if self.flies_shown:
            self.drawfreeflies(gravity)

        self.drawlayer = Image.new("RGBA", (32,32))
        self.drawer = ImageDraw.Draw(self.drawlayer)

        self.drawimages()
        self.drawtext()

        if self.trans:
            self.drawlayer = self.drawlayer.transpose(self.trans)
        self.image.paste(self.drawlayer, (0, 0), self.drawlayer)


class DEMOSCRIPT_ELEMENT(object):

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def at_start(self):
        pass

    def at_end(self):
        pass

    def run(self, count, gravity):
        pass

    def step(self, counter, gravity):

        if counter < self.start:
            return
        if counter > self.end:
            return

        if counter == self.start:
            self.at_start()

        self.run(counter-self.start, gravity)

        if counter == self.end:
            self.at_end()


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

        self.freeflies = []

        self.demo_elements = []
        self.demo_counter = 0

        super(LEDCube, self).__init__(*args, **kwargs)

    def getSquare(self, name):

        for s in self.squares:
            if s.name == name:
                return s

        return None

    def reset(self):
        for n in LEDCube.sidedata:
            s = Square(n, self)
            self.squares.append(s)

    def moveflies(self):

        for ff in self.freeflies:
            ff.move(self)

    def run(self):

        image = Image.new("RGB", (96, 64))

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

            for e in self.demo_elements:
                e.step(self.demo_counter, gravity)

            for i in range(0, 3):
                for j in range(0, 2):
                    s = self.squares[j*3+i]

                    s.draw(gravity)
                    tile = s.image

                    image.paste(tile, (i*32, j*32))

            self.matrix.SetImage(image)

            self.demo_counter += 1
            print self.demo_counter



# Main function
if __name__ == "__main__":
    sys.argv += ["--led-chain", "3", "--led-parallel", "2", "--led-brightness", "75", "--led-slowdown-gpio", "2"]
    DEMO_CUBE = LEDCube()
    import demoscript
    demoscript.assamble_demo(DEMO_CUBE)
    if (not DEMO_CUBE.process()):
        DEMO_CUBE.print_help()