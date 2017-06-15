#!/usr/bin/env python
## -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: t; tab-width: 4; coding: utf-8; -*-
#title           : CVImage.py
#description     : Read, open and modify an image using OpenCV 3
#					http://docs.opencv.org/3.0-beta/
#author          : Marco Romanelli
#date            : 14/06/2017
#version         : 1
#python_version  : 3.6.0
#==============================================================================

from utils.utils import splitFilename, isInRegion
from os.path import join as os_join
import cv2 as cv

class CVImage():
		"""
		Display an image using OpenCV 3
		"""

		__source = None
		__image = None
		__width = None
		__height = None
		__title = None

		id = None
		__class_counter = 0

		# Colors
		BGR_COLOR_BLUE = (255, 0, 0)
		BGR_COLOR_YELLOW = (0, 255, 255)
		BGR_COLOR_RED = (0, 0, 255)
		BGR_COLOR_GREEN = (0, 255, 0)
		BGR_COLOR_BLACK = (0, 0, 0)
		BGR_COLOR_WHITE = (255, 255, 255)

		def __init__( self, source, title=None ):
			self.id = CVImage.__class_counter
			CVImage.__class_counter += 1

			if title == None:
				_, name, _ = splitFilename( source )
				self.__title = name
			else:
				self.__title = title

			self.__source = source

			# Create window
			cv.namedWindow( "image", cv.WINDOW_NORMAL )

			# Loads image as such including alpha channel
			self.__image = cv.imread( self.__source, cv.IMREAD_UNCHANGED )

			# Check if the image has been loaded correctly
			assert self.__image is not None, "[!] Error occured while loading the image \"%s\": image is None" % self.__source

			# Get dimensions
			self.__height, self.__width = self.__image.shape[:2]


		def showImage( self ):
			# Resize the image
			self.__image = cv.resize( self.__image, (self.__width, self.__height))

			# Show image
			cv.imshow( self.__title, self.__image )

			# Display the image infinitely until any keypress
			k = cv.waitKey( 0 ) & 0xFF		# fix for 64-bit machines

			if k == 27:
				# wait for ESC key to exit
				pass
			elif k == ord('s'):
				# wait for 's' key to save and exit
				path, name, ext = splitFilename( self.__source )

				out_name = name + "_out" + ext

				cv.imwrite( os_join( path, out_name ), self.__image )

			# Destroy all the windows that has been created
			cv.destroyAllWindows()

		def drawRectangle( self, p1, p2, color=BGR_COLOR_YELLOW, thickness=1 ):
			"""
			Draw a rectangle given two point p1=(x1, y1) and p2=(x2, y2) such that:
				p1 ---------------- +
				|					|			x1 <= x2
				|					|			y1 >= y2
				|					|
				+ ----------------- p2
			"""

			x1, y1 = p1
			x2, y2 = p2

			# Check if the two points are admissibles
			assert isInRegion( (self.__width, self.__height), p1 ), "[!] Error: (%d,%d) is not a feasibile point of the image." % p1
			assert isInRegion( (self.__width, self.__height), p2 ), "[!] Error: (%d,%d) is not a feasibile point of the image." % p2

			if (x1 > x2 ) and ( y1 < y2 ):
				t = p2
				p2 = p1
				p1 = t

				x1, y1 = p1
				x2, y2 = p2

			# Draw
			cv.rectangle( self.__image, p1, p2, color, thickness )


		def drawPoint( self, p1, color=BGR_COLOR_YELLOW, thickness=1 ):
			"""
			Draw a point
			"""

			# Check if the point is admissible
			assert isInRegion( (self.__width, self.__height), p1 ), "[!] Error: (%d,%d) is not a feasibile point of the image." % p1

			# Draw
			cv.line( self.__image, p1, p1, color, thickness )


		def drawData( self, data ):
			"""
			Draw multiple figures. Data format example:
			Data = {
					"rectangle" : {
								"data" : [((148, 646), (237, 557))],
								"color" : CVImage.BGR_COLOR_YELLOW,
								"thickness" : 2
					},
					"point" : {
						"data" : [(200, 200)],
						"color" : CVImage.BGR_COLOR_YELLOW,
						"thickness" : 5
					}
				}
			"""

			# Loop
			for key in data.keys():
				assert (key == "rectangle") or (key == "point"), "[!] Error: data not valid."

				# If rectangles
				if key == "rectangle":
					d = data["rectangle"]
					color = d["color"]
					tn = int( d["thickness"] )

					for el  in d["data"]:
						p1, p2 = el
						self.drawRectangle( p1, p2, color, tn )

				# If point
				if key == "point":
					d = data["point"]
					color = d["color"]
					tn = int( d["thickness"] )

					for p in d["data"]:
						self.drawPoint( p, color, tn )


		def printInfo( self ):
			print( " ----------------- " )
			print( " Id: %d " % self.id )
			print( " Source: %s " % self.__source )
			print( " Title: %s " % self.__title )
			print( " Width: %s " % self.__width )
			print( " Height: %s " % self.__height )
			print( " ----------------- " )


		def getWidth( self ):
			return self.__width


		def getHeight( self ):
			return self.__height
