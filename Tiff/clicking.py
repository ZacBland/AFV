# Imports
from osgeo import gdal, gdal_array

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import glob
from PIL import Image
import cv2
import numpy as np
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import numpy as np
def visualise_rgb(img,clip=[0.3,0.3,0.3],display=True):
        """Visulaise RGB image with given clip values and return image"""

        # Scale image
        img = np.clip(img/10000,0,1)
        
        # Get RGB channels
        rgb = img[[3,2,1]]

        #clip rgb values
        rgb[0] = np.clip(rgb[0],0,clip[0])/clip[0]
        rgb[1] = np.clip(rgb[1],0,clip[1])/clip[1]
        rgb[2] = np.clip(rgb[2],0,clip[2])/clip[2]

        rgb = rgb.transpose(1,2,0)

        plt.imshow(rgb)
        plt.title("RGB Image")
        plt.axis('off')
        plt.show()

        return rgb

# Example usage
file_path = 'Tiff/LandInsidePolygon_StillwaterAirport_1.tif'
img = gdal.Open(file_path).ReadAsArray()
rgb_3 = visualise_rgb(img,[0.3,0.3,0.3],display=True )
import rasterio
dataset = rasterio.open(file_path)
#left edge
print(dataset.bounds[0])
#bottom edge
print(dataset.bounds[1])
#right edge
print(dataset.bounds[2])
#top edge
print(dataset.bounds[3])
import rasterio
from rasterio.transform import Affine
from pyproj import Transformer

def pixel_to_gps(file_path, x_pixel, y_pixel):
    """
    Convert pixel coordinates to GPS (latitude and longitude) coordinates.

    Args:
    - file_path: Path to the GeoTIFF file.
    - x_pixel, y_pixel: Pixel coordinates in the image.

    Returns:
    - A tuple of (longitude, latitude).
    """
    with rasterio.open(file_path) as dataset:
        # Get the affine transform for the dataset
        transform = dataset.transform

        # Convert pixel coordinates to the CRS of the GeoTIFF
        x_crs, y_crs = transform * Affine.translation(0.5, 0.5) * (x_pixel, y_pixel)

        # Initialize transformer to convert from the CRS of the GeoTIFF to WGS84
        # Replace 'dataset.crs' with the correct CRS if necessary
        transformer = Transformer.from_crs(dataset.crs, 'EPSG:4326', always_xy=True)

        # Convert from CRS to WGS84
        longitude, latitude = transformer.transform(x_crs, y_crs)

    return longitude, latitude

# Example usage
x_pixel, y_pixel = 100, 50  # Example pixel coordinates
longitude, latitude = pixel_to_gps(file_path, x_pixel, y_pixel)
print(f"Longitude: {longitude}, Latitude: {latitude}")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.transform import from_origin
from pyproj import Transformer


def onclick(event, dataset, transformer, ax):
    if event.xdata is not None and event.ydata is not None:
        # Convert pixel coordinates to the CRS of the GeoTIFF
        x_crs, y_crs = dataset.transform * (event.xdata, event.ydata)
        
        # Convert from CRS to WGS84
        longitude, latitude = transformer.transform(x_crs, y_crs)
        
        print(f'Longitude: {longitude}, Latitude: {latitude}')
        # Optionally, you can also display this information directly on the plot
        ax.plot(event.xdata, event.ydata, 'ro')  # mark the clicked position
        ax.annotate(f'({longitude:.5f}, {latitude:.5f})', (event.xdata, event.ydata), color='white')
dataset = rasterio.open(file_path)

    # Setup the transformer to convert from the dataset's CRS to WGS84
transformer = Transformer.from_crs(dataset.crs, 'EPSG:4326', always_xy=True)

image = dataset.read(1)

fig, ax = plt.subplots(figsize=(50, 25))  # Adjust the figsize to suit your image's aspect ratio
im = ax.imshow(image, interpolation='nearest',aspect='equal')


    # The 'lambda' function here creates a closure over the variables we want to use inside the onclick function
fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, dataset, transformer, ax))

plt.show()

# Open your GeoTIFF file
dataset = gdal.Open(file_path, gdal.GA_ReadOnly)
from pyproj import Proj, Transformer

# Get geotransform and projection
geo_transform = dataset.GetGeoTransform()
proj = dataset.GetProjection()

# Setup projection using the GeoTIFF's projection info
source_proj = Proj(proj)

# Setup destination projection as WGS84
dest_proj = Proj(proj='latlong', datum='WGS84')

# Setup transformer
transformer = Transformer.from_proj(source_proj, dest_proj)

def pixel_to_coords(x_pixel, y_pixel, geo_transform, transformer):
    """
    Convert pixel coordinates to geographic coordinates.
    
    Args:
    - x_pixel, y_pixel: Pixel coordinates
    - geo_transform: Affine transformation coefficients
    - transformer: PyProj transformer object for coordinate conversion
    
    Returns:
    - Longitude, Latitude: Geographic coordinates
    """
    # Apply geo_transform to get coordinates in the dataset's CRS
    x_crs = geo_transform[0] + x_pixel * geo_transform[1] + y_pixel * geo_transform[2]
    y_crs = geo_transform[3] + x_pixel * geo_transform[4] + y_pixel * geo_transform[5]
    
    # Transform to geographic coordinates (longitude, latitude)
    longitude, latitude = transformer.transform(x_crs, y_crs, direction='FORWARD')
    
    return longitude, latitude

# Example usage
x_pixel, y_pixel = 100, 50  # Example pixel coordinates
longitude, latitude = pixel_to_coords(x_pixel, y_pixel, geo_transform, transformer)
print(f"Longitude: {longitude}, Latitude: {latitude}")


def onclick(event, geo_transform, transformer, ax):
    if event.xdata is not None and event.ydata is not None:
        x_pixel, y_pixel = int(event.xdata), int(event.ydata)
        
        # Convert pixel coordinates to geographic coordinates
        x_crs, y_crs = geo_transform[0] + x_pixel * geo_transform[1] + y_pixel * geo_transform[2], \
                       geo_transform[3] + x_pixel * geo_transform[4] + y_pixel * geo_transform[5]
        longitude, latitude = transformer.transform(x_crs, y_crs, direction='FORWARD')
        
        print(f'Longitude: {longitude}, Latitude: {latitude}')
        
        # Optionally, display the clicked position and coordinates on the plot
        ax.plot(x_pixel, y_pixel, 'ro')  # mark the clicked position
        ax.annotate(f'({longitude:.5f}, {latitude:.5f})', (x_pixel, y_pixel), color='white')
def read_rgb_image(dataset):
    """Reads the first three bands of the dataset and stacks them into an RGB image."""
    img = dataset.ReadAsArray()
    img = np.clip(img/10000,0,1)
    rgb = img[[3,2,1]]
    rgb[0] = np.clip(rgb[0],0,0.3)/0.3
    rgb[1] = np.clip(rgb[1],0,0.3)/0.3
    rgb[2] = np.clip(rgb[2],0,0.3)/0.3
    rgb = rgb.transpose(1,2,0)
    return rgb

# Read the raster data as RGB
image_data = read_rgb_image(dataset)

    # Ensure data is in the correct range for display
    # Normalize or scale if necessary (this step may be optional based on your data)
image_data = image_data.astype(float)
for i in range(3):  # Normalize each channel to 0-1
        channel = image_data[:,:,i]
        image_data[:,:,i] = (channel - np.min(channel)) / (np.max(channel) - np.min(channel))

    # Display the image
fig, ax = plt.subplots(figsize=(8, 6))
ax.imshow(image_data)

    # Connect the onclick event
fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, geo_transform, transformer, ax))
    
plt.show()