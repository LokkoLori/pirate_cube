import plasma
import random
import colorsys
import sys

from PIL import Image

DEMO_CUBE = None
Le = None
Ba = None
Ri = None
Up = None
Fr = None
Do = None


class MATRIXSHOW(plasma.DEMOSCRIPT_ELEMENT):

    def __init__(self, squares, framedrop, stopbbeforend, start, end):
        super(MATRIXSHOW, self).__init__(start, end)
        self.squares = squares
        self.framedrop = framedrop
        self.stopbbeforend = stopbbeforend

    def at_start(self):
        for s in self.squares:
            s.matrix_shown = True
            s.matrix_dropping = True
            s.matrix_framedrop = self.framedrop

    def run(self, count, gravity):
        if self.length - self.stopbbeforend < count:
            for s in self.squares:
                s.matrix_dropping = False

    def at_end(self):
        for s in self.squares:
            s.matrix_shown = False

class SCROLLER(plasma.DEMOSCRIPT_ELEMENT):

    def __init__(self, text, speed, y, font, start, end):
        super(SCROLLER, self).__init__(start, end)
        self.text = text
        self.speed = speed
        self.y = y
        self.font = font
        self.text1 = [self.text, 0, self.y, self.font]
        self.text2 = [self.text, 0, self.y, self.font]
        self.text3 = [self.text, 0, self.y, self.font]

    def at_start(self):
        Ri.texts.append(self.text1)
        Ba.texts.append(self.text2)
        Le.texts.append(self.text3)


    def run(self, count, gravity):

        offs = 32
        self.text1[1] = offs - int(count * self.speed)
        offs += 32
        self.text2[1] = offs - int(count * self.speed)
        offs += 32
        self.text3[1] = offs - int(count * self.speed)

    def at_end(self):
        Ri.texts.remove(self.text1)
        Ba.texts.remove(self.text2)
        Le.texts.remove(self.text3)

class SHOW_IMAGE(plasma.DEMOSCRIPT_ELEMENT):

    def __init__(self, squares, fn, x, y, blend, start, end):
        super(SHOW_IMAGE, self).__init__(start, end)
        self.image = Image.open(fn)
        self.squares = squares
        self.x = x
        self.y = y
        self.blend = blend

    def at_start(self):

        for s in self.squares:
            s.images_shown.append([self.image, self.x, self.y, self.blend, self])

    def at_end(self):

        for s in self.squares:
            s.images_shown = [_ for _ in s.images_shown if _[4] != self]



class STARSFIELD(plasma.DEMOSCRIPT_ELEMENT):

    def __init__(self, start, end):
        super(STARSFIELD, self).__init__(start, end)


    def at_start(self):


        stars = []

        #Le
        for i in range(0, 10):
            grey = random.randint(64, 255)
            stars.append(plasma.FreeFly(
                color=(grey, grey, grey, 255),
                loc=[0, random.uniform(0, 31), random.uniform(0, 31)]
            ))
        #Ba
        for i in range(0, 10):
            grey = random.randint(64, 255)
            stars.append(plasma.FreeFly(
                color=(grey, grey, grey, 255),
                loc=[random.uniform(0, 31), 0, random.uniform(0,31)]
            ))
        #Ri
        for i in range(0, 10):
            grey = random.randint(64, 255)
            stars.append(plasma.FreeFly(
                color=(grey, grey, grey, 255),
                loc=[32, random.uniform(0, 31), random.uniform(0,31)]
            ))
        #Fr
        for i in range(0, 10):
            grey = random.randint(64, 255)
            stars.append(plasma.FreeFly(
                color=(grey, grey, grey, 255),
                loc=[0, random.uniform(0,31), random.uniform(0,31)]
            ))

        DEMO_CUBE.freeflies += stars

        for ff in DEMO_CUBE.freeflies:
            ff.blinking = False

            M = 0.075
            D = 0.0025
            if ff.onSquare(Le):
                ff.vel[1] = M + random.uniform(0,D * ff.color[0])
            elif ff.onSquare(Ba):
                ff.vel[0] = -M - random.uniform(0,D * ff.color[0])
            elif ff.onSquare(Ri):
                ff.vel[1] = -M - random.uniform(0,D * ff.color[0])
            elif ff.onSquare(Fr):
                ff.vel[0] = M + random.uniform(0,D * ff.color[0])

        sides = [Le, Ba, Ri, Fr]
        for s in sides:
            s.flies_shown = True

    def run(self, count, gravity):

        DEMO_CUBE.moveflies()

    def at_end(self):
        sides = [Le, Ba, Ri, Fr]
        for s in sides:
            s.flies_shown = False


