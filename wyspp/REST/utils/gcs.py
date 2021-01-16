import os
import time
import hashlib
from google.cloud import storage


def uploadFile(data):
    file = data.file
    fileName = os.path.splitext(data.name)
    originalName = fileName[0]
    fileExt = fileName[1]
    fileNewName = str(round(time.time() * 1000)) + '-' + originalName
    fileHashedName = computeMD5hash(fileNewName) + fileExt
    
    client = storage.Client()
    bucket = client.get_bucket("wyspp-data")
    blob = bucket.blob(fileHashedName)

    blob.upload_from_file(file)
    url = blob.public_url
    return url


def computeMD5hash(my_string):
    m = hashlib.md5()
    m.update(my_string.encode('utf-8'))
    return m.hexdigest()
