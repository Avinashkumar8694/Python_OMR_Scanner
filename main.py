# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scanner.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import pymysql
import os
import shutil

#from pyimagesearch.transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse
from scipy import ndimage
import scipy
import pylab
#import pymorph
#import mahotas
from math import *
import cv2
#from pymorph import regmax
from PIL import Image
import imutils
import copy
import array as arr
kernel = np.ones((3,3), np.uint8) 
kernel1 = np.ones((5,5), np.uint8)


conn=pymysql.connect(host="localhost",user="root",password="123456",db="omr_python")
directory = '/home/avinash/Documents/project/matlab_omr_scanner/Python_OMR_Scanner/images'
to_corrected = './corrected/'
List = []
####################################### VAriables ########################################
centroid_diff_bubble=953    #Variable
diff_bubble_hall_x=700      #Variable
diff_bubble_hall_y=1900     #Variable
diff_bubble_vcode_x=400     #Variable
diff_bubble_vcode_y=900     #Variable
diff_bubble_booklet_x=650   #Variable
diff_bubble_booklet_y=350   #Variable

########################################################################################

class Ui_Dialog(object):
    #######################main methods##############################################
    def centroid_coordinates(self,Img,i):
    	orig = copy.copy(Img)
    	crop_img = Img[0: , 0:280]
    
    	gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    	blurred = cv2.GaussianBlur(gray, (5, 5), 1)
    
    
    	thresh = cv2.threshold(blurred, 90, 255, cv2.THRESH_BINARY)[1]
    	thresh = cv2.erode(thresh, kernel1, iterations=2)
    	thresh = cv2.dilate(thresh,kernel,iterations = 1)
    	thresh = cv2.erode(thresh, kernel1, iterations=2)
    	contours, hierarchy = cv2.findContours(thresh,1, cv2.CHAIN_APPROX_NONE)
    	cnt = contours[5]
    	cnt2= contours[i]
    	M = cv2.moments(cnt)
    	M2= cv2.moments(cnt2)
    
    	cv2.drawContours(thresh, cnt2, -1, (0, 255, 0), 10)  
    	#cv2.imshow("Output", thresh)				
    	#cv2.waitKey(0)
    
    	cx = int(M['m10']/M['m00'])
    	cy = int(M['m01']/M['m00'])
    	cx2 = int(M2['m10']/M2['m00'])
    	cy2 = int(M2['m01']/M2['m00'])
    	if(cx2==cx):
    		slope=0
    	else:
    		slope = (cy2-cy)/(cx2-cx)
    	angle=degrees(atan(slope))+90
    	Img=orig
    	#print(cx)
    	#print(cy)
    	#print(cx2)
    	#print(cy2)
    	return cx2,cy2,angle
    
###################    Rotate the image By the given angle   ################
    def rotate_image(self,Img,angle):
    	rotated = ndimage.rotate(Img, angle)
    	Img=rotated
    	return rotated

##################    Image pre-processing for bubble detection 	##################

    def bubble_detect_pre_process(self,Img):
    	gray = cv2.cvtColor(Img, cv2.COLOR_BGR2GRAY)
    
    	closing = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    	#dilation = cv2.dilate(gray,kernel,iterations = 2)
    	erosion = cv2.erode(closing,kernel1,iterations = 2)
    	image = cv2.GaussianBlur(gray, (5, 5), 1)
    	thresh1 = cv2.threshold(erosion,127,255,cv2.THRESH_BINARY)[1]
    	thresh1 = cv2.dilate(thresh1,kernel1,iterations = 4)
    	thresh1 = cv2.morphologyEx(thresh1, cv2.MORPH_OPEN, kernel1)
    	thresh1 = cv2.erode(thresh1,kernel1,iterations = 2)
    	temp=cv2.resize(thresh1,(800,1000))
    	#cv2.imshow("Output",temp)
    	#cv2.waitKey(0)
    	#cv2.imshow("close",erosion)
    	#cv2.waitKey(0)
    	Img=thresh1
    	return thresh1

