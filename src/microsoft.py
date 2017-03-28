# -*- coding: utf-8 -*-
#!/usr/bin/env python

from __future__ import print_function
import sys
#sys.path.append("/Users/Marco/anaconda2/lib/python2.7/site-packages")
import time
import requests
import operator
import numpy as np
import pprint
import cv2 as cv

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

def renderResultOnImage( result, img ):
	"""
	Display the obtained results onto the input image
	"""

	canvas = np.zeros((450, 270, 3), np.uint8)
	canvas = cv.imread(img)

	if ("regions" in result) and ("lines" in result["regions"][0]):
		lines = result["regions"][0]["lines"]
		for line in lines:
			coordinates = map(int, line["boundingBox"].split(','))
			top_left = (coordinates[0], coordinates[1])
			bottom_right = (coordinates[0] + coordinates[2], coordinates[1] + coordinates[3])
			cv.rectangle(canvas, top_left, bottom_right, (0,255,0), 1)

	cv.imshow('Result', canvas)
	cv.waitKey(0)
	cv.destroyAllWindows()

def wrapper(mode):
	"""
	Wraps several methods for analyse an image (having in mind the project goal)

	Parameters:
	mode: select the type of operation to perform
		0: Analyze image
		1: OCR
		2: Tag Image

	[Documentation can be found at: https://goo.gl/htwlmc]
	"""

	# define which API endpoint will be used
	operation = None

	# Computer Vision parameters
	params = None

	if mode == 0:
		print("[+] Mode: Analyze Image.")
		operation = "analyze"
		params = {
			"visualFeatures" : "Tags,Categories"
		}
	elif mode == 1:
		print("[+] Mode: OCR.")
		operation = "ocr"
		params = {
			"language": "it",
			"detectOrientation": "true"
		}
	elif mode == 2:
		print("[+] Mode: Tag Image.")
		operation = "tag"
		params = {}
	else:
	 	print("[!] Error: undefined operation.")
		sys.exit(1)

	headers = dict()
	headers["Ocp-Apim-Subscription-Key"] = _key
	headers["Content-Type"] = "application/json"

	json = { "url": _urlImage }
	data = None

	result = processRequest( _url + operation, json, data, headers, params )

	if result is not None:
		print("[+] Results:")
		pp = pprint.PrettyPrinter(indent=2)
		pp.pprint(result)

		if mode == 1:
			renderResultOnImage(result, _localImage)


if __name__ == "__main__":
	_url = "https://westus.api.cognitive.microsoft.com/vision/v1.0/"
	_key = "***REMOVED***"        # my primary key
	_maxNumRetries = 10                                # not used

	_urlImage = "https://cdn.pbrd.co/images/OtNOX1gbi.jpg"
	_localImage = "scontrino.jpg"

	# if there is arguments use them instead of default values
	if len(sys.argv) == 2:
		localImage = str(sys.argv[1])

	# Set parameters and then call the API
	wrapper(2)