class PAINT_STARS(plasma.DEMOSCRIPT_ELEMENT):

    def __init__(self, start, end):
        super(PAINT_STARS, self).__init__(start, end)
        self.stari = 0
        self.wait = 2
        self.hue = 0.1

    def at_start(self):

        sides = [Le, Ba, Ri, Fr]
        for s in sides:
            s.flies_shown = True

    def run(self, count, gravity):

        if count % self.wait == 0:
            if self.stari < len(DEMO_CUBE.freeflies):
                ff = DEMO_CUBE.freeflies[self.stari]

                self.hue += 1.0 / len(DEMO_CUBE.freeflies)
                rgb = list(colorsys.hsv_to_rgb(self.hue, 1, 1))
                rgb.append(1)
                ff.color = tuple([int(round(c * 255.0)) for c in rgb])

                self.stari += 1

        DEMO_CUBE.moveflies()

    def at_end(self):
        sides = [Le, Ba, Ri, Fr]
        for s in sides:
            s.flies_shown = False


class FIREFLY_DANCE(plasma.DEMOSCRIPT_ELEMENT):

    def __init__(self, lurk, start, end):
        super(FIREFLY_DANCE, self).__init__(start, end)
        self.lurk = lurk

    def at_start(self):

        sides = [Up, Le, Ba, Ri, Fr]
        for s in sides:
            s.flies_shown = True
            s.fly_tails_faded = True
            s.flies_diffblended = True


    def run(self, count, gravity):


        for ff in DEMO_CUBE.freeflies:

            square = None
            for s in DEMO_CUBE.squares:
                if ff.onSquare(s):
                    square = s
                    break

            if not square:
                continue

            stick_coord = square.getStickCoord()

            D = - 0.0000003

            sgrav = list(gravity)

            sgrav[0] = D * gravity[0]
            sgrav[1] = D * gravity[1]
            sgrav[2] = - D * gravity[2]

            for coi in range(0, 3):
                if coi != stick_coord:
                    ff.vel[coi] += random.uniform(-self.lurk, self.lurk) + sgrav[coi]

                ff.vel[coi] *= 0.998

                if ff.vel[coi] > 0.5:
                    ff.vel[coi] = 0.5
                elif ff.vel[coi] < -0.5:
                    ff.vel[coi] = -0.5

            firstonsqare = None

            for other in square.owner.freeflies:
                if other == ff or not other.onSquare(square):
                    continue

                firstonsqare = other
                break

            if firstonsqare:
                for v in range(0, 3):
                    ff.vel[v] += 0.001 * (firstonsqare.vel[v] - ff.vel[v])
                    ff.vel[v] += 0.001 * (firstonsqare.loc[v] - ff.loc[v])

        DEMO_CUBE.moveflies()


    def at_end(self):
        sides = [Up, Le, Ba, Ri, Fr]
        for s in sides:
            s.flies_shown = False


class PLASMA(plasma.DEMOSCRIPT_ELEMENT):

    def __init__(self, speed, start, end):
        super(PLASMA, self).__init__(start, end)
        self.speed = speed
        self.offset = [0,0,0]

    def run(self, count, gravity):

        self.offset[0] += -self.speed * gravity[0]
        self.offset[1] += -self.speed * gravity[1]
        self.offset[2] += self.speed * gravity[2]

        sides = [Up, Le, Ba, Ri, Fr]
        for s in sides:
            s.plasma_offset = self.offset

    def at_start(self):

        sides = [Up, Le, Ba, Ri, Fr]
        for s in sides:
            s.plasma_shown = True


    def at_end(self):
        sides = [Up, Le, Ba, Ri, Fr]
        for s in sides:
            s.plasma_shown = False