###############   Detect Bubbles #######################################

    def detect_bubles(self,thresh1,cx,cy,diff,result):
    	start_of_the_box_x=cx+diff
    	start_of_the_box_y=cy
    	
    	#result=[None] * 120
    	ans=0
    	outermost=1
    	outer=1
    	inner=1
    	while(outermost<5):
    		x=start_of_the_box_x+(outermost-1)*(350)
    		y=start_of_the_box_y-50
    		outer=1
    		while(outer<7):
    			y=y+50
    			inner=1
    			while(inner<6):
    				count=0
    				#print("----")
    		
    				if(thresh1[y,x]==0):
    					result[ans]='A'
    					count=count+1
    				x=x+50
    				if(thresh1[y,x]==0):
    					result[ans]='B'
    					count=count+1
    				x=x+50
    				if(thresh1[y,x]==0):
    					result[ans]='C'
    					count=count+1
    				x=x+50
    				if(thresh1[y,x]==0):
    					result[ans]='D'
    					count=count+1
    				if(count > 1):
    					result[ans]='N'
    				if(count==0):
    					result[ans]='S'
    				ans=ans+1
    				inner=inner+1
    				#print(inner)
    				y=y+50
    				x=start_of_the_box_x+(outermost-1)*350
    		
    			outer=outer+1
    			#print(outer)
    		outermost=outermost+1
    	return result

###############  Print Bubble Result  ####################

    def Print_Bubble_result(self,result):
    	j=0
    	for c in result:
    		j=j+1
    		print(c)
    		if(j%5==0):
    			print(' ')
    	return


    ##############   Detect hall Ticket No. ##################
    
    def detect_hall_ticket_no(self,thresh1,cx,cy,result):
    	loop=1
    	ans=0
    	x=cx
    	y=cy
    	print("-----hall_tt----")
    	print(cx)
    	print(cy)
    	while(loop<9):
    		count=0
    		if(thresh1[y,x]==0):
    			result.insert(ans,0)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,1)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,2)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,3)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,4)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,5)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,6)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,7)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,8)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,9)
    			count=count+1	
    		if(count>1):
    			result.insert(ans,-2)
    		if(count==0):
    			result.insert(ans,-1)
    		x=x+50
    		y=cy
    		ans=ans+1
    		loop=loop+1
    		ans=ans+1
    	return result

############   Version Code ###################

    def detect_version_code(self,thresh1,cx,cy,result):
    	x=cx
    	y=cy
    	print(x)
    	print(y)
    	count=0
    	if(thresh1[y,x]==0):
    		result[0]='A'
    		count=count+1
    	x=x+50
    	if(thresh1[y,x]==0):
    		result[0]='B'
    		count=count+1
    	x=x+50
    	if(thresh1[y,x]==0):
    		result[0]='C'
    		count=count+1
    	x=x+50
    	if(thresh1[y,x]==0):
    		result[0]='D'
    		count=count+1
    	if(count>1):
    		result[0]='N'
    	if(count==0):
    		result[0]='S'
    	return result

#######################    Booklet No.   ####################


    def detect_booklet_no(self,thresh1,cx,cy,result):
    	loop=1
    	ans=0
    	x=cx
    	y=cy
    	print("-----hall_tt----")
    	print(cx)
    	print(cy)
    	while(loop<7):
    		count=0
    		if(thresh1[y,x]==0):
    			result.insert(ans,0)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,1)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,2)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,3)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,4)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,5)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,6)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,7)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,8)
    			count=count+1	
    		y=y+50
    		if(thresh1[y,x]==0):
    			result.insert(ans,9)
    			count=count+1	
    		if(count>1):
    			result.insert(ans,-2)
    		if(count==0):
    			result.insert(ans,-1)
    		x=x+50
    		y=cy
    		ans=ans+1
    		loop=loop+1
    		ans=ans+1
    	return result

    #######################################################################################################################################################################################
    def messagebox(self):
        mess = QtWidgets.QMessageBox()
        mess.setWindowTitle("Notice:")
        mess.setText("Task Completed")
        mess.setStandardButtons(QtWidgets.QMessageBox.Ok)
        mess.exec_()
