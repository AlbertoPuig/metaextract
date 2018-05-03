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
            mdata = get_metadata(upfile)
            gps_values = get_gpsdata(mdata)
            final_data = formatter(mdata, gps_values)
            return 'OK'
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
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                exif_data[decoded] = gps_data
                #print (tag, " + ", value)
            else:
                #print (tag, " - ", value)
                exif_data[decoded] = value
    else:
        return "Error while trying read tags"

    return exif_data

#trasnform gps data
def get_gpsdata(pmetadata):
    latitude = None
    longitude = None
    gps_data_transf = {}
    if "GPSInfo" in pmetadata:
        gps_info = pmetadata["GPSInfo"]
        gps_latitude = gps_info['GPSLatitude']
        gps_latitude_ref = gps_info['GPSLatitudeRef']
        gps_longitude = gps_info['GPSLongitude']
        gps_longitude_ref = gps_info['GPSLongitudeRef']
        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            latitude = convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":                     
                latitude = 0 - latitude
            longitude = convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                longitude = 0 - longitude
        googlemaps = 'https://maps.google.com/?ll=' + str(latitude) + ',' + str(longitude) + '&z14&views=traffic'
        gps_data_transf.update({'Latitude': latitude,'GPS_latitude_ref':gps_latitude_ref,'Longitude': longitude,'GPS_longitude_ref':gps_longitude_ref,'googlemaps':googlemaps}) 
    return gps_data_transf


#convert gps coordinates to float degress
def convert_to_degress(value):
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)
    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)
    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)

#format response
def formatter(pexif_data, pgps_data):
    response_data = {}
    

    if 'Make' in pexif_data:
      response_data.update({'Make': pexif_data['Make']})
    if 'Model' in pexif_data:
      response_data.update({'Model': pexif_data['Model']})
    if 'XResolution' in pexif_data:
      response_data.update({'XResolution': pexif_data['XResolution']})
    if 'YResolution' in pexif_data:
      response_data.update({'YResolution': pexif_data['YResolution']}) 
    vvalue = pexif_data.get('Orientation',None)
    if str(vvalue) == '0':
       response_data.update({'Orientation': 'Vertical'}) 
    if str(vvalue) == '1':
      response_data.update({'Orientation': 'Horizontal'}) 

    vvalue = pexif_data.get('DateTimeDigitized',None)
    if str(vvalue) != None:
     response_data.update({'DateTimeDigitized': pexif_data['DateTimeDigitized']})	
    
    vvalue = pexif_data.get('DateTime',None)
    if str(vvalue) != None:
     response_data.update({'DateTime': pexif_data['DateTime']})	
    
    vvalue = pexif_data.get('Flash',None)
    if str(vvalue) == '0':
      response_data.update({'Flash': 'NO'})	
    if str(vvalue) == '1':
      response_data.update({'Flash': 'YES'})	

    vvalue = pexif_data.get('ISOSpeedRatings',None)
    if str(vvalue) != None:
     response_data.update({'ISOSpeedRatings': pexif_data['ISOSpeedRatings']})	
      

    vvalue = pexif_data.get('ResolutionUnit',None) 
    if str(vvalue) == '1':
      response_data.update({'ResolutionUnit': 'None'})
    if str(vvalue) == '12':
      response_data.update({'ResolutionUnit': 'inches'})
    if str(vvalue) == '3':
      response_data.update({'ResolutionUnit': 'cm'})
    
    #add gps data
    response_data.update(pgps_data)
    
    print ("2///////////////////////////////////////////////////2")
    print (response_data)
    print ("2///////////////////////////////////////////////////2")
    return response_data

if __name__ == "__main__":
    application.run()