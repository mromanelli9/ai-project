#!/usr/bin/env python
## -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: t; tab-width: 4; coding: utf-8; -*-
#title           : ibm.py
#description     : Uses IBM Vision Recognition API to analyze an image.
#author          : Marco Romanelli
#date            : 15/06/2017
#version         : 1
#python_version  : 3.6.0
#==============================================================================

import json
from os.path import join, dirname
import sys
from os import environ
from watson_developer_cloud import VisualRecognitionV3
from utils import CVImage

def parseDetectFacesResults(data):
	dataToRender = {}

	d = data["images"][0]["faces"]

	list_of_rect = []

	for el in d:
		current = el["face_location"]

		l = int( current["left"] )
		t = int( current["top"] )
		w = int( current["width"] )
		h = int( current["height"] )

		p1 = ( l, t )
		p2 = ( l + w, t + h )

		list_of_rect.append( (p1, p2) )

	new = {
		"data" : list_of_rect,
		"color" : CVImage.BGR_COLOR_YELLOW,
		"thickness" : 2
	}
	dataToRender["rectangle"] = new

	return dataToRender


def main(argv):
	data = None
	localImage = argv[0]

	print( "[+] Init API." )
	visual_recognition = VisualRecognitionV3( "2016-05-20", api_key=_api_key )

	# Load raw image file into memory
	data = None
	face_path = join( dirname(__file__), localImage )
	fp = open( face_path, "rb" )

	print( "[+] Calling API..." )
	tres = visual_recognition.detect_faces( images_file=fp )
	results = json.dumps( tres, indent=2 )
	print( results )

	# Load image
	img = CVImage( localImage )

	# Render results
	print( "[+] Rendering data..." )
	renderedRes = parseDetectFacesResults( tres )
	img.drawData( renderedRes )

	# Display image
	print( "[+] Opening image..." )
	img.showImage()


if __name__ == "__main__":
	_api_key = "5499a7b475d76e001439ec1f0b37af8d7af9fb64"	# my API key

	# Check argument
	assert len(sys.argv) >= 2, "[!] Argument missing."

	main(sys.argv[1:])

	print
