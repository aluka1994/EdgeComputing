import RPi.GPIO as GPIO
import subprocess
import time
import sys
import redis
import datetime
from picamera import PiCamera
from subprocess import Popen, PIPE
from time import sleep
import os, fcntl
import time
import cv2
import datetime
import subprocess
from os import listdir
from os.path import isfile, join

inputPath = '/home/pi/cloudProject/inputFiles'
resultPath = '/home/pi/cloudProject/resultsFiles'
redis_host = "localhost"
redis_port = 6379
redis_password = ""

def startCamera(filename):
    iframe = 0 

    camera = PiCamera()
                    
    #camera.resolution = (416, 416)
    #camera.resolution = (544, 544)
    camera.resolution = (608, 608)
    #camera.resolution = (608, 288) 
    
    camera.start_preview()      # You will see a preview window while recording
    camera.start_recording('/home/pi/cloudProject/inputFiles/' + str(int(filename)) + ".h264") # Video will be saved at desktop
    sleep(5)
    camera.stop_recording()
    camera.stop_preview()
    sleep(2)
    print("Successfully recorded ")

def startCam(filename):
    cmd = "raspivid -o "+inputPath+"/"+filename+" -t 5000"
    process = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    sleep(2)
    print(proc_stdout)
def subprocess_cmd(filename,inputPath,resultPath):
    cmd = './darknet detector demo cfg/coco.data cfg/yolov3-tiny.cfg yolov3-tiny.weights ' +inputPath + "/" + filename  + " > " + resultPath+"/"+filename.split(".")[0] + ".txt"
    process = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print(proc_stdout)

def processResult(ifilename,rfilename):
    rpath = resultPath + "/" + rfilename

def inputRedis(filename):
    flag = 0
    try:
        ifilename = filename
        ipath = inputPath
        rpath = resultPath
        key = filename
        keyValue = str(ifilename + "," + ipath + "," + rpath)
        rcon = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
        rcon.set(str(key),keyValue)
        # step 5: Retrieve the hello message from Redis
        msg = rcon.get(str(key))
        print(msg)
        flag = 1
    except Exception as e:
        print(e)

    if flag == 1:
        return "success"
    else:
        return "failure" 

#if __name__ == '__main__':
#    '''
#    vfiles = [f for f in listdir(inputPath) if isfile(join(inputPath, f))]
#    for value in vfiles:
#    	subprocess_cmd(value,inputPath,resultPath)
#    exit(1)
#    '''
while True:
    sensor = 12

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(sensor, GPIO.IN)

    on = 0 
    off = 0 
    flag = 0 
    while flag == 0:
        i=GPIO.input(sensor)
        if i == 0:
            if flag == 1:
                off = time.time()
                diff = off - on
                print 'time: ' + str(diff%60) + ' sec'
                print ''
                flag = 0
            print "No intruders"
            time.sleep(5)
        elif i == 1:
            if flag == 0:
                print "Intruder detected"
                on = time.time()
                flag = 1
                ep = datetime.datetime(1970,1,1,0,0,0)
                filename = str(int((datetime.datetime.utcnow()- ep).total_seconds()))
                resultFileName = filename
                startCam(filename+".h264")
                filename = filename + ".h264"
                inputRedis(filename)
