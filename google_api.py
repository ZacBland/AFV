import ee
import numpy as np
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Initialize the Earth Engine
ee.Initialize()

# Define the area of interest with latitude and longitude bounds
lat, lon =  36.162738, -97.086237   
point = ee.Geometry.Point(lon, lat)

# Get the satellite image data
image = ee.ImageCollection('LANDSAT/LC08/C01/T1') \
    .filterBounds(point) \
    .filterDate('2020-01-01', '2020-12-31') \
    .sort('CLOUD_COVER') \
    .first() \
    .select(['B1','B4', 'B3', 'B2'])  # RGB bands for Landsat 8

# Set the region to download
region = image.geometry().bounds().getInfo()['coordinates']

# Export the image to a Google Drive folder
task = ee.batch.Export.image.toDrive(**{
    'image': image,
    'description': 'imageToDriveExample',
    'folder': 'Example_folder',
    'fileNamePrefix': 'Stillwater_Airport',
    'scale': 30,
    'region': region
})
task.start()


# Wait for the task to complete
import time
while task.active():
    print('Polling for task (id: {}).'.format(task.id))
    task.status()
    time.sleep(30)

# Authenticate and initialize the Google Drive client
gauth = GoogleAuth()
gauth.LocalWebserverAuth()  # Creates local webserver for authentication
drive = GoogleDrive(gauth)

# List and download files from Google Drive
file_list = drive.ListFile({'q': "'<Your Folder ID>' in parents and trashed=false"}).GetList()
for file in file_list:
    if file['title'] == 'Stillwater_Airport.tif':
        print('Downloading file %s from Google Drive' % file['title'])  # The file name
        file.GetContentFile(file['title'])  # Download file as 'NYC_Image.tif'
# Use GDAL or similar library to convert the downloaded image to GeoTIFF here
# This step depends on how you have set up your local environment and where you have saved the image.
