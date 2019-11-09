# importing cv2  
import cv2 
  
# importing os module   
import os 
# Image directory 
def load_omr_images():
    directory = '/home/avinash/Documents/project/matlab_omr_scanner/python_omrscanner/images/'
    os.chdir(directory) 
    list = os.listdir(directory)
    for ls in list:
        print(ls)
    
load_omr_images()