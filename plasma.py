import colorsys


from samplebase import SampleBase
import sys
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter
from accelero import get_accelvector
import math
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


class Firefly():

    def __init__(self, maxw, maxh, maxv, lurk, color):

        self.x = random.randint(0, maxw)
        self.y = random.randint(0, maxh)
        self.vx = random.uniform(0, maxv)
        self.vy = random.uniform(0, maxv)
        self.lurk = lurk
        self.color = color

    def draw(self, d):

        env = []
        for ry in range(int(self.y), int(self.y)+2):
            for rx in range(int(self.x), int(self.x)+2):
                dx = math.fabs(self.x - rx)
                dy = math.fabs(self.y - ry)

                dc = (1 - dx) * (1 - dy)

                env.append([rx, ry, dc])

        for e in env:

            fillc = []
            for c in self.color:
                fillc.append(int(e[2]*c))

            #fillc[3] = 255

            d.point((e[0],e[1],e[0],e[1]), fill=tuple(fillc))

        self.vx += random.uniform(-self.lurk, self.lurk)
        self.vy += random.uniform(-self.lurk, self.lurk)

        self.x += self.vx
        self.y += self.vy

        if self.x < 0:
            self.x = 0
            self.vx *= -1

        if self.x > 31:
            self.x = 31
            self.vx *= -1

        if self.y < 0:
            self.y = 0
            self.vy *= -1

        if self.y > 31:
            self.y = 31
            self.vy *= -1

class Square():

    def __init__(self, data, owner):
        self.plasmaimage = Image.new("RGBA", (32, 32))
        self.plasmaimagearr = self.plasmaimage.load()
        self.fliesImage = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        self.fliesImageDraw = ImageDraw.Draw(self.fliesImage, mode="RGBA")
        self.image = Image.new("RGBA", (32, 32))

        self.name = data[0]
        self.coordtrs =  data[1:]
        self.owner = owner
        self.pa = PulseAnim(0.05)
        self.ic = 0
        self.nc = 0

        self.firefiles = []
        for n in range(0, 10):
            hue = random.uniform(0, 1)
            rgb = list(colorsys.hsv_to_rgb(hue, 1, 1))
            rgb.append(1)
            self.firefiles.append(Firefly(32, 32, 0.3, 0.02, tuple([int(round(c * 255.0)) for c in rgb])))
            #self.firefiles.append(Firefly(32, 32, 0.1, 0.00, (255, 255, 255, 255)))

    def draw(self, vect):

        # if self.name not in ["Up", "Ba", "Ri"]:
        #     return


        #PLASMAIMAGE
        o = 2
        huedrifting = False
        satdrifting = False
        valuedrifting = True
        interlaced = [True, True]

        for i in xrange(32/o):
            if interlaced[0] and (i + self.ic) % 2 != 0:
                continue
            for n in xrange(32/o):
                if interlaced[1] and (n + self.nc) % 2 != 0:
                    continue
                ian = [i*o, n*o]
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
                    sat = 0.75

                if valuedrifting:
                    value = (1 - hue) * (0.25 + (math.sin(p * 2) + 1.0) * 0.375)
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



        self.pa.nextpahse()
        self.ic += 1
        if self.ic % 2 == 0:
            self.nc += 1


        self.image = self.plasmaimage.filter(ImageFilter.GaussianBlur())



        #fireflies

        fliesfade = False

        if fliesfade:
            if self.ic % 10 == 0:
                fader = Image.new("RGBA", (32,32))
                fader = Image.blend(fader, self.fliesImage, alpha=0.8)
                self.fliesImage.paste(fader)
                del fader
        else:
            self.fliesImageDraw.rectangle((0,0,31,31), fill=(0,0,0,0))

        for ff in self.firefiles:
            ff.draw(self.fliesImageDraw)

        self.image.paste(self.fliesImage, (0,0), self.fliesImage)



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
    sys.argv += ["--led-chain", "3", "--led-parallel", "2", "--led-brightness", "100", "--led-slowdown-gpio", "2"]
    graphics_test = LEDCube()
    if (not graphics_test.process()):
        graphics_test.print_help()