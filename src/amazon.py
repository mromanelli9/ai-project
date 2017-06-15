#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import base64
import datetime
import hashlib
import hmac
import json
import sys

import requests
from utils import CVImage, changeCoordinates

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


def analyzeImage(source):
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
	# In this case you want to use 'DetectFaces'
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
	request_dict = {
	 	"Attributes": [ "DEFAULT" ],
		"Image": {
			'Bytes': base64_string
		}
	}

	# If we want to use a S3 oject
	# request_dict = {
	#  	"Attributes": [ "DEFAULT" ],
	# 	"Image": {
	# 		 "S3Object": {
	# 	         "Bucket": "unipd-ia-project",
	# 	         "Name": "face.jpg"
	# 	         # "Version": "Jun 15, 2017 11:34:26 AM"
	# 	      }
	# 	}
	# }

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
		np1 = changeCoordinates( p1, (image_width, image_height) )
		np2 = (np1[0] + w, np1[1] - h )

		list_of_rect.append( (np1, np2) )

		for lndm in el["Landmarks"]:
			x = int( float( lndm["X"] ) * image_width )
			y = int( float( lndm["Y"] ) * image_height )
			np = changeCoordinates( (x, y), (image_width, image_height) )
			list_of_points.append( np )

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

	print( "[+] Calling API..." )

	res = analyzeImage( localImage )

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
