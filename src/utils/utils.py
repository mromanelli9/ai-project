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
from PyQt5.QtGui import QIcon, QPixmap
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
		pixmap = QPixmap( self.source )
		label.setPixmap( pixmap )
		self.resize( pixmap.width(), pixmap.height() )

		self.show()
