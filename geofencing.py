# -*- coding: utf-8 -*-
"""

-- BE SURE TO ADD 'maps' FOLDER IN C DRIVE

-- install cv2 module with commmand '!pip install opencv-python'

INSTRUCTIONS:
    
-- Enter two coordinates seperated by a comma!

-- Maps will be uploaded into 'maps' folder

--
"""

# =============================================================================
# ----- MODULE IMPORTS --------------------------------------------------------
# =============================================================================
import cv2
import os
import urllib.request
from shapely.geometry import Polygon
import simplekml

# BE SURE TO ADD 'maps' FOLDER IN YOUR C DRIVE
directory = './maps'
if not os.path.exists(directory):
    os.makedirs(directory)
os.chdir(directory)

# =============================================================================
# ----- MAIN ROUTINE ----------------------------------------------------------
# =============================================================================
def main():
    
    # 36.162738, -97.086237  <------ Stillwater Regional Airport
    # 35.952261, -96.769567  <------ Cushing Regional Airport
    # 35.851035, -97.412976  <------ Guthrie Regional Airport
    
    # Enter center coordinates
    coords_in = input('Enter center coordinates: ')
    coords_list = coords_in.split(',')
    coords_list[0] = float(coords_list[0])
    coords_list[1] = float(coords_list[1])
    
    print('This may take a sec.')
    
    # Quadrent functions for generating image from coords
    quad_1(coords_list)
    quad_2(coords_list)
    quad_3(coords_list)
    quad_4(coords_list)
    # Stitch image quadrents together
    stitch_image()
    
    # Read stitched image
    img = cv2.imread('Z_MAP.jpg')
    # Sobel/Canny edge detection
    edges = edge_detection(img)
    # Fill largest contours and place boxes around them
    top_left_corners, bottom_right_corners = box_edges(img, edges)   
    
    # Convert pixel location of boxes to set of coordinates for geofencing
    top_left_corners, bottom_right_corners = convert_pixels_to_coords(coords_list, 
                                        top_left_corners, bottom_right_corners)
    # Define geofences with sets of coordinates 
    geofencing(top_left_corners, bottom_right_corners)
    
    print('\nAll generated files can be found in C:/maps.')
    input('Press <Enter> to exit.') 
    
    
    
    return 


# =============================================================================
# ----- FUNCTIONS & DEFINITIONS -----------------------------------------------
# =============================================================================
# Quadrent size
n = 4

# Zoom 17: (0.00687, 0.00534)
# Zoom 18: (0.003435, 0.00267) (factor of 2 per zoom)
# Veritcal scaling factor
vert = 0.00267
# Horizontal scaling factor
horiz = 0.003435


# Create quadrent arrays
coords_1 = [[0 for x in range(n)] for x in range(n)]
coords_2 = [[0 for x in range(n)] for x in range(n)]
coords_3 = [[0 for x in range(n)] for x in range(n)]
coords_4 = [[0 for x in range(n)] for x in range(n)]

# Stiching Quads
imgs = [[0 for x in range(n)] for x in range(n)]
columns = [0 for x in range(n)]
quad = [0 for x in range(4)]
key = os.environ.get('MAP')

# =============================================================================
# ----- QUADRENT FUNCTIONS ----------------------------------------------------
# =============================================================================

# ===== Quad 1 ================================================================
def quad_1(coords_list : list):
    for i in range(n):
        # Columns 
        for j in range(n):
            coords_1[i][j] = [(coords_list[0] + vert*i), (coords_list[1] + horiz*j)]
            print(coords_1[i][j])
            url = "https://maps.googleapis.com/maps/api/staticmap?center=" + str(coords_1[i][j][0]) + "," + str(coords_1[i][j][1]) + "&zoom=18&size=640x640&maptype=satellite&key="+str(key),"map" + str(i) + str(j) + ".jpg"
            print(url)
            urllib.request.urlretrieve("https://maps.googleapis.com/maps/api/staticmap?center=" + str(coords_1[i][j][0]) + "," + str(coords_1[i][j][1]) + "&zoom=18&size=640x640&maptype=satellite&key="+str(key),"map" + str(i) + str(j) + ".jpg") 

    for i in range(n):
        # Vertically concat columns
        for j in range(n):
            imgs[i][j] = cv2.imread('map' + str(i) + str(j) + '.jpg')
            # Cropping
            imgs[i][j] = imgs[i][j][0:615, 0:640]
        
    for i in range(n):
        column = cv2.vconcat([imgs[3][i], imgs[2][i], imgs[1][i], imgs[0][i]])
        cv2.imwrite('column' + str(i) + '.jpg', column)
        columns[i] = cv2.imread('column' + str(i) + '.jpg')

    quad_left = cv2.hconcat([columns[0], columns[1]])
    quad_right = cv2.hconcat([columns[2], columns[3]])
    cv2.imwrite('quad_left.jpg', quad_left)
    cv2.imwrite('quad_right.jpg', quad_right)
    quad_left = cv2.imread('quad_left.jpg')
    quad_right = cv2.imread('quad_right.jpg')

    # quad 1
    quad_1 = cv2.hconcat([quad_left, quad_right])
    cv2.imwrite('quad_1.jpg', quad_1)
    
    
