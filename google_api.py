import ee
import numpy as np
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import geemap
# Initialize the Earth Engine
ee.Initialize()
ee.Authenticate()
# Define the area of interest with latitude and longitude bounds
lat, lon =  36.162738, -97.086237   
point = ee.Geometry.Point(lon, lat)


image = ee.ImageCollection('LANDSAT/LC08/C01/T1') \
    .filterBounds(point) \
    .filterDate('2020-01-01', '2023-12-31') \
    .sort('CLOUD_COVER') \
    .first() 
    #.select(['B1','B4', 'B3', 'B2']) 

# Define a map centered on southern Maine.
m = geemap.Map(center=[lat, lon], zoom=10)

# Add the image layer to the map and display it.
m.add_layer(
    image, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 30000}, 'first'
)

# Define the file path for the output image
out_file = './Tiff/Stillwater_Airport.tif'

# Export the image
geemap.ee_export_image(image, filename=out_file, scale=30, region=point.buffer(10000).bounds(), file_per_band=False)

#display(m)
'''
# Get the satellite image data
image = ee.ImageCollection('LANDSAT/LC08/C01/T1') \
    .filterBounds(point) \
    .filterDate('2020-01-01', '2020-12-31') \
    .sort('CLOUD_COVER') \
    .first() \
    .select(['B1','B4', 'B3', 'B2'])  # RGB bands for Landsat 8
'''


'''
# Get the satellite image data
image = ee.ImageCollection('LANDSAT/LC08/C01/T1') \
    .filterBounds(point) \
    .filterDate('2020-01-01', '2020-12-31') \
    .sort('CLOUD_COVER') \
    .first() \
    .select(['B1','B4', 'B3', 'B2'])  # RGB bands for Landsat 8
'''
# Set the region to download
# Set the region to download
region = image.geometry().bounds().getInfo()['coordinates']

# Export the image to a Google Drive folder
task = ee.batch.Export.image.toDrive(
    image= image,
    description = 'imageToDriveExample',
    folder= 'Tiff_Images',
    fileNamePrefix= 'Stillwater_Airport',
    region=region,
    scale=30,
    crs='EPSG:5070'

)
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