import os
import cv2
import numpy as np

name = 'images/test1_croped.jpg'
# name = 'images/test2.png'

with open(name, 'rb') as f:
    image_np = np.frombuffer(f.read(), dtype=np.uint8)
    image = cv2.imdecode(image_np, flags=1)

    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

image = image_gray

cv2.imshow('original', image)

BLUR_KERNEL_SIZE = (17, 17)
STD_DEV_X_DIRECTION = 0
STD_DEV_Y_DIRECTION = 0
blurred = cv2.GaussianBlur(image, BLUR_KERNEL_SIZE, STD_DEV_X_DIRECTION, STD_DEV_Y_DIRECTION)
MAX_COLOR_VAL = 255
BLOCK_SIZE = 15
SUBTRACT_FROM_MEAN = -2

img_bin = cv2.adaptiveThreshold(
    ~blurred,
    MAX_COLOR_VAL,
    cv2.ADAPTIVE_THRESH_MEAN_C,
    cv2.THRESH_BINARY,
    BLOCK_SIZE,
    SUBTRACT_FROM_MEAN,
)

cv2.imshow("img_bin", img_bin)

vertical = horizontal = img_bin.copy()
SCALE = 5
image_width, image_height = horizontal.shape
horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(image_width / SCALE), 1))
horizontally_opened = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, horizontal_kernel)
vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(image_height / SCALE)))
vertically_opened = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, vertical_kernel)


cv2.imshow('horizontally_opened', horizontally_opened)
cv2.imshow('vertically_opened', vertically_opened)

horizontally_dilated = cv2.dilate(horizontally_opened, cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1)))
vertically_dilated = cv2.dilate(vertically_opened, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 60)))

mask = horizontally_dilated + vertically_dilated
contours, heirarchy = cv2.findContours(
    mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE,
)

MIN_TABLE_AREA = 1e5
contours = [c for c in contours if cv2.contourArea(c) > MIN_TABLE_AREA]
perimeter_lengths = [cv2.arcLength(c, True) for c in contours]
epsilons = [0.1 * p for p in perimeter_lengths]
approx_polys = [cv2.approxPolyDP(c, e, True) for c, e in zip(contours, epsilons)]
bounding_rects = [cv2.boundingRect(a) for a in approx_polys]

# The link where a lot of this code was borrowed from recommends an
# additional step to check the number of "joints" inside this bounding rectangle.
# A table should have a lot of intersections. We might have a rectangular image
# here though which would only have 4 intersections, 1 at each corner.
# Leaving that step as a future TODO if it is ever necessary.
images = [image[y:y+h, x:x+w] for x, y, w, h in bounding_rects]

cv2.imshow("table", images[0])


cv2.waitKey(0)
cv2.destroyAllWindows()
