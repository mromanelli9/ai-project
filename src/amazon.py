#!/usr/bin/env python
## -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: t; tab-width: 4; coding: utf-8; -*-
#title           : amazon.py
#description     : Uses Amazon Rekognition to analyze an image.
#author          : Marco Romanelli
#date            : 15/06/2017
#version         : 1
#python_version  : 3.6.0
#==============================================================================

import os
import base64
import datetime
import hashlib
import hmac
import json
import sys
import requests
from utils import CVImage

# Key derivation functions
# http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
def sign(key, msg):
	return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def getSignatureKey(key, date_stamp, regionName, serviceName):
	kDate = sign(('AWS4' + key).encode('utf-8'), date_stamp)
	kRegion = sign(kDate, regionName)
	kService = sign(kRegion, serviceName)
	kSigning = sign(kService, 'aws4_request')
	return kSigning


def analyzeImage(source, mode):
	# Read credentials from the environment
	#access_key = os.environ.get('AWS_ACCESS_KEY_ID')
	access_key = "AKIAIFIZSGMD55P254FA"
	#secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
	secret_key = "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"

	# Uncomment this line if you use temporary credentials via STS or similar
	#token = os.environ.get('AWS_SESSION_TOKEN')

	if access_key is None or secret_key is None:
		print('No access key is available.')
		sys.exit()

	# This code shows the v4 request signing process as shown in
	# http://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html

	host = 'rekognition.us-east-1.amazonaws.com'
	endpoint = 'https://rekognition.us-east-1.amazonaws.com'
	service = 'rekognition'

	# Currently, all Rekognition actions require POST requests
	method = 'POST'

	region = 'us-east-1'

	# This defines the service target and sub-service you want to hit
	if mode == 0:
		# We use 'DetectLabels'
		print( "[+] Mode: DetectLabels.")
		amz_target = 'RekognitionService.DetectLabels'
	elif mode == 1:
		# In this case you want to use 'DetectFaces'
		print( "[+] Mode: DetectFaces.")
		amz_target = 'RekognitionService.DetectFaces'

	# Amazon content type - Rekognition expects 1.1 x-amz-json
	content_type = 'application/x-amz-json-1.1'

	# Create a date for headers and the credential string
	now = datetime.datetime.utcnow()
	amz_date = now.strftime('%Y%m%dT%H%M%SZ')
	date_stamp = now.strftime('%Y%m%d') # Date w/o time, used in credential scope

	# Canonical request information
	canonical_uri = '/'
	canonical_querystring = ''
	canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + '\n' + 'x-amz-date:' + amz_date + '\n' + 'x-amz-target:' + amz_target + '\n'

	# list of signed headers
	signed_headers = 'content-type;host;x-amz-date;x-amz-target'

	# Our source image: -
	with open( source, "rb" ) as source_image:
		# source_bytes = base64.b64encode(source_image.read())
		source_bytes = base64.b64encode( source_image.read() )

	base64_string = source_bytes.decode( "utf-8" )

	# here we build the dictionary for our request data
	# that we will convert to JSON
	request_dict = {}
	if mode == 0:
		request_dict = {
			"Attributes": [ "DEFAULT" ],
			"Image": {
				'Bytes': base64_string
			}
		}
	elif mode == 1:
		request_dict = {
			"Image": {
				'Bytes': base64_string
			},
			"MaxLabels": 5,	# Maximum number of labels you want the service to return in the response.
			"MinConfidence" : 75	# Specifies the minimum confidence level for the labels to return.
		}


	# Convert our dict to a JSON string as it will be used as our payload
	request_parameters = json.dumps(request_dict)

	# Generate a hash of our payload for verification by Rekognition
	payload_hash = hashlib.sha256(request_parameters.encode('utf-8')).hexdigest()

	# All of this is
	canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash

	algorithm = 'AWS4-HMAC-SHA256'
	credential_scope = date_stamp + '/' + region + '/' + service + '/' + 'aws4_request'
	string_to_sign = algorithm + '\n' +  amz_date + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()

	signing_key = getSignatureKey(secret_key, date_stamp, region, service)
	signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()

	authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

	headers = { 'Content-Type': content_type,
			'X-Amz-Date': amz_date,
			'X-Amz-Target': amz_target,

			# uncomment this if you uncommented the 'token' line earlier
			#'X-Amz-Security-Token': token,
			'Authorization': authorization_header}

	r = requests.post(endpoint, data=request_parameters, headers=headers)

	# Let's format the JSON string returned from the API for better output
	formatted_text = json.dumps(json.loads(r.text), indent=4, sort_keys=True)

	print('Response code: {}\n'.format(r.status_code))
	print('Response body:\n{}'.format(formatted_text))

	return json.loads(r.text)

def parseDetectFacesResults(data, image_width, image_height):
	dataToRender = {}

	d = data["FaceDetails"]

	list_of_rect = []
	list_of_points = []

	for el in d:
		current = el["BoundingBox"]

		l = int( float( current["Left"] ) * image_width )
		t = int( float( current["Top"] ) * image_height )
		w = int( float( current["Width"] ) * image_width )
		h = int( float( current["Height"] ) * image_height )

		p1 = ( l, t )
		p2 = ( l + w, l + h)

		list_of_rect.append( (p1, p2) )

		for lndm in el["Landmarks"]:
			x = int( float( lndm["X"] ) * image_width )
			y = int( float( lndm["Y"] ) * image_height )
			list_of_points.append( (x,y) )

	new = {
		"data" : list_of_rect,
		"color" : CVImage.BGR_COLOR_YELLOW,
		"thickness" : 2
	}
	dataToRender["rectangle"] = new

	new = {
		"data" : list_of_points,
		"color" : CVImage.BGR_COLOR_YELLOW,
		"thickness" : 5
	}
	dataToRender["point"] = new

	return dataToRender


def main(argv):
	localImage = argv[0]
	mode = (0, 1)[len(argv) >= 2]

	print( "[+] Calling API..." )

	res = analyzeImage( localImage, mode )

	if mode == 1:
		# Load image
		img = CVImage( localImage )

		# Render results
		print( "[+] Rendering data..." )
		renderedRes = parseDetectFacesResults( res, img.getWidth(), img.getHeight() )
		img.drawData( renderedRes )

		# Display image
		print( "[+] Opening image..." )
		img.showImage()

if __name__ == '__main__':
	main(sys.argv[1:])

	print
