import logodemo
import random
import colorsys
import sys
import pyqrcode
import socket

from PIL import Image

DEMO_CUBE = None
Le = None
Ba = None
Ri = None
Up = None
Fr = None
Do = None


class MATRIXSHOW(logodemo.DEMOSCRIPT_ELEMENT):

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


class SCROLLER(logodemo.DEMOSCRIPT_ELEMENT):

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


class SHOW_IMAGE(logodemo.DEMOSCRIPT_ELEMENT):

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


class SHOW_IP_QR(logodemo.DEMOSCRIPT_ELEMENT):

    def __init__(self, squares, start, end):
        super(SHOW_IP_QR, self).__init__(start, end)
        self.squares = squares
        self.image = None
        self.ip = None
        self.showing = False

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def run(self, count, gravity):
        if count % 20 == 0:
            self.refreshqr()

    def refreshqr(self):

        ip = self.get_ip()
        if self.ip == ip:
            return

        self.ip = ip
        #todo: don't do the magic with png files!!!
        qrc = pyqrcode.create("http://{}:8088".format(self.ip), error="L")
        qrstr = qrc.text()
        qrstrl = qrstr.split('\n')
        i = Image.new("RGB", (len(qrstrl[0]), len(qrstrl)), color=(255, 255, 255, 255))

        qrm = i.load()

        for y in range(0, len(qrstrl)):
            for x in range(0, len(qrstrl[y])):
                if qrstrl[y][x] == "1":
                    qrm[x, y] = (0,0,0)

        bg = Image.new("RGB", (32, 32), color=(255, 255, 255, 255))
        width, heigth = i.size
        topleft = (32 - width) / 2
        bg.paste(i, (topleft, topleft))

        self.removeImage()
        self.image = bg

        if self.showing:
            self.addImage()

    def addImage(self):
        for s in self.squares:
            s.images_shown.append([self.image, 0, 0, "nomask", self])

    def removeImage(self):

        for s in self.squares:
            s.images_shown = [_ for _ in s.images_shown if _[4] != self]

    def at_start(self):

        self.showing = True
        self.refreshqr()


    def at_end(self):

        self.showing = False



class FIREFLY_DANCE(logodemo.DEMOSCRIPT_ELEMENT):

    def __init__(self, lurk, start, end):
        super(FIREFLY_DANCE, self).__init__(start, end)
        self.lurk = lurk

    def at_start(self):

        sides = [Up, Le, Ba, Ri, Fr, Do]
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

            D = 0.003

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
        sides = [Up, Le, Ba, Ri, Fr, Do]
        for s in sides:
            s.flies_shown = False



class SWITCH(logodemo.DEMOSCRIPT_ELEMENT):
    def __init__(self, switchdef, start, end):
        super(SWITCH, self).__init__(start, end)
        self.switchdef = switchdef

    def at_start(self):
        self.switchdef()


LOC = 0


def al(c):
    global LOC
    LOC += c
    return LOC

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

        n = 50
        hue = 0
        for i in range(0, n):
            hue += 1.0 / 40
            rgb = list(colorsys.hsv_to_rgb(hue, 1, 0.5))
            rgb.append(1)
            DEMO_CUBE.freeflies.append(logodemo.FreeFly(
                color=tuple([int(round(c * 255.0)) for c in rgb]),
                loc=[random.uniform(0, 31), random.uniform(0, 31), 32]
            ))

    def switchtoblur():
        for s in [Le, Ba, Ri, Fr, Up, Do]:
            s.fly_tails_faded = False
            s.fly_tails_blurred = True

    cube.demo_elements.append(SWITCH(createbugs, 0, 0))
    cube.demo_elements.append(FIREFLY_DANCE(0.1, 0, -1))
    #cube.demo_elements.append(SWITCH(switchtoblur, 0, 0))
    cube.demo_elements.append(SHOW_IMAGE([Ri, Up, Do], "pixxelcubelogo.png", 0, 0, "", 0, -1))
    cube.demo_elements.append(SHOW_IMAGE([Le, Ba], "pixxelcubename.png", 0, 0, "", 0, -1))


    cube.demo_elements.append(SHOW_IP_QR([Fr], 0, -1))