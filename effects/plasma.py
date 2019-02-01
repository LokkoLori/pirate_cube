import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__),".."))
from pixxlcube.cubecore import PiXXLEffect, PiXXLCube
from PIL import ImageFilter, Image
import math
import colorsys

class PlasmaEffect(PiXXLEffect):

    def __init__(self, side):
        super(PlasmaEffect, self).__init__(side)
        self.phase = 0.0
        self.ic = 0
        self.nc = 0
        self.plasma_offset = [0.0, 0.0, 0.0]
        self.plasma_huedrifting = False
        self.plasma_satdrifting = False
        self.plasma_valuedrifting = False
        self.rawimage = Image.new("RGBA", (self.side.res, self.side.res))
        self.rawimagearr = self.rawimage.load()
        self.speed = -0.5

    def draw(self):
        o = 2
        interlaced = [True, True]

        for i in xrange(self.side.res / o):
            if interlaced[0] and (i + self.ic) % 2 != 0:
                continue
            for n in xrange(self.side.res  / o):
                if interlaced[1] and (n + self.nc) % 2 != 0:
                    continue
                ian = [i * o, n * o, 1]
                crs = list(self.plasma_offset)
                for cin in range(0, 3):
                    for din in range(0, 3):
                        crs[cin] += ian[din]*self.side.equMatrix[cin][din]

                x, y, z = crs
                p = self.phase

                hue = math.sin(x * 0.3) + math.cos(y * 0.5) + math.sin(z * 0.25) + math.cos(
                    (x + y + z) * 0.16) + 0.5 * math.sin(p)
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

                #flip y coord before draw dot
                ian[1] = self.side.res - ian[1] - 2

                if o == 1:
                    self.rawimagearr[ian[0], ian[1]] = pix
                elif o == 2:
                    self.rawimagearr[ian[0] + 0, ian[1] + 0] = pix
                    self.rawimagearr[ian[0] + 1, ian[1] + 0] = pix
                    self.rawimagearr[ian[0] + 0, ian[1] + 1] = pix
                    self.rawimagearr[ian[0] + 1, ian[1] + 1] = pix

        self.image = self.rawimage.filter(ImageFilter.GaussianBlur())

        self.phase += 0.02
        self.ic += 1
        if self.ic % 2 == 0:
            self.nc += 1

        self.plasma_offset[0] += self.speed * self.side.cube.gravity[0]
        self.plasma_offset[1] += self.speed * self.side.cube.gravity[1]
        self.plasma_offset[2] += self.speed * self.side.cube.gravity[2]



if __name__ == "__main__":

    cube = PiXXLCube()
    sides = ["Ba", "Up", "Fr", "Le", "Do", "Ri"]
    for s in [cube.getSide(s) for s in sides]:
        s.addEffect(PlasmaEffect)

    cube.run()