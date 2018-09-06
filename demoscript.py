import plasma
import random

from PIL import Image

DEMO_CUBE = None
Le = None
Ba = None
Ri = None
Up = None
Fr = None
Do = None

class SCROLLER(plasma.DEMOSCRIPT_ELEMENT):

    def __init__(self, text, start, end):
        super(SCROLLER, self).__init__(start, end)
        self.text = text

    def at_start(self):
        pass


    def run(self, count, gravity):

        sides = [Ri, Ba, Le]

        offs = 32
        for s in sides:
            s.texts = [(self.text, offs - int(count / 2), 10, plasma.s15font)]
            offs += 32

    def at_end(self):

        sides = [Ri, Ba, Le]
        for s in sides:
            s.texts = []


class WONDERING(plasma.DEMOSCRIPT_ELEMENT):

    def __init__(self, start, end):
        super(WONDERING, self).__init__(start, end)

        self.face1 = Image.open("wface1.png")
        self.face2 = Image.open("wface2.png")
        self.face3 = Image.open("wface3.png")

    def at_start(self):
        Ba.images_shown = [[self.face1, 0, 0]]

    def run(self, count, gravity):

        if count == 0:
            return

        if count > self.end - self.start - 350:
            Ba.images_shown = [[self.face3, 0, 0]]
            return

        if count % 120 == 0:
            Ba.images_shown = [[self.face2, 0, 0]]
        if count % 135 == 0:
            Ba.images_shown = [[self.face1, 0, 0]]


    def at_end(self):
        Ba.images_shown = []


class STARSFIELD(plasma.DEMOSCRIPT_ELEMENT):

    def __init__(self, start, end):
        super(STARSFIELD, self).__init__(start, end)


    def at_start(self):

        # fc = 30
        # hue = 0
        # colorflies = True
        # for n in range(0, fc):
        #     if colorflies:
        #         hue += 1.0 / fc
        #         rgb = list(colorsys.hsv_to_rgb(hue, 1, 1))
        #         rgb.append(1)
        #         FreeFly.freeflies.append(FreeFly(
        #             color=tuple([int(round(c * 255.0)) for c in rgb]),
        #             loc=[random.randint(0, 31), random.randint(0, 31), 32],
        #             lurk=0.2
        #         ))
        #     else:
        #         FreeFly.freeflies.append(FreeFly(
        #             color=(255, 255, 255, 255),
        #             loc=[random.randint(0, 31), random.randint(0, 31), 32],
        #             lurk=0.2)
        #         )

        stars = []

        #Le
        for i in range(0, 10):
            grey = random.randint(32, 255)
            stars.append(plasma.FreeFly(
                color=(grey, grey, grey, 255),
                loc=[0, random.uniform(0, 31), random.uniform(0, 31)]
            ))
        #Ba
        for i in range(0, 10):
            grey = random.randint(32, 255)
            stars.append(plasma.FreeFly(
                color=(grey, grey, grey, 255),
                loc=[random.uniform(0, 31), 0, random.uniform(0,31)]
            ))
        #Ri
        for i in range(0, 10):
            grey = random.randint(32, 255)
            stars.append(plasma.FreeFly(
                color=(grey, grey, grey, 255),
                loc=[32, random.uniform(0, 31), random.uniform(0,31)]
            ))
        #Fr
        for i in range(0, 10):
            grey = random.randint(32, 255)
            stars.append(plasma.FreeFly(
                color=(grey, grey, grey, 255),
                loc=[0, random.uniform(0,31), random.uniform(0,31)]
            ))

        DEMO_CUBE.freeflies += stars

        for ff in DEMO_CUBE.freeflies:
            ff.blinking = True

            D = 0.075
            if ff.onSquare(Le):
                ff.vel[1] = D + random.uniform(0,D * 5)
            elif ff.onSquare(Ba):
                ff.vel[0] = -D - random.uniform(0,D * 5)
            elif ff.onSquare(Ri):
                ff.vel[1] = -D - random.uniform(0,D * 5)
            elif ff.onSquare(Fr):
                ff.vel[0] = D + random.uniform(0,D * 5)

        sides = [Up, Le, Ba, Ri, Fr]
        for s in sides:
            s.flies_shown = True

    def run(self, count, gravity):

        DEMO_CUBE.moveflies()

    def at_end(self):
        sides = [Le, Ba, Ri, Fr]
        for s in sides:
            s.flies_shown = False


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

    start = 1600
    DEMO_CUBE.demo_counter = start

    cube.demo_elements.append(SCROLLER("WHAT IF I TOLD YOU, THIS CUBE IS A DEMO PLATFORM?", 0, 800))
    cube.demo_elements.append(WONDERING(720, 1200))
    cube.demo_elements.append(SCROLLER("WHAT IS IT FOR?   CAN IT SHOW STARS?", 1150, 2000))
    cube.demo_elements.append(STARSFIELD(1600, 10000))