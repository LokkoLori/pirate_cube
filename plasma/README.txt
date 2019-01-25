8-bit Plasma Effect in Python, version 1.2
C++ code version and data by Alex Champandard.
Ported to python by Sean McKean <smckean at yvn dot com>
This file and plasma.py are placed in the public domain.


Requirements:
Python (http://www.python.org/)
Pygame (http://www.pygame.org/) -- This is included with the distribution.

Type 'python plasma.py' on the command line to run the program.  Add
'-nologo' option if you want to remove the centered text, or change the
SkipLogo variable to True in the global variable section.  From there,
you can also change the screen resolution, screen options, and so on.

Example -- To run in windowed mode at 640x480 pixels, set the variables
like this:
	ScreenSize = ScreenWidth, ScreenHeight = 640, 480
	ScreenFlags = 0

To change the functions displayed, try messing around with the math in
the 'create_plasmas.py' file. Running the script will re-write the files
'sin_hyp.raw' and 'sin_cos.raw'.

CHANGELOG:
v1.2:	Saved 2-dimensional function info in separate "raw" files, for
	faster loading. Also made another option for pygame's
	Surface.blit function (pygame.BLEND_AOF) that adds 8-bit surfaces
	together, and wraps the color value when it goes over 255
	(blit_blend_add_overflow). This allows the quick blending together
        of the surface blits to the screen.


-Sean McKean (asona)
