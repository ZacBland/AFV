import rasterio
import matplotlib.pyplot as plt
import numpy as np
# Open the GeoTIFF file
with rasterio.open('./NYC_Image.tif') as src:
    r = src.read(1).astype(float)
    g = src.read(2).astype(float)
    b = src.read(3).astype(float)
    img = src.read()
    # Normalize the bands to 0-1 range if they are not in 0-255 range
    #r /= r.max()
    #g /= g.max()
    #b /= b.max()

    # Stack the bands along the last axis
    #rgb = np.stack((r, g, b), axis=-1)

    # Plot the image
    plt.imshow(img[:,:,0])
    plt.title('RGB Image')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.savefig('NYC.png')