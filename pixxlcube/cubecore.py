import numpy
import accelreader
import json
from PIL import Image
from PIL.Image import ROTATE_90, ROTATE_180, ROTATE_270

from rgbmatrix import RGBMatrix, RGBMatrixOptions


default_cube_settings = {
    "resolution": 32,
    "gpio_slowdown": 3,
    "brightness": 75,
    "chain_length": 3,
    "parallel": 2,
    "sides": [
        {"name": "Ba", "rol": 3, "equ": ["x","0","y"]},
        {"name": "Up", "rol": 3, "equ": ["x","y","1"]},
        {"name": "Fr", "rol": 1, "equ": ["-x","1","y"]},
        {"name": "Ri", "rol": 1, "equ": ["1","x","y"]},
        {"name": "Do", "rol": 0, "equ": ["-x","y","0"]},
        {"name": "Le", "rol": 3, "equ": ["0","-x","y"]}
    ],
    "accelero_tmatrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
}

def load_settings(path=""):
    if not path:
        path = "pixxlsettings.json"

    global default_cube_settings
    try:
        with open(path) as f:
            default_cube_settings = json.load(f)
    except Exception as e:
        pass

load_settings()

class PiXXLSide(object):
    def __init__(self, cube, data):

        self.name = data["name"]
        self.res = data["res"]
        self.rol = data["rol"]
        self.equ = data["equ"]
        self.gavTransM = self.parseEqu()
        self.cube = cube
        self.image = Image.new("RGB", (self.res, self.res))

    def parseEqu(self):
        m = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        for i in range(0,3):
            if self.equ[i] == "x":
                m[i][0] = 1.0
            elif self.equ[i] == "-x":
                m[i][0] = -1.0
            elif self.equ[i] == "y":
                m[i][1] = 1.0
            elif self.equ[i] == "-y":
                m[i][1] = -1.0
            elif self.equ[i] == "1":
                m[i][2] = 1.0
            elif self.equ[i] == "0":
                m[i][2] = -1.0
        return m

    def getAlignedGravity(self):
        return numpy.matmul(self.cube.gravity, self.gavTransM)

    def draw(self):
        pass

    def coordsRTD(self, x, y):
        #raster to descarte coordinates <-- flip y coorditane
        return x, self.res - y

    def alignedDraw(self):

        self.draw()

        if self.rol == 1:
            self.image = self.image.transpose(ROTATE_90)
        elif self.rol == 2:
            self.image = self.image.transpose(ROTATE_180)
        elif self.rol == 3:
            self.image = self.image.transpose(ROTATE_270)

class PiXXLCube(object):
    def __init__(self, sideclass):


        assert issubclass(sideclass, PiXXLSide)
        options = RGBMatrixOptions()

        self.settings = default_cube_settings
        #cube specific defaults:
        options.rows = default_cube_settings["resolution"]
        options.cols = default_cube_settings["resolution"]
        options.chain_length = default_cube_settings["chain_length"]
        options.parallel = default_cube_settings["parallel"]
        options.brightness = default_cube_settings["brightness"]
        options.gpio_slowdown = default_cube_settings["gpio_slowdown"]

        #other led-matrix defaults:
        options.row_address_type = 0
        options.multiplexing = 0
        options.pwm_bits = 11
        options.pwm_lsb_nanoseconds = 130
        options.led_rgb_sequence = "RGB"
        options.pixel_mapper_config = ""
        options.drop_privileges = False

        self.options = options
        self.raw_accel_vector = []
        self.sides = []

        for sidedata in default_cube_settings["sides"]:
            sidedata["res"] = default_cube_settings["resolution"]
            self.sides.append(sideclass(self, sidedata))

        self.image = Image.new("RGB", (self.options.chain_length*self.options.cols, self.options.parallel*self.options.rows))

    def preDrawHook(self):
        pass

    def savesettings(self, path=None):
        if not path:
            path = "pixxlsettings.json"
        with open(path, "w") as f:
            json.dump(self.settings, f, indent=4)

    def run(self):

        try:
            print("Press CTRL-C to stop PiXXL app")
            self.matrix = RGBMatrix(options=self.options)


            while True:

                self.raw_accel_vector = accelreader.read_raw_accel_vector()
                self.gravity = numpy.matmul(self.raw_accel_vector, self.settings["accelero_tmatrix"])
                self.preDrawHook()

                side_index = 0
                for j in range(0, self.options.parallel):
                    for i in range(0, self.options.chain_length):

                        side = self.sides[side_index]
                        side.alignedDraw()
                        self.image.paste(side.image, (i*self.options.cols, j*self.options.rows))
                        side_index += 1

                self.matrix.SetImage(self.image)

        except KeyboardInterrupt:
            print("Exiting\n")