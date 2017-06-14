#!/usr/bin/env python
## -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: t; tab-width: 4; coding: utf-8; -*-
#title           : utils.py
#description     : Provides some utilities widely used by other modules.
#author          : Marco Romanelli
#date            : 14/06/2017
#version         : 1
#python_version  : 3.6.0
#==============================================================================

import numpy as np
from os.path import split, splitext, basename, join
import sys

def splitFilename(filepath):
	"""
	Split a filepath into path, name and extension
	"""

	path, filename = split( filepath )
	name, ext = splitext( basename( filename ) )

	return path, name, ext
