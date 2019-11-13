import cv2
import sqlite3
import pymysql
import numpy as np
kernel = np.ones((5,5),np.uint8)
conn=pymysql.connect(host="localhost",user="root",password="123456",db="omr_python")
cam = cv2.VideoCapture(0)
detector=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
def inorup(id,Name):
    conn=sqlite3.connect('facebase')
    c=conn.cursor()
    cmd="SELECT * FROM people WHERE ID="+str(id)
    c=conn.execute(cmd)
    isRecordExist=0
    for row in c:
        isRecordExist=1
    if(isRecordExist==1):
        cmd="UPDATE people SET name="+str(Name)+" Where ID="+str(id)
    else:
        cmd="INSERT INTO people (id,name) VALUES("+str(Id)+","+str(Name)+")"
    conn.execute(cmd)    
    conn.commit()
    conn.close()
    
def inorup1(id,name):
    cur=conn.cursor()
    query2 = "SELECT * FROM user WHERE id=" + id
    result2 = cur.execute(query2)
    record = cur.fetchall()
    isRecord = 0
    for result in record:
        isRecord = 1
    cur.close()

    if(isRecord == 1):
        cmd="UPDATE user SET name="+  str(name)  + " Where ID=" + id
    else:
        cmd="INSERT INTO user (id,name) VALUES("+ id +"," + '"' +str(name)+ '"' + ")"
    cur=conn.cursor()
    result=cur.execute(cmd)    
    conn.commit()
    
Id=input('enter your id')
name=input('name')
inorup1(Id,name)
sampleNum=0
while(True):
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    alpha = 1.8 # Contrast control (1.0-3.0)
    beta = 0 # Brightness control (0-100)
    img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    #erosion = cv2.erode(gray,kernel,iterations = 1)

    faces = detector.detectMultiScale(img, 1.3, 5)
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        
        #incrementing sample number 
        sampleNum=sampleNum+1
        #saving the captured face in the dataset folder
        cv2.imwrite("dataSet/User."+Id +'.'+ str(sampleNum) + ".png", gray[y:y+h,x:x+w])

        cv2.imshow('frame',img)
        cv2.waitKey(100)
    #wait for 100 miliseconds 
    #if cv2.waitKey(10) & 0xFF == ord('q'):
       # break
    # break if the sample number is morethan 20
    if sampleNum>100:
        cam.release()
        break
#cv2.destroyAllWindows()
