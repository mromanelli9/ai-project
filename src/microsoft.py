#!/usr/bin/env python
## -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: t; tab-width: 4; coding: utf-8; -*-
#title           : microsoft.py
#description     : Uses Vision API and Face API to analyze an image.
#author          : Marco Romanelli
#date            : 15/06/2017
#version         : 2
#python_version  : 3.6.0
#==============================================================================

from __future__ import print_function
import sys
import time
import requests
import operator
import pprint
from utils import CVImage

def getAPIInfo(mode):
	data = {}

	if mode == 0:
		# Vision API
		data["endpoint"] = "https://westus.api.cognitive.microsoft.com/vision/v1.0/"
		data["key"] = "***REMOVED***" # Vision API key 1

	else:
		# Fase API
		data["endpoint"] = "https://westcentralus.api.cognitive.microsoft.com/face/v1.0/"
		data["key"] = "***REMOVED***" # Vision API key 1

	return data

def processRequest( url, json, data, headers, params ):
	"""
	Helper function to process the request to Cognitive Services (former Project Oxford)

	Parameters:
	json: Used when processing images from its URL. See API Documentation
	data: Used when processing image read from disk. See API Documentation
	headers: Used to pass the key information and the data type request

	[From API tutorial: https://github.com/Microsoft/Cognitive-Vision-Python/]
	"""

	retries = 0
	result = None

	while True:
		response = requests.request( "post", url, json = json, data = data, headers = headers, params = params )

		if response.status_code == 429:
			print( "Message: %s" % ( response.json()["error"]["message"] ) )

			if retries <= _maxNumRetries:
				time.sleep(1)
				retries += 1
				continue
			else:
				print( "Error: failed after retrying!" )
				break

		elif response.status_code == 200 or response.status_code == 201:

			if "content-length" in response.headers and int(response.headers["content-length"]) == 0:
				result = None
			elif "content-type" in response.headers and isinstance(response.headers["content-type"], str):
				if "application/json" in response.headers["content-type"].lower():
					result = response.json() if response.content else None
				elif "image" in response.headers["content-type"].lower():
					result = response.content
		else:
			print( "[!] Error code: %d" % ( response.status_code ) )
			print( "[!] Message: %s" % ( response.json()["message"] ) )

		break

	return result

def analyzeImage(image, mode):
	"""
	Wraps several methods for analyse an image (having in mind the project goal)

	Parameters:
	mode: select the type of operation to perform
		0: Analyze image (Tags and Classification)
		1: OCR

	[Documentation can be found at: https://goo.gl/htwlmc]
	"""

	operation = None	# define which API endpoint will be used
	params = None	# Computer Vision parameters

	if mode == 0:
		print("[+] Mode: Analyze Image.")
		operation = "analyze"
		params = {
			"visualFeatures" : "Tags,Categories,Description",
			"language" : "en"
		}
	elif mode == 1:
		print("[+] Mode: Face Detection.")
		operation = "detect"
		params = {
			"returnFaceId": "true",
			"returnFaceLandmarks": "true",
			"returnFaceAttributes": "age,gender,smile"
		}
	else:
		print("[!] Error: undefined operation.")
		sys.exit(1)

	APIinfo = getAPIInfo(mode)	# Retrieve endpoint and key

	headers = dict()
	headers["Ocp-Apim-Subscription-Key"] = APIinfo["key"]
	headers["Content-Type"] = "application/octet-stream"

	json = None

	# Load raw image file into memory
	with open( image, "rb" ) as f:
		data = f.read()

	print( "[+] API request..." )
	result = processRequest( APIinfo["endpoint"] + operation, json, data, headers, params )

	if result is not None:
		print("[+] Results:")
		pp = pprint.PrettyPrinter(indent=2)
		pp.pprint(result)

		#renderResultOnImage(result, _localImage)

	return result

def parseFaceAPIResults(res):
	dataToRender = {}

	if "faceRectangle" in res.keys():
		d = res["faceRectangle"]

		l = int( d["left"] )
		t = int( d["top"] )
		w = int( d["width"] )
		h = int( d["height"] )

		p1 = ( l, t )
		p2 = ( l + w, t + h )

		new = {
			"data" : [(p1, p2)],
			"color" : CVImage.BGR_COLOR_YELLOW,
			"thickness" : 2
		}
		dataToRender["rectangle"] = new

	if "faceLandmarks" in res.keys():
		d = res["faceLandmarks"]

		points = []
		# Loop over all the landmarks
		for k in d:
			c = d[k]
			p = ( int(c['x']), int(c['y']) )
			points.append(p)

		new = {
			"data" : points,
			"color" : CVImage.BGR_COLOR_YELLOW,
			"thickness" : 5
		}
		dataToRender["point"] = new

	return dataToRender


def main(argv):
	_maxNumRetries = 10                            	# not used

	# Default values
	mode = 0
	localImage = None

	# Check argument
	assert len(argv) >= 1, "[!] Argument missing."

	localImage = str(argv[0])

	if len(argv) >= 2:
		mode = int(argv[1])

	# Set parameters and then call the API
	results = analyzeImage( localImage, mode )

	# Load image
	img = CVImage( localImage )

	if mode == 1:
		for el in results:
			# Parse results
			data = parseFaceAPIResults( el )

			# Render results
			print( "[+] Rendering data..." )
			img.drawData(data)

	# Display image
	print( "[+] Opening image..." )
	img.showImage()


if __name__ == "__main__":
	main(sys.argv[1:])
