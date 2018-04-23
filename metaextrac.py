from flask import Flask, request, make_response, abort
from flask_restful import Resource, Api
import json
from mimetypes import MimeTypes
import urllib
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

application = Flask(__name__)

#to check status of service
@application.route("/<param>")
def hello(param):
	print ("Request to / with param: " + param)
	return "Service Enabled!...."

#extra metadata from image uploaded
@application.route('/api/v1/mex/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        upfile = request.files.get('photo')
        if upfile:
            return get_metadata(upfile)
    else:
        return "Error, try again!!"

#exif data extractor
def get_metadata(pfile):    
    exif_data = None
    image = None
    image = Image.open(pfile)
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            exif_data[decoded] = value
            print (tag, " - ", value)
    else:
        return "Error while trying read tags"

    
    return "OK"


if __name__ == "__main__":
    application.run()