class SWITCH(plasma.DEMOSCRIPT_ELEMENT):
    def __init__(self, switchdef, start, end):
        super(SWITCH, self).__init__(start, end)
        self.switchdef = switchdef

    def at_start(self):

        self.switchdef()

def assamble_demo(cube):

    global DEMO_CUBE
    DEMO_CUBE = cube
    global Le
    Le = DEMO_CUBE.getSquare("Le")
    global Ba
    Ba = DEMO_CUBE.getSquare("Ba")
    global Ri
    Ri = DEMO_CUBE.getSquare("Ri")
    global Up
    Up = DEMO_CUBE.getSquare("Up")
    global Fr
    Fr = DEMO_CUBE.getSquare("Fr")
    global Do
    Do = DEMO_CUBE.getSquare("Do")

    start = 0
    DEMO_CUBE.demo_counter = start

    def createbugs():

        if DEMO_CUBE.freeflies:
            return

        n = 40
        hue = 0
        for i in range(0, n):
            hue += 1.0 / n
            rgb = list(colorsys.hsv_to_rgb(hue, 1, 1))
            rgb.append(1)
            DEMO_CUBE.freeflies.append(plasma.FreeFly(
                color=tuple([int(round(c * 255.0)) for c in rgb]),
                loc=[random.uniform(0, 31), random.uniform(0, 31), 32]
            ))

    cube.demo_elements.append(MATRIXSHOW([Le, Ba, Ri, Fr], 5, 300, 0, 1700))
    cube.demo_elements.append(SCROLLER("                              WHAT IF I TOLD YOU, THIS CUBE IS A DEMO PLATFORM?", 0.3, 15, plasma.s15font, 0, 1700))
    cube.demo_elements.append(SHOW_IMAGE([Ba], "wface1.png", 0, 0, "", 1700, 1750))
    cube.demo_elements.append(SHOW_IMAGE([Ba], "wface2.png", 0, 0, "", 1750, 1770))
    cube.demo_elements.append(SHOW_IMAGE([Ba], "wface1.png", 0, 0, "", 1770, 1820))
    cube.demo_elements.append(SHOW_IMAGE([Ba], "wface2.png", 0, 0, "", 1820, 1840))
    cube.demo_elements.append(SHOW_IMAGE([Ba], "wface1.png", 0, 0, "", 1840, 1890))
    cube.demo_elements.append(SHOW_IMAGE([Ba], "wface3.png", 0, 0, "", 1890, 2100))
    cube.demo_elements.append(STARSFIELD(2100, 3100))
    cube.demo_elements.append(SCROLLER("              AHWWW ... SCROLLING STARS, HUH? ... REALLY?!! ... ITS BOOOOOORING !!!", 0.5, 15, plasma.s15font, 2100, 3200))
    cube.demo_elements.append(PAINT_STARS(3100, 4000))
    cube.demo_elements.append(SCROLLER("    BRRRRR ... COLORED STARS? ... IS IT ALL YOUV GOT?", 0.5, 15, plasma.s15font, 3200, 4000))
    cube.demo_elements.append(FIREFLY_DANCE(0.1, 4000, 6050))
    cube.demo_elements.append(SCROLLER("                      WOOOOOW ... DANCING COLOR BUGS!", 1, 15, plasma.s15font, 4000, 4500))

    def switchtoblur():
        for s in [Le, Ba, Ri, Fr, Up]:
            s.fly_tails_faded = False
            s.fly_tails_blurred = True

    cube.demo_elements.append(SWITCH(switchtoblur, 4500, 4501))
    cube.demo_elements.append(SCROLLER("        ARE THEY FARTING FOG?  ...   EVEN BETTER!        OKAY, SAY SOME WORDS ABOUT THE HARDWARE!        THE CUBE HAS 6 LED PANELS ON EACH SIDES WITH 32x32 PIXELS ON THEM  ...  POWERD BY A RASBERRY PI INSIDE        AND WHAT ELSE IT CAN DO SO???", 1, 15, plasma.s15font, 4500, 6049))

    cube.demo_elements.append(PLASMA(0.00003, 6050, 6600))
    cube.demo_elements.append(SWITCH(createbugs, 6050, 6051))
    cube.demo_elements.append(SHOW_IMAGE([Up, Le, Ba, Ri, Fr], "qcube.png", 0, 0, "", 6050, 6100))
    cube.demo_elements.append(SHOW_IMAGE([Up, Le, Ba, Ri, Fr], "qcube.png", 0, 0, "", 6105, 6110))
    cube.demo_elements.append(SHOW_IMAGE([Up, Le, Ba, Ri, Fr], "qcube.png", 0, 0, "", 6115, 6120))
    cube.demo_elements.append(SHOW_IMAGE([Up, Le, Ba, Ri, Fr], "qcube.png", 0, 0, "", 6125, 6130))

    def switchtdiffedon():
        print "switchon"
        for s in [Le, Ba, Ri, Fr, Up]:
            s.drawdiffed = True

    def switchtdiffedoff():
        for s in [Le, Ba, Ri, Fr, Up]:
            s.drawdiffed = False

    cube.demo_elements.append(SWITCH(switchtdiffedon, 6131, 6131))
    cube.demo_elements.append(SCROLLER("ITS PLASMAAAAAAAAAAA ! ! !", 1, 15, plasma.s15font, 6130, 6400))
    cube.demo_elements.append(SWITCH(switchtdiffedoff, 6400, 6401))
    cube.demo_elements.append(SHOW_IMAGE([Up, Le, Ba, Ri, Fr], "ccube.png", 0, 0, "", 6480, 6481))
    cube.demo_elements.append(SHOW_IMAGE([Up, Le, Ba, Ri, Fr], "ccube.png", 0, 0, "", 6490, 6492))
    cube.demo_elements.append(SHOW_IMAGE([Up, Le, Ba, Ri, Fr], "ccube.png", 0, 0, "", 6496, 6498))
    cube.demo_elements.append(FIREFLY_DANCE(0.1, 6500, 7600))

    def killbugs():
        n = 0
        ffs = []
        for ff in DEMO_CUBE.freeflies:
            if not (n % 2 == 0):
                ffs.append(ff)
            n += 1

        DEMO_CUBE.freeflies = ffs

    cube.demo_elements.append(SWITCH(switchtoblur, 6500, 6501))
    cube.demo_elements.append(SWITCH(killbugs, 6500, 6501))
    cube.demo_elements.append(SHOW_IMAGE([Up, Le, Ba, Ri, Fr], "ccube.png", 0, 0, "", 6500, 6600))

    cube.demo_elements.append(MATRIXSHOW([Le, Ba, Ri, Fr], 2, 200, 6600, 7600))
    cube.demo_elements.append(SWITCH(createbugs, 6600, 6601))
    cube.demo_elements.append(SWITCH(killbugs, 6601, 6602))

    cube.demo_elements.append(SCROLLER("CREATED BY LOKKO LORI         KUDOS TO PIRATEGAMES.HU    AND TO NNG       HAVE A GOOD", 1, 15, plasma.s15font, 6650, 7500))
    cube.demo_elements.append(SHOW_IMAGE([Ba], "function.png", 0, 0, "", 7230, 7300))
    cube.demo_elements.append(SHOW_IMAGE([Ba], "funk.png", 0, 0, "", 7300, 7320))
    cube.demo_elements.append(SHOW_IMAGE([Ba], "sun.png", 0, 0, "", 7320, 7340))

    cube.demo_elements.append(SHOW_IMAGE([Ba], "function.png", 0, 0, "", 7340, 7580))
    cube.demo_elements.append(SHOW_IMAGE([Ba], "funk.png", 0, 0, "", 7580, 7590))
    cube.demo_elements.append(SHOW_IMAGE([Ba], "sun.png", 0, 0, "", 7590, 7600))

    def exitdemo():
        sys.exit(0)

    cube.demo_elements.append(SWITCH(exitdemo, 7601, 7602))