# ===== Quad 2 ================================================================
def quad_2(coords_list : list):
    for i in range(n):
        # Columns 
        for j in range(n):
            coords_1[i][j] = [(coords_list[0] - vert*(i+1)), (coords_list[1] + horiz*j)]
            
            urllib.request.urlretrieve(
           "https://maps.googleapis.com/maps/api/staticmap?center=" + 
           str(coords_1[i][j][0]) + "," + str(coords_1[i][j][1]) + 
           "&zoom=18&size=640x640&maptype=satellite&key="+str(key),
           "map" + str(i) + str(j) + ".jpg") 

    for i in range(n):
        # Vertically concat columns
        for j in range(n):
            imgs[i][j] = cv2.imread('map' + str(i) + str(j) + '.jpg')
            # Cropping
            imgs[i][j] = imgs[i][j][0:615, 0:640]
        
    for i in range(n):
        column = cv2.vconcat([imgs[0][i], imgs[1][i], imgs[2][i], imgs[3][i]])
        cv2.imwrite('column' + str(i) + '.jpg', column)
        columns[i] = cv2.imread('column' + str(i) + '.jpg')

    quad_left = cv2.hconcat([columns[0], columns[1]])
    quad_right = cv2.hconcat([columns[2], columns[3]])
    cv2.imwrite('quad_left.jpg', quad_left)
    cv2.imwrite('quad_right.jpg', quad_right)
    quad_left = cv2.imread('quad_left.jpg')
    quad_right = cv2.imread('quad_right.jpg')

    # quad 2
    quad_2 = cv2.hconcat([quad_left, quad_right])
    cv2.imwrite('quad_2.jpg', quad_2)
    
    
# ===== Quad 3 ================================================================   
def quad_3(coords_list : list):
    for i in range(n):
        # Columns 
        for j in range(n):
            coords_1[i][j] = [(coords_list[0] - vert*(i+1)), (coords_list[1] - horiz*(j+1))]
            
            urllib.request.urlretrieve(
           "https://maps.googleapis.com/maps/api/staticmap?center=" + 
           str(coords_1[i][j][0]) + "," + str(coords_1[i][j][1]) + 
           "&zoom=18&size=640x640&maptype=satellite&key="+str(key),
           "map" + str(i) + str(j) + ".jpg") 

    for i in range(n):
        # Vertically concat columns
        for j in range(n):
            imgs[i][j] = cv2.imread('map' + str(i) + str(j) + '.jpg')
            # Cropping
            imgs[i][j] = imgs[i][j][0:615, 0:640]
        
    for i in range(n):
        column = cv2.vconcat([imgs[0][i], imgs[1][i], imgs[2][i], imgs[3][i]])
        cv2.imwrite('column' + str(i) + '.jpg', column)
        columns[i] = cv2.imread('column' + str(i) + '.jpg')

    quad_left = cv2.hconcat([columns[3], columns[2]])
    quad_right = cv2.hconcat([columns[1], columns[0]])
    cv2.imwrite('quad_left.jpg', quad_left)
    cv2.imwrite('quad_right.jpg', quad_right)
    quad_left = cv2.imread('quad_left.jpg')
    quad_right = cv2.imread('quad_right.jpg')

    # quad 3
    quad_3 = cv2.hconcat([quad_left, quad_right])
    cv2.imwrite('quad_3.jpg', quad_3)


