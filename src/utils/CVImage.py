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

from utils.utils import splitFilename
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

		def __init__( self, source, title=None ):
			self.id = CVImage.__class_counter
			CVImage.__class_counter += 1

			if title == None:
				_, name, _ = splitFilename( source )
				self.__title = name
			else:
				self.__title = title

			self.__source = source

			# Loads image as such including alpha channel
			self.__image = cv.imread( self.__source, cv.IMREAD_UNCHANGED )

			# Check if the image has been loaded correctly
			assert self.__image is not None, "[!] Error occured while loading the image \"%s\": image is None" % self.__source

			# Get dimensions
			self.__height, self.__width = self.__image.shape[:2]


		def showImage( self ):
			# Create window
			cv.namedWindow( "image", cv.WINDOW_NORMAL )

			# Resize the image
			self.__image = cv.resize( self.__image, (self.__width, self.__height))

			# Show image
			cv.imshow( self.__title, self.__image )

			# Display the image infinitely until any keypress
			cv.waitKey( 0 )

			# Destroy all the windows that has been created
			cv.destroyAllWindows()

		def drawRectangle( self, p1, p2 ):
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

			if (x1 > x2 ) and ( y1 < y2 ):
				t = p2
				p2 = p1
				p1 = t

				x1, y1 = p1
				x2, y2 = p2

			print( p1, p2 )

			cv.rectangle( self.__image, p1, p2, (0,255,0), 1 )


		def printInfo( self ):
			print( " ----------------- " )
			print( " Id: %d " % self.id )
			print( " Source: %s " % self.__source )
			print( " Title: %s " % self.__title )
			print( " Width: %s " % self.__width )
			print( " Height: %s " % self.__height )
			print( " ----------------- " )
