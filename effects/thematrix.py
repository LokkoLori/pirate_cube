import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__),".."))
from pixxlcube.cubecore import PiXXLEffect, PiXXLCube
import random

class MatrixEffect(PiXXLEffect):
    def __init__(self, side):
        super(MatrixEffect, self).__init__(side)
        self.matrixImageArr = self.image.load()

        self.matrix = []
        for i in range(0, side.res+2):
            row = []
            self.matrix.append(row)
            for j in range(0, side.res):
                row.append([0, 0.0])

        self.matrix_dropping = True
        self.matrix_framedrop = 5
        self.counter = 0

    def draw(self):

        valmin = 10
        valmax = 70
        dense = 100

        def drawdot(x, y, front=False):

            if y < 1 or self.side.res < y:
                return

            val = self.matrix[y][x]
            if val[0] == 0:
                self.matrixImageArr[x, y - 1] = (0, 0, 0, 0)

            if front:
                g = int(val[1] * 255)
                self.matrixImageArr[x, y - 1] = (g, g, g, 255)
                drawdot(x, y - 1)
            else:
                g = int((val[0] * 1.0) * (1.0 / valmax) * val[1] * 255)
                self.matrixImageArr[x, y - 1] = (0, g, 0, 255)

        if self.counter % self.matrix_framedrop == 0:

            for y in reversed(range(1, self.side.res+2)):
                for x in range(0, self.side.res):
                    me = self.matrix[y][x]
                    ab = self.matrix[y - 1][x]
                    if me[0] < ab[0]:
                        self.matrix[y][x] = [ab[0], random.uniform(0.2, 1)]
                        drawdot(x, y, True)
                    elif 0 < me[0]:
                        me[0] -= 1
                        if me[0] == 0:
                            me[1] = 0.0
                            drawdot(x, y)
                        elif random.randint(0, me[0]) == 0:
                            me[1] = random.uniform(0.2, 1)
                            drawdot(x, y)

            # new drops
            for x in range(0, self.side.res):
                if self.matrix_dropping and random.randint(0, dense) == 0:
                    self.matrix[0][x] = [random.randint(valmin, valmax), random.uniform(0.2, 1)]
                    drawdot(x, 0, True)
                else:
                    val = self.matrix[0][x]
                    if val[0] > 0:
                        val[0] -= 1

        self.counter += 1




if __name__ == "__main__":

    cube = PiXXLCube()
    sides = ["Le", "Ba", "Ri", "Fr"]
    for s in [cube.getSide(s) for s in sides]:
        s.addEffect(MatrixEffect)

    cube.run()