####################################  Calling Calulating main Function ##########################
    #def skip_data(self):
        
    def calculate_omr(self):
        l = len(List)
        if l > 0:
            image = ""
            image1 = ""
            image1 = List.pop()
            
            path_to =  "../corrected/" + image1 
            
            
            print(image1)
            
            image = cv2.imread(image1)
            
            cv2.imwrite(path_to, image)
            self.calculate_omr_stage_2nd(image)
            self.display_OMR(image1)
            self.Next.setEnabled(False)
            self.Exit.setEnabled(True)
            os.remove(image1)
            
        else:
            self.messagebox()
    
    def calculate_omr_stage_2nd(self,image):
        orig = copy.copy(image)
        cx,cy,angle=self.centroid_coordinates(image,55)
        rotated=self.rotate_image(orig,angle)
        cx,cy,angle=self.centroid_coordinates(rotated,55)
        r_orig = copy.copy(rotated)
        processed=self.bubble_detect_pre_process(rotated)
        result_b=[None]*120
        result_b=self.detect_bubles(processed,cx,cy,centroid_diff_bubble,result_b)    #result_b   holds result
        print("working calculate omar 2nd image")
        self.Print_Bubble_result(result_b)
        
        result_hall_tkt = arr.array('i', [])                
        #cx1,cy1,angle=centroid_coordinates(r_orig,16)
        cx=cx+centroid_diff_bubble
        result_hall_tkt=self.detect_hall_ticket_no(processed,cx-diff_bubble_hall_x,cy+diff_bubble_hall_y,result_hall_tkt)   #result_hall_tkt    holds hall ticket number
        print("-------------calculating hall ticket----------------")
        
        #hall_ticket = ""
        #hall_ticket = hall_ticket.join(result_hall_tkt)
        ########################################################## hall ticket no #####################
        htn = ""
        for digit in result_hall_tkt:
            htn += str(digit) 
        self.display_Hall_Ticket_no(htn)
        
        self.Print_Bubble_result(result_hall_tkt)
        #################################################################################################
        
        #################################################### Version code ##############################
        result_vcode =[None]*1
        result_vcode=self.detect_version_code(processed,cx-diff_bubble_vcode_x,cy+diff_bubble_vcode_y,result_vcode)     
        vc = ""

        for digit in result_vcode:
            vc += str(digit)
        self.display_version_code(vc)
        
        print("calculating hall version Code")
        self.Print_Bubble_result(result_vcode)
        #################################################################################################
        
        
        
        #############################################  Booklet Number ###################################
        result_booklet_no = arr.array('i', []) 
        #cx1,cy1,angle=centroid_coordinates(r_orig,16)
        
        result_booklet_no=self.detect_booklet_no(processed,cx-diff_bubble_booklet_x,cy+diff_bubble_booklet_y,result_booklet_no)
        bn = ""
        for digit in result_booklet_no:
            bn += str(digit)
        self.display_booklet_no(bn)
        print("-----------------------------")
        self.Print_Bubble_result(result_booklet_no)
        List=[]
        List.append(bn)
        List.append(htn)
        List.append(vc)
        for c in result_b:
            List.append(c)
        print(len(List))
        cur=conn.cursor()
        query="INSERT INTO answers VALUES %r;" % (tuple(List),)
        result=cur.execute(query)
        conn.commit()
        #self.load_data()
        
        ####################################################################################################
    def display_booklet_no(self,bn):
        
        self.Hall_Ticket_no_3.setText(bn)
        self.Hall_Ticket_no_3.adjustSize()
        
    def display_version_code(self,vc):
        
        self.Hall_Ticket_no_4.setText(vc)
        self.Hall_Ticket_no_4.adjustSize()
        
    def display_Hall_Ticket_no(self,htn):
        self.Hall_Ticket_no.setText(htn)
        self.Hall_Ticket_no.adjustSize()
