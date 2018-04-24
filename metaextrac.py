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
        #gps_latitude = self.get_if_exist(gps_info, "GPSLatitude")
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

        #print "GPS INFO present"
       
        #print latitude
        #print gps_latitude_ref
        #print longitude
        #print gps_longitude_ref
        googlemaps = 'https://maps.google.com/?ll=' + str(latitude) + ',' + str(longitude) + '&z14&views=traffic'
        #print googlemaps
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
    print pexif_data
    #print pgps_data

    if 'Orientation' in pexif_data and pexif_data['Orientation'] == '0':
		print ("Orientation Vertical")
    if 'Orientation' in pexif_data and pexif_data['Orientation'] == '1':
		print ("Orientation Horizontal")
    if 'Orientation' in pexif_data and pexif_data['Orientation'] == '2':
		print ("Orientation Mirror Horizontal")		
    if 'Orientation' in pexif_data and pexif_data['Orientation'] == '3':
		print ("Orientation Rotate 180")		
    if 'Orientation' in pexif_data and pexif_data['Orientation'] == '4':
		print ("Orientation Mirror vertical")		
    if 'Orientation' in pexif_data and pexif_data['Orientation'] == '5':
		print ("Orientation Mirror horizontal and rotate 270 CW")		
    if 'Orientation' in pexif_data and pexif_data['Orientation'] == '6':
		print ("Orientation Rotate 90 CW")		
    if 'Orientation' in pexif_data and pexif_data['Orientation'] == '7':
		print ("Orientation Mirror horizontal and rotate 90 CW")			
    if 'Orientation' in pexif_data and pexif_data['Orientation'] == '8':
		print ("Orientation Rotate 270 CW")		

    if 'GPSAltitudeRef' in pexif_data and pexif_data['GPSAltitudeRef'] == '\x00':
		print ("GPSAltitudeRef  Above Sea Level")	
    if 'GPSAltitudeRef' in pexif_data and pexif_data['GPSAltitudeRef'] == '1':
		print ("GPSAltitudeRef  Below Sea Level")

    if 'Flash' in pexif_data and pexif_data['Flash'] == '0':
		print ("Flash NO")
    if 'Flash' in pexif_data and pexif_data['Flash'] == '1':
		print ("Flash YES")

    if 'GPSSpeedRef' in pexif_data and pexif_data['GPSSpeedRef'] == 'K':
		print ("GPSSpeedRef  km/h")
    if 'GPSSpeedRef' in pexif_data and pexif_data['GPSSpeedRef'] == 'M':
		print ("GPSSpeedRef  mph")
    if 'GPSSpeedRef' in pexif_data and pexif_data['GPSSpeedRef'] == 'N':
        print ("GPSSpeedRef  knots")
        
    if 'ResolutionUnit' in pexif_data and pexif_data['ResolutionUnit'] == '1':
		print ("ResolutionUnit None")
    if 'ResolutionUnit' in pexif_data and pexif_data['ResolutionUnit'] == '12':
		print ("ResolutionUnit inches")	
    if 'ResolutionUnit' in pexif_data and pexif_data['ResolutionUnit'] == '3':
		print ("ResolutionUnit cm")	
    
    
    return "ok"

if __name__ == "__main__":
    application.run()