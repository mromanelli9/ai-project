#!/usr/bin/env python
## -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: t; tab-width: 4; coding: utf-8; -*-
#title           : utils.py
#description     : Provides some utilities widely used by other modules.
#author          : Marco Romanelli
#date            : 12/05/2017
#version         : 1
#python_version  : 3.6.0
#==============================================================================

import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QPen, QPainter
from PyQt5 import QtCore
from os.path import split, splitext, basename, join
import sys

def splitFilename(filepath):
	"""
	Split a filepath into path, name and extension
	"""

	path, filename = split( filepath )
	name, ext = splitext( basename( filename ) )

	return path, name, ext

def displayImage(source, destination=None, surplus=None):
	"""
	Display an image in a window.
	The window automatically fits to the image size.
	"""

	# if no destinaton file is provided...
	if destination == None or destination == "":
		if surplus == None:
			surplus = "_new"

		path, name, ext = splitFilename( source )

		# Compute destination filename
		destination = join( path, name + surplus + ext)


	app = QApplication( sys.argv )
	ex = App( source )
	app.exec_()

	return ex


class App(QWidget):
	"""
	Display an image using PyQt5
	"""

	def __init__(self, source, title=None):
		super().__init__()
		self.source = source

		if title == None:
			_, name, _ = splitFilename( source )
			self.title = name
		else:
			self.title = title

		self.left = 10
		self.top = 10
		self.width = 640
		self.height = 480
		self.initUI()

	def initUI(self):
		self.setWindowTitle( self.title )
		self.setGeometry( self.left, self.top, self.width, self.height )

		# Create widget
		label = QLabel( self )
		self.pixmap = QPixmap( self.source )
		label.setPixmap( self.pixmap )
		self.resize( self.pixmap.width(), self.pixmap.height() )

		self.show()

	def drawRectangle( self, p1, p2 ):
		x1, y1 = p1
		x2, y2 = p2

		# create painter instance with pixmap
		self.painterInstance = QPainter( self.pixmap )

		# set rectangle color and thickness
		self.penRectangle = QPen( QtCore.Qt.red )
		self.penRedBorder.setWidth( 3 )

		# draw rectangle on painter
		self.painterInstance.setPen( self.penRectangle )
		self.painterInstance.drawRect( x1, y1, x2-x1, y2-y1 )

		# set pixmap onto the label widget
		self.ui.label_imageDisplay.setPixmap( self.pixmap )
		self.ui.label_imageDisplay.show()
