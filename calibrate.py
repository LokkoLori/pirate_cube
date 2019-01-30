from pixxlcube.cubecore import PiXXLSide, PiXXLCube
from PIL import ImageDraw, ImageFont
import os
import math
import sys
import numpy

if os.path.dirname(__file__):
    os.chdir(os.path.dirname(__file__))

arialfont = ImageFont.truetype("arial.ttf", 18)

class CalibratorSide(PiXXLSide):

    def __init__(self, cube, data):
        super(CalibratorSide, self).__init__(cube, data)

    def draw(self):
        d = ImageDraw.Draw(self.image)

        color = self.cube.sideColors.get(self.name, (255, 255, 255))
        d.rectangle((0, 0, self.res-1, self.res-1), fill=(0, 0, 0), outline=color)

        #show name of the side
        d.text((5, 6), self.name, font=arialfont, fill=color)

        #show 2D axies on the side
        r = 3
        #left bottom (origo)
        d.ellipse((0 - r, self.res - 1 - r, 0 + r, self.res - 1 + r), fill=(255, 0, 0))
        #right bottom (x axis)
        d.ellipse((self.res - 1 - r, self.res - 1  - r, self.res - 1 + r, self.res - 1 + r), fill=(0, 255, 0))
        #top left (y axis)
        d.ellipse((0 - r, 0 - r, 0 + r, 0 + r), fill=(0, 0, 255))


        #draw graviti attack point, blue on top red on bottom
        gx, gy, gz = self.getAlignedGravity()

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

        rp2 = self.res*0.5
        px, py = self.coordsRTD(x*rp2 + rp2, y*rp2 + rp2)

        d.ellipse((px-2, py-2, px+2, py+2), fill=fill, outline=(0, 0, 0))


d = 1 / math.sqrt(3)
ExeptedGravityVectors = [
    ["Up", [0.0, 0.0, -1.0]],
    ["Ri", [-1.0, 0.0, 0.0]],
    ["Do", [0.0, 0.0, 1.0]],
    ["Ba", [0.0, 1.0, 0.0]],
    ["Le", [1.0, 0.0, 0.0]],
    ["Fr", [0.0, -1.0, 0.0]],
    ["Le,Ba,Do", [d, d, d]],
    ["Ri,Fr,Up", [-d, -d, -d]]
]

class CalibratorCube(PiXXLCube):

    def __init__(self):
        self.sideColors = {}
        self.measureCounter = 0
        self.measureIndex = -1
        self.measuredVectors = []
        self.measureStart = -300
        self.measureEnd = 200
        self.actMeasure = None
        super(CalibratorCube, self).__init__(CalibratorSide)


    def startMeasure(self):
        self.measureIndex = 0
        self.measureCounter = self.measureStart
        print "measure {} on top".format(ExeptedGravityVectors[self.measureIndex][0])

    def createTMatrix(self):

        am = []
        bm = []
        for i in range(0, len(ExeptedGravityVectors)):
            am.append(self.measuredVectors[i][1])
            bm.append(ExeptedGravityVectors[i][1])


        Y = numpy.matrix(am)
        X = numpy.matrix(bm)

        A1 = numpy.linalg.lstsq(Y, X)[0]

        arotm = []
        for i in range(0, len(A1)):
            row = numpy.array(A1[i]).tolist()[0]
            arotm.append(row)

        self.settings["accelero_tmatrix"] = arotm

        self.savesettings()

    def preDrawHook(self):

        self.sideColors = {}
        if self.measureIndex < 0:
            return

        self.measureCounter += 1

        if self.measureEnd < self.measureCounter:

            #caclulate avarage vector
            self.actMeasure[0] /= self.measureEnd
            self.actMeasure[1] /= self.measureEnd
            self.actMeasure[2] /= self.measureEnd

            self.measureIndex += 1
            self.measureCounter = self.measureStart
            if len(ExeptedGravityVectors) <= self.measureIndex:
                self.measureIndex = -1
                print self.measuredVectors
                self.createTMatrix()
                return
            print "measure {} on top".format(ExeptedGravityVectors[self.measureIndex][0])

        sides, vect = ExeptedGravityVectors[self.measureIndex]
        sidelist = sides.split(",")

        #set for measuring
        color = (0, 255, 0)
        if 0 < self.measureCounter:

            #measuring phase
            if self.measureCounter == 1:
                self.actMeasure = [0.0, 0.0, 0.0]
                self.measuredVectors.append([sides, self.actMeasure])

            #cumulate measured vector
            self.actMeasure[0] += self.raw_accel_vector[0]
            self.actMeasure[1] += self.raw_accel_vector[1]
            self.actMeasure[2] += self.raw_accel_vector[2]
            color = (255, 0, 0)

        for side in sidelist:
            self.sideColors[side] = color



if __name__ == "__main__":
    cube = CalibratorCube()
    if "-m" in sys.argv:
        cube.startMeasure()
    cube.run()