#!/usr/bin/env python
## -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: t; tab-width: 4; coding: utf-8; -*-
#title           : test.py
#description     : Used for debug and develpment.
#author          : Marco Romanelli
#date            : 12/05/2017
#version         : 1
#python_version  : 3.6.0
#==============================================================================

from utils import displayImage
import sys

def main(argv):
	displayImage( argv[0] )

if __name__ == "__main__":
	main(sys.argv[1:])
