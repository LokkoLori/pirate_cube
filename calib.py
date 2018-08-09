import json
import numpy as np
import math
import time

#from accelero import get_accelvector


def measrun():

    v = [0,0,0]
    mc = 100
    for i in range(0, mc):
        m = get_accelvector()
        v[0] += m[0]
        v[1] += m[1]
        v[2] += m[2]

    v[0] = v[0] / mc
    v[1] = v[1] / mc
    v[2] = v[2] / mc

    return v

def measure_still():

    sides = ["Up", "Ri", "Ba"]

    vs = []
    for s in sides:
        print s
        time.sleep(5)
        v = measrun()
        print v
        vs.append(v)

    with open("accel.json", "w") as f:
        json.dump(vs, f)

def transform():

    with open("accel.json") as f:
        vs = json.load(f)

    for v in vs:
        print v

        x, y, z = v
        l = math.sqrt(x*x + y*y + z*z)

        print l

        x = x / l
        y = y / l
        z = z / l

        print "coord {}, {}, {}".format(x, y, z)

        v[0] = x
        v[1] = y
        v[2] = z


    zrot = math.atan(vs[0][1]/vs[0][0])
    yrot = np.pi/2 - math.atan(vs[0][2]/math.sqrt(vs[0][0]*vs[0][0]+vs[0][1]*vs[0][1]))

    #wild guess
    z2rot = np.pi/2

    print "rot : {}, {}".format(zrot, yrot)

    zrotm = [
        [math.cos(zrot), -math.sin(zrot), 0],
        [math.sin(zrot), math.cos(zrot), 0],
        [0, 0, 1]
    ]

    for v in vs:

        vr = np.matmul(v, zrotm)

        v[0] = vr[0]
        v[1] = vr[1]
        v[2] = vr[2]

        print "zrot coord {}, {}, {}".format(v[0], v[1], v[2])

    yrotm = [
        [math.cos(yrot), 0, math.sin(yrot)],
        [0, 1, 0],
        [-math.sin(yrot), 0, math.cos(yrot)]
    ]

    for v in vs:
        vr = np.matmul(v, yrotm)

        v[0] = vr[0]
        v[1] = vr[1]
        v[2] = vr[2]

        print "yrot coord {}, {}, {}".format(v[0], v[1], v[2])

    z2rotm = [
        [math.cos(z2rot), -math.sin(z2rot), 0],
        [math.sin(z2rot), math.cos(z2rot), 0],
        [0, 0, 1]
    ]

    for v in vs:
        vr = np.matmul(v, z2rotm)

        v[0] = vr[0]
        v[1] = vr[1]
        v[2] = vr[2]

        print "z2rot coord {}, {}, {}".format(v[0], v[1], v[2])

    arotm = np.matmul(zrotm, yrotm)
    arotm = np.matmul(arotm, z2rotm)

    arotm = list(arotm)
    for i in range(0, len(arotm)):
        arotm[i] = list(arotm[i])

    with open("rotm.json", "w") as f:
        json.dump(arotm, f)

if __name__ == "__main__":
    #measure_still()
    transform()



