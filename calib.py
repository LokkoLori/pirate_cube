import json
import numpy
import math
import time
import sys

try:
    from accelero import get_pure_accelero
except Exception as e:
    pass

def measrun():

    v = [0,0,0]
    mc = 100
    for i in range(0, mc):
        m = get_pure_accelero()
        v[0] += m[0]
        v[1] += m[1]
        v[2] += m[2]

    v[0] = v[0] / mc
    v[1] = v[1] / mc
    v[2] = v[2] / mc

    return v

def measure_still():

    sides = ["Le", "Ba", "Do", "Ri", "Fr", "Up", "LeBaDo", "RiFrUp"]

    vs = {}
    for s in sides:
        print s
        time.sleep(5)
        v = measrun()
        print v
        vs[s] = v

    with open("accel.json", "w") as f:
        json.dump(vs, f)

Sides = ["Le", "Ri", "Ba", "Fr", "Do", "Up", "LeBaDo", "RiFrUp"]

d = 1 / math.sqrt(3)

TV = {
    "Le": [1.0, 0.0, 0.0],
    "Ri": [-1.0, 0.0, 0.0],
    "Ba": [0.0, 1.0, 0.0],
    "Fr": [0.0, -1.0, 0.0],
    "Do": [0.0, 0.0, 1.0],
    "Up": [0.0, 0.0, -1.0],
    "LeBaDo": [d, d, d],
    "RiFrUp": [-d, -d, -d]
}

def transform():

    with open("accel.json") as f:
        vs = json.load(f)

    am = []
    bm = []
    for s in Sides:
        l = [1.0*v for v in vs[s]]
        am.append([1.0*v for v in vs[s]])
        bm.append([1.0*v for v in TV[s]])

    Y = numpy.matrix(am)
    X = numpy.matrix(bm)

    A1 = numpy.linalg.lstsq(Y,X)[0]

    t = numpy.matmul(am[0], A1)
    print t
    t = numpy.matmul(am[1], A1)
    print t
    t = numpy.matmul(am[2], A1)
    print t
    t = numpy.matmul(am[3], A1)
    print t
    t = numpy.matmul(am[4], A1)
    print t
    t = numpy.matmul(am[5], A1)
    print t
    t = numpy.matmul(am[6], A1)
    print t
    t = numpy.matmul(am[7], A1)
    print t

    arotm = []
    for i in range(0, len(A1)):
        row = numpy.array(A1[i]).tolist()[0]
        arotm.append(row)

    with open("rotm.json", "w") as f:
        json.dump(arotm, f)



if __name__ == "__main__":
    if "-m" in sys.argv:
        measure_still()
    transform()



