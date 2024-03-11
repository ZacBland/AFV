from PIL import Image
import cv2

counter = 0
max_value = input('Max Temp Value: ')
min_value = input('Min Temp Value: ')

def mouse_callback(event, x, y, flags, params): # Tracks the pixel the mouse it hovering on. When right click it prints the pixel location and its RBG values.                                     
    global counter
    if event == 2:
        counter += 1
        r, g, b = rgb_img.getpixel((x, y))
        print(f'{counter}: {[x, y]} value {r} {g} {b}')
    else:
        print([x, y], end='\t\r', flush=True)

path_image = 'FLIR0025.jpg'
img = cv2.imread(path_image)
im = Image.open(path_image)
rgb_img = im.convert('RGB')

width = 480
height = 640

scale_width = width / im.size[0]
scale_height = height / im.size[1]
scale = min(scale_width, scale_height)
window_width = int((im.size[0] * scale) * 0.5)
window_height = int((im.size[1] * scale) * 0.5)

cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('image', window_width, window_height)

cv2.setMouseCallback('image', mouse_callback)

cv2.imshow('image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()