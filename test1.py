from flask import Flask, request

'''files = {
    'photo': ('image4.jpg', open('/image4.jpg', 'rb')),
}'''

#response = request.post('http://127.0.0.1:5000/api/v1/mex/upload', files=files)
response = request.post('http://127.0.0.1:5000/api/v1/mex/upload')

print response
