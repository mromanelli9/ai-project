#!/usr/bin/env python
## -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: t; tab-width: 4; coding: utf-8; -*-
#title           : test.py
#description     : Used for debug and develpment.
#author          : Marco Romanelli
#date            : 14/06/2017
#version         : 1
#python_version  : 3.6.0
#==============================================================================

#from utils import displayImage
from utils import CVImage, isInRegion, changeCoordinates
import sys


def main(argv):
	# displayImage( argv[0] )
	print( "start" )

	img = CVImage( argv[0] )

	w = img.getWidth()
	h = img.getHeight()

	print( "%d x %d" % (w, h) )

	img.drawRectangle( (50, 400), (500, 100), CVImage.BGR_COLOR_YELLOW, 2)

 	img.drawPoint( (500, 500), CVImage.BGR_COLOR_BLACK, 3)

	img.showImage()

	print( "end" )


if __name__ == "__main__":
	main(sys.argv[1:])
