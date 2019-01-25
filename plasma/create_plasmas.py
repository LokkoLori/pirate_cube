"""Creates a couple of 2-dimensional functions and saves them
in raw files 'sin_hyp.raw' and 'sin_cos.raw'.
"""

from math import sin, cos, hypot

W, H = 640, 480

sh = ''
sc = ''
for y in range(H):
    for x in range(W):
        hyp = hypot(H / 2 - y, W / 2 - x)
        # These functions are copied for the most part identical
        # to the functions from the original source.
        sh += chr(int(64 + 63 * sin(hyp / 16.0)))
        sc += chr( int( 63 * sin(x / (37 + 15 * cos(y / 74.0))) *
                    cos(y / (31 + 11 * sin(x / 57.0))) + 64 ) )
print len(sh) + len(sc)
sin_hyp_file = file('sin_hyp.raw', 'wb')
sin_hyp_file.write(sh)
sin_hyp_file.close()
sin_cos_file = file('sin_cos.raw', 'wb')
sin_cos_file.write(sc)
sin_cos_file.close()