# ===== Quad 4 ================================================================
def quad_4(coords_list : list):
    for i in range(n):
        # Columns 
        for j in range(n):
            coords_1[i][j] = [(coords_list[0] + vert*i), (coords_list[1] - horiz*(j+1))]
            
            urllib.request.urlretrieve(
           "https://maps.googleapis.com/maps/api/staticmap?center=" + 
           str(coords_1[i][j][0]) + "," + str(coords_1[i][j][1]) + 
           "&zoom=18&size=640x640&maptype=satellite&key="+str(key),
           "map" + str(i) + str(j) + ".jpg") 

    for i in range(n):
        # Vertically concat columns
        for j in range(n):
            imgs[i][j] = cv2.imread('map' + str(i) + str(j) + '.jpg')
            # Cropping
            imgs[i][j] = imgs[i][j][0:615, 0:640]
        
    for i in range(n):
        column = cv2.vconcat([imgs[3][i], imgs[2][i], imgs[1][i], imgs[0][i]])
        cv2.imwrite('column' + str(i) + '.jpg', column)
        columns[i] = cv2.imread('column' + str(i) + '.jpg')
            

    quad_left = cv2.hconcat([columns[3], columns[2]])
    quad_right = cv2.hconcat([columns[1], columns[0]])
    cv2.imwrite('quad_left.jpg', quad_left)
    cv2.imwrite('quad_right.jpg', quad_right)
    quad_left = cv2.imread('quad_left.jpg')
    quad_right = cv2.imread('quad_right.jpg')

    # quad 4
    quad_4 = cv2.hconcat([quad_left, quad_right])
    cv2.imwrite('quad_4.jpg', quad_4)


# ===== Stich final image =====================================================
def stitch_image():
    for i in range(4):
        quad[i] = cv2.imread('quad_' + str(i+1) + '.jpg')

    quad_upper = cv2.hconcat([quad[3], quad[0]])
    quad_lower = cv2.hconcat([quad[2], quad[1]])
    cv2.imwrite('quad_upper.jpg', quad_upper)
    cv2.imwrite('quad_lower.jpg', quad_lower)
    quad_upper = cv2.imread('quad_upper.jpg')
    quad_lower = cv2.imread('quad_lower.jpg')
     
    # Fial Image
    mega_img = cv2.vconcat([quad_upper, quad_lower])   
    cv2.imwrite('Z_MAP.jpg', mega_img)    


# =============================================================================
# ----- IMG PROCESSING FUNCTIONS ----------------------------------------------
# =============================================================================

# ===== Edge Detection ========================================================
def edge_detection(img):
    ''' Uses sobel/canny edge detection from OpenCV to outline image ''' 
    # Convert to graycsale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Sobel Edge Detection
    grad_x = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=1)
    grad_y = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=1)
    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)
    grad = cv2.addWeighted(abs_grad_x, 0.7, abs_grad_y, 0.7, 0) 
    cv2.imwrite('sobel.jpg', grad)
    
    # Blur the image for better edge detection
    img_blur = cv2.GaussianBlur(grad, (5,5), 0) 
    # Canny Edge Detection
    edges = cv2.Canny(image=img_blur, threshold1=190, threshold2=210) 
    cv2.imwrite('canny.jpg', edges)
    
    # Return Canny Edge Detection Image
    return edges

    
