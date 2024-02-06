# Imports
from osgeo import gdal

import numpy as np
import matplotlib.pyplot as plt

import glob
#Load first image
img = gdal.Open('NYC_Image.tif').ReadAsArray()
img.shape #(12,256,256)
rgb = img[[2,1,0]].transpose(1,2,0)
print(rgb.min(),rgb.max()) #150 8,600
rgb = np.clip(rgb/10000,0,1)
plt.imshow(rgb)