#######################################################################################################
   # def select_images_in_list(self):
   #     cur=conn.cursor()
   #     query = "select omr_sheet from scanned_images where is_done = 0"
   #     result = cur.execute(query)
   #     record = cur.fetchall()
   #     for row in record:
            
    #        self.Scanned_Img.setPixmap(QtGui.QPixmap("abc.jpg"))
    #        List.append(row)
    #    cur.close()

    def display_OMR(self,img):
        self.Scanned_Img.setPixmap(QtGui.QPixmap(img))
    
    def load_all_omr_image(self):
        
        os.chdir(directory)
        
        list = os.listdir(directory)
        print(list)
        for ls in list:
            List.append(ls)
            cur=conn.cursor()
            query2 = "select * from scanned_images where omr_sheet = '" + ls + "'";
            result2 = cur.execute(query2)
            record = cur.fetchall()
            sz = len(record)
            if sz >= 1:
                continue
            cur.close()
            cur=conn.cursor()
            query = "INSERT INTO scanned_images (omr_sheet) VALUES('" + ls + "')" 
            result = cur.execute(query)
            conn.commit()
            
            print(ls)
            cur.close()
            print("******************************************************")
            
        
    def load_data(self):
        self.load_all_omr_image()
        #self.select_images_in_list()
        #image =  directory + "/abc.jpg"
        #self.display_OMR(image)
        cur=conn.cursor()
        query = "select * from answers"
        result = cur.execute(query)
        
        records = cur.fetchall()
        row_size = len(records)
        self.Responce_Table.setRowCount(0)
        j=0
        for row in records:
            col_size = len(row)
            self.Responce_Table.insertRow(j)
            for i in range(0,123):
                self.Responce_Table.setItem(j,i,QtWidgets.QTableWidgetItem(row[i]))
        j = j + 1    
        cur.close()

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1270, 560)
        Dialog.setMinimumSize(QtCore.QSize(1270, 560))
        Dialog.setMaximumSize(QtCore.QSize(1270, 560))
        Dialog.setAutoFillBackground(True)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(480, 20, 131, 16))
        font = QtGui.QFont()
        font.setFamily("padmaa-Bold.1.1")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setGeometry(QtCore.QRect(10, 40, 281, 231))
        self.frame.setAutoFillBackground(True)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.Hall_Ticket = QtWidgets.QLabel(self.frame)
        self.Hall_Ticket.setGeometry(QtCore.QRect(10, 100, 151, 21))
        font = QtGui.QFont()
        font.setFamily("padmaa-Bold.1.1")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.Hall_Ticket.setFont(font)
        self.Hall_Ticket.setAutoFillBackground(True)
        self.Hall_Ticket.setObjectName("Hall_Ticket")
        self.qr_Code = QtWidgets.QLabel(self.frame)
        self.qr_Code.setGeometry(QtCore.QRect(10, 10, 261, 51))
        self.qr_Code.setText("")
        self.qr_Code.setPixmap(QtGui.QPixmap("../qr_Pixel.png"))
        self.qr_Code.setScaledContents(True)
        self.qr_Code.setObjectName("qr_Code")
        self.Hall_Ticket_no = QtWidgets.QLabel(self.frame)
        self.Hall_Ticket_no.setGeometry(QtCore.QRect(150, 100, 111, 21))
        font = QtGui.QFont()
        font.setFamily("Padauk Book [PYRS]")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.Hall_Ticket_no.setFont(font)
        self.Hall_Ticket_no.setAlignment(QtCore.Qt.AlignCenter)
        self.Hall_Ticket_no.setObjectName("Hall_Ticket_no")
        self.Hall_Ticket_3 = QtWidgets.QLabel(self.frame)
        self.Hall_Ticket_3.setGeometry(QtCore.QRect(10, 130, 121, 21))
        font = QtGui.QFont()
        font.setFamily("padmaa-Bold.1.1")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.Hall_Ticket_3.setFont(font)
        self.Hall_Ticket_3.setAutoFillBackground(True)
        self.Hall_Ticket_3.setObjectName("Hall_Ticket_3")
        self.Hall_Ticket_no_3 = QtWidgets.QLabel(self.frame)
        self.Hall_Ticket_no_3.setGeometry(QtCore.QRect(150, 130, 111, 21))
        font = QtGui.QFont()
        font.setFamily("Padauk Book [PYRS]")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.Hall_Ticket_no_3.setFont(font)
        self.Hall_Ticket_no_3.setAlignment(QtCore.Qt.AlignCenter)
        self.Hall_Ticket_no_3.setObjectName("Hall_Ticket_no_3")
        self.Hall_Ticket_4 = QtWidgets.QLabel(self.frame)
        self.Hall_Ticket_4.setGeometry(QtCore.QRect(10, 160, 151, 21))
        font = QtGui.QFont()
        font.setFamily("padmaa-Bold.1.1")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.Hall_Ticket_4.setFont(font)
        self.Hall_Ticket_4.setAutoFillBackground(True)
        self.Hall_Ticket_4.setObjectName("Hall_Ticket_4")
        self.Hall_Ticket_no_4 = QtWidgets.QLabel(self.frame)
        self.Hall_Ticket_no_4.setGeometry(QtCore.QRect(150, 160, 111, 21))
        font = QtGui.QFont()
        font.setFamily("Padauk Book [PYRS]")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.Hall_Ticket_no_4.setFont(font)
        self.Hall_Ticket_no_4.setAlignment(QtCore.Qt.AlignCenter)
        self.Hall_Ticket_no_4.setObjectName("Hall_Ticket_no_4")
        self.frame_2 = QtWidgets.QFrame(Dialog)
        self.frame_2.setGeometry(QtCore.QRect(10, 440, 281, 111))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.Next = QtWidgets.QPushButton(self.frame_2)
        self.Next.setGeometry(QtCore.QRect(20, 20, 75, 23))
        self.Next.setIconSize(QtCore.QSize(16, 16))
        self.Next.setObjectName("Next")
        self.pushButton_2 = QtWidgets.QPushButton(self.frame_2)
        self.pushButton_2.setGeometry(QtCore.QRect(150, 20, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.Exit = QtWidgets.QPushButton(self.frame_2)
        self.Exit.setGeometry(QtCore.QRect(90, 70, 75, 23))
        self.Exit.setObjectName("Exit")
        self.Scanned_Img = QtWidgets.QLabel(Dialog)
        self.Scanned_Img.setGeometry(QtCore.QRect(320, 40, 421, 511))
        self.Scanned_Img.setAutoFillBackground(True)
        self.Scanned_Img.setText("")
        self.Scanned_Img.setPixmap(QtGui.QPixmap("../1285_Pixel.jpg"))
        self.Scanned_Img.setScaledContents(True)
        self.Scanned_Img.setWordWrap(False)
        self.Scanned_Img.setObjectName("Scanned_Img")
        self.Responce_Table = QtWidgets.QTableWidget(Dialog)
        self.Responce_Table.setGeometry(QtCore.QRect(770, 40, 491, 511))
        self.Responce_Table.setMouseTracking(False)
        self.Responce_Table.setRowCount(0)
        self.Responce_Table.setColumnCount(124)
        self.Responce_Table.setObjectName("Responce_Table")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(950, 20, 131, 16))
        font = QtGui.QFont()
        font.setFamily("padmaa-Bold.1.1")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        
        self.pushButton_2.clicked.connect(self.skip_img)
        self.Next.clicked.connect(self.calculate_omr)
        
        self.Exit.clicked.connect(self.next_img)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_2.setText(_translate("Dialog", "OMR Sheet"))
        self.Hall_Ticket.setText(_translate("Dialog", "Hall Ticket No.:"))
        self.Hall_Ticket_no.setText(_translate("Dialog", "0000000"))
        self.Hall_Ticket_3.setText(_translate("Dialog", "Booklet No.:"))
        self.Hall_Ticket_no_3.setText(_translate("Dialog", "0000000"))
        self.Hall_Ticket_4.setText(_translate("Dialog", "Version Code:"))
        self.Hall_Ticket_no_4.setText(_translate("Dialog", "0"))
        self.Next.setText(_translate("Dialog", "Calculate"))
        self.pushButton_2.setText(_translate("Dialog", "Skip"))
        self.Exit.setText(_translate("Dialog", "Next"))
        self.label_4.setText(_translate("Dialog", "OMR Responce"))
        
    def next_img(self):
        ln = len(List)
        if ln>0:
            img = List[-1]
            
            
            
            self.display_OMR(img)
            self.Next.setEnabled(True)
            self.Exit.setEnabled(False)
            
            self.display_booklet_no("000000")
            self.display_Hall_Ticket_no("00000000")
            self.display_version_code("0")
            
        else:
            self.display_OMR("../images.jpeg")
            self.messagebox()
            
    def skip_img(self):
        l = len(List)
        if l > 0:
            image = ""
            image1 = ""
            image1 = List.pop()
            
            path_to =  "../error/" + image1 
            
            
            print(image1)
            #self.display_OMR(image1)
            image = cv2.imread(image1)
            
            cv2.imwrite(path_to, image)
            
            os.remove(image1)
            self.display_booklet_no("000000")
            self.display_Hall_Ticket_no("00000000")
            self.display_version_code("0")
            self.Next.setEnabled(True)
            self.Exit.setEnabled(False)
            self.next_img()
        else:
            self.display_OMR("../images.jpeg")
            self.display_booklet_no("000000")
            self.display_Hall_Ticket_no("00000000")
            self.display_version_code("0")
            self.messagebox()

if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    ui.load_data()
    ui.next_img()
    #ui.load_all_omr_image()
    Dialog.show()
    
    sys.exit(app.exec_())