# ===== Fill outlines of shapes ===============================================
def box_edges(img, edges):
    ''' Fill enclosed outlined areas using contour detection and box them.'''
    # Thicken canny image output
    kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    dilate = cv2.dilate(edges, kernel_ellipse, iterations=1)
    (cnts, _) = cv2.findContours(dilate.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = img.copy()
    
    # Area threshold for boxes
    max_area = 800
    
    # For storing pixel locations of boxes
    top_left_corners = []
    bottom_right_corners = []
    
    # Shade contours over specified area and draw boxes around them
    for c in cnts:
        area = cv2.contourArea(c)
        if area > max_area:
            cv2.drawContours(result , [c], -1, (255, 255, 255), -1)
            area = max_area
            rect = cv2.boundingRect(c)
            # print(cv2.contourArea(c))
            x,y,w,h = rect
            cv2.rectangle(result,(x,y),(x+w,y+h),(255,0,255),5)
            top_left_corners.append((x,y))
            bottom_right_corners.append((x+w,y+h))
    
    '''
    # special color
    colors = [ (255, 255, 255) ]
    # all other colors
    mask = np.zeros(shaded.shape[:2], dtype=bool)
    for color in colors:   
        mask |= (shaded == color).all(-1)
    shaded[~mask] = (0,0,0) 
    '''
    
    cv2.imwrite('Z_FENCED.jpg', result)
    return top_left_corners, bottom_right_corners                   


# ===== Pixel pairs to coordinate pairs =======================================
def convert_pixels_to_coords(coords_list : list, top_left_corners : list, 
                            bottom_right_corners : list) -> list:
    ''' Converts the pixel location in an image to a set of latitude and 
        longitude coordinates.'''
    
    # Image dimensions (in pixels)
    image_width = 5120
    image_height = 4920
    
    # Known coordinates of top-left and bottom-right corners on the image
    top_left_latitude = (coords_list[0] + (3.5*vert))  # Replace with your actual coordinates
    bottom_right_latitude = (coords_list[0] - (4.5*vert))  # Replace with your actual coordinates
    left_longitude = (coords_list[1] - (4.5*horiz))  # Replace with your actual coordinates
    right_longitude = (coords_list[1] + (3.5*horiz))  # Replace with your actual coordinates
    
    # Calculate the degrees difference
    latitude_difference = top_left_latitude - bottom_right_latitude
    longitude_difference = right_longitude - left_longitude

    # Calculate pixels per degree
    degrees_per_pixel_latitude = 1 / (image_height / latitude_difference)
    degrees_per_pixel_longitude = 1 / (image_width / longitude_difference)
    
    # Known center coordinate (latitude and longitude) of the image
    center_latitude = (coords_list[0] - (vert/2))
    center_longitude = (coords_list[1] - (horiz/2))

    # Convert top left corners list from pixel pairs to coordinate pairs
    i = 0
    for pixel_x, pixel_y in top_left_corners:
        # Calculate the offset from the center (in degrees)
        offset_longitude = (pixel_x - (image_width / 2)) * degrees_per_pixel_longitude
        offset_latitude = (-(pixel_y) + (image_height / 2)) * degrees_per_pixel_latitude
        # Calculate the geographical coordinates of the pixel
        pixel_latitude = center_latitude + offset_latitude
        pixel_longitude = center_longitude + offset_longitude
        # Store in list
        top_left_corners[i] = (pixel_latitude, pixel_longitude)
        i += 1
        
    # Convert bottom right corners list from pixel pairs to coordinate pairs    
    i = 0    
    for pixel_x, pixel_y in bottom_right_corners:
        # Calculate the offset from the center (in degrees)
        offset_longitude = (pixel_x - (image_width / 2)) * degrees_per_pixel_longitude
        offset_latitude = (-(pixel_y) + (image_height / 2)) * degrees_per_pixel_latitude
        # Calculate the geographical coordinates of the pixel
        pixel_latitude = center_latitude + offset_latitude
        pixel_longitude = center_longitude + offset_longitude
        # Store in list
        bottom_right_corners[i] = (pixel_latitude, pixel_longitude)
        i += 1    
    
    return top_left_corners, bottom_right_corners
   
    
# ===== Build geofence polygons ===============================================
def geofencing(top_left_corners : list, bottom_right_corners : list):
    ''' Define geofence polygons from list of coordniate pairs.'''
    geofence_polygon = [0 for x in range(len(top_left_corners))]
     
    for i in range(len(top_left_corners)):
        # Define the coordinates of the geofence polygon
        top_left = (top_left_corners[i][1], top_left_corners[i][0])
        top_right = (bottom_right_corners[i][1], top_left_corners[i][0])
        bottom_left = (top_left_corners[i][1], bottom_right_corners[i][0])
        bottom_right = (bottom_right_corners[i][1], bottom_right_corners[i][0])
        close = top_left
        geofence_coordinates = [(top_left),(top_right),(bottom_right),(bottom_left),(close)]
        # Create a Shapely Polygon
        geofence_polygon[i] = Polygon(geofence_coordinates)
    
    kml = simplekml.Kml()
    
    # Create KML polygons from the Shapely polygons
    for geofence in geofence_polygon:
        kml_polygon = kml.newpolygon(
            outerboundaryis=list(geofence.exterior.coords),
            innerboundaryis=[list(r.coords) for r in geofence.interiors]
            )
        # Customize the KML polygon style (optional)
        kml_polygon.style.linestyle.color = simplekml.Color.red
        kml_polygon.style.linestyle.width = 3
        kml_polygon.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.orange)
    
    kml.save("geofence.kml")
    
# =============================================================================
# ----- INVOKE MAIN ROUTINE ---------------------------------------------------
# =============================================================================
if __name__ == '__main__':
    main()


# =============================================================================
# ----- END OF FILE -----------------------------------------------------------
# =============================================================================