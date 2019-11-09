# USAGE
# python scan.py --image images/page.jpg

# import the necessary packages
from pyimagesearch.transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import imutils
import os
directory = r'C:\Users\mithai\Downloads\document-scanner\document-scanner\images\error'
kernel = np.ones((3,3), np.uint8) 


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True,
	help = "Path to the image to be scanned")
args = vars(ap.parse_args())

# load the image and compute the ratio of the old height
# to the new height, clone it, and resize it

###################################################################
#for bloack boxes
image = cv2.imread(args["image"])
#ratio = image.shape[0] / 500.0
orig = image.copy()
#image = imutils.resize(image, height = 500)

crop_img = image[20: , 0:70]
cv2.imshow("cropped", crop_img)
###################################################################
img_erosion = cv2.erode(crop_img, kernel, iterations=1) 
img_dilation = cv2.dilate(crop_img, kernel, iterations=1)

cv2.waitKey(0)
edged=crop_img
cv2.destroyAllWindows()
###################################################################
gray = cv2.cvtColor(img_erosion, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(blurred, 90, 255, cv2.THRESH_BINARY)[1]
cv2.imshow("thresh", thresh)
cv2.waitKey(0)

###################################################################

#contours,hierarchy = cv2.findContours(thresh, 1, 2)
contours, hierarchy = cv2.findContours(thresh,1, cv2.CHAIN_APPROX_NONE)


cnt = contours[1]
M = cv2.moments(cnt)

cv2.drawContours(thresh, contours, -1, (0, 255, 0), 2) 
cv2.imshow("thresh", thresh)
cv2.waitKey(0)

cx = int(M['m10']/M['m00'])
cy = int(M['m01']/M['m00'])
print (len(contours))





###################################################################
#for bubbols
bubble = image[cy + 20: , cx:20]
cv2.imshow("bubble", bubble)