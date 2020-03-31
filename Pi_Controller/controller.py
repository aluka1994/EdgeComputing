import subprocess
import sys
import redis
import threading
import logging
import boto3
import threading
import sys
import os
import json
from time import time, sleep
from botocore.exceptions import ClientError
from aws_credentials import *
from boto3.s3.transfer import TransferConfig
from os import listdir
from os.path import isfile, join
REGION = "us-east-1"

inputFilesPath = '/home/pi/cloudProject/inputFiles'
resultsFilesPath = '/home/pi/cloudProject/resultsFiles'

redis_host = "localhost"
redis_port = 6379
redis_password = ""


ss3thread = []


def isTreadAlive(threads):
	for t in threads:
		if t.isAlive():
			return 1
	return 0

def processResult(filename):
    tfile = filename.split(".")[0]
    filename = resultsFilesPath+"/"+filename
    file1 = open(filename, "r")
    data = file1.readlines()
    file1.close()

    wt = ""
    for value in data:
        wt += (value.strip("\n")).strip("\x1b[2J\x1b[1;H")

    pt = str(wt)
    pt = pt.split("FPS:")
    rResult = []
    pt = pt[1:]

    file1 = open(filename, "w")
    #tfile = filename.split(".")[0]
    word_list = []

    for value in pt:
        ty = value.split("Objects:")
        if ty[1] != "":
            ty = ty[1].split("%")
            ty = ty[:-1]
            for tvalue in ty:
                if tvalue != "":
                    file1.write(str(tfile) + "," + str(tvalue) + "%" + "\n")
                    new = tvalue.split(":")
                    word_list.append(new[0])
                    # rResult.append(["temp",str(tvalue)+"%"])
                else:
                    file1.write(str(tfile) + "," + "No object detected" + "\n")
                    # rResult.append(["temp","No object detected"])
        else:
            file1.write(str(tfile) + "," + "No object detected" + "\n")

        file1.write("\n")
    file1.close()
    final_list = set(word_list)
    line = "Final results: "
    if len(final_list) > 0:
        line += ','.join(final_list)
    else:
        line += "No object detected \n"

    with open(filename, "r+") as f:
        old = f.read()  # read everything in the file
        f.seek(0)  # rewind
        f.write(line + "\n\n" + old)  #
        f.close()
class ProgressPercentage(object):

	def __init__(self, filename):
		self._filename = filename
		self._size = float(os.path.getsize(filename))
		self._seen_so_far = 0 
		self._lock = threading.Lock()

	def __call__(self, bytes_amount):
		# To simplify, assume this is hooked up to a single filename
		with self._lock:
			self._seen_so_far += bytes_amount
			percentage = (self._seen_so_far / self._size) * 100 
			sys.stdout.write(
				"\r%s  %s / %s  (%.2f%%)" % ( 
					self._filename, self._seen_so_far, self._size,
					percentage))
			sys.stdout.flush()

def createSQSMessage(video_filename,result_filename,processed,time):
		message = {}
		message['video_filename'] = video_filename
		message['result_filename'] = result_filename
		message['processed'] = processed
		message['time'] = time
		return json.dumps(message)


def uploadFileS3(filename,bucketName):
		s3_client = boto3.client(
				's3',\
				aws_access_key_id=aws_access_key_id,\
				aws_secret_access_key=aws_secret_access_key,\
				aws_session_token=aws_session_token,\
				region_name=REGION
		)
		config = TransferConfig(multipart_threshold=1024 * 25, max_concurrency=10,
								multipart_chunksize=1024 * 25, use_threads=True)
		file = filename
		key = filename
		s3_client.upload_file(file, bucketName, key,
					ExtraArgs={'ACL': 'public-read', 'ContentType': 'video/mp4'},
					Config=config,
					Callback=ProgressPercentage(file)
		)


def uploadS3Input(myfile,bucketName,object_name=None):
		print(" ---- s3 upload")
		s3_client = boto3.client('s3',
				aws_access_key_id=aws_access_key_id,
				aws_secret_access_key=aws_secret_access_key,
				aws_session_token=aws_session_token,
				region_name=REGION
		)

		if object_name is None:
				object_name = myfile

		try:
				message = {}
				response = s3_client.upload_file(inputFilesPath+"/"+myfile,bucketName,object_name, Callback=ProgressPercentage(inputFilesPath+"/"+myfile))
				print(" Uploading video file : " + str(myfile)  + " : " + str(response))
				message = createSQSMessage(myfile,"noresultfile",False,myfile.split('.')[0])
				sqs_client = boto3.client(
						'sqs',
						aws_access_key_id=aws_access_key_id,
						aws_secret_access_key=aws_secret_access_key,
						aws_session_token=aws_session_token,
						region_name = REGION
				)

				response = sqs_client.list_queues()
				queueUrl = response['QueueUrls'][0]
				response = sqs_client.send_message(
						QueueUrl=queueUrl,
						DelaySeconds=2,
						MessageBody=message
				)
				print("Message has been sent to queue : " + str(queueUrl) + " : " + str(response['MessageId']))

		except ClientError as e:
				logging.error(e)
				return False
		return True

def uploadPIResult(myfile, bucketName, object_name=None):
		print("uplaod started")
		s3_client = boto3.client(
				's3',
				aws_access_key_id=aws_access_key_id,
				aws_secret_access_key=aws_secret_access_key,
				aws_session_token=aws_session_token,
				region_name=REGION
		)
		myfile = myfile + ".txt"
		if object_name is None:
				object_name = myfile

		try:
				message = {}
				response = s3_client.upload_file(resultsFilesPath + "/" + myfile, bucketName, object_name,
												 Callback=ProgressPercentage(resultsFilesPath + "/" + myfile))
				print(" Uploading the result file generated on PI : " + str(myfile) + " : " + str(response))
		except ClientError as e:
				logging.error(e)
				return False
		return True


def uploadPIInput(myfile, bucketName, object_name=None):
		print("uplaod started")
		s3_client = boto3.client(\
				's3',\
				aws_access_key_id=aws_access_key_id,\
				aws_secret_access_key=aws_secret_access_key,\
				aws_session_token=aws_session_token,\
				region_name=REGION
		)

		if object_name is None:
				object_name = myfile

		try:
				message = {}
				response = s3_client.upload_file(inputFilesPath + "/" + myfile, bucketName, object_name,
												 Callback=ProgressPercentage(inputFilesPath + "/" + myfile))
				print(" Uploading the input video file processed on PI : " + str(myfile) + " : " + str(response))
		except ClientError as e:
				logging.error(e)
				return False
		return True

def subprocess_cmd(filename,inputPath,resultPath):
	#cmd = "cd ../../darknet"
	#process = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True)
	#proc_stdout = process.communicate()[0].strip()
	#print(proc_stdout)
	cmd = './darknet detector demo cfg/coco.data cfg/yolov3-tiny.cfg yolov3-tiny.weights ' +inputPath + "/" + filename  + " > " + resultPath+"/"+filename + ".txt"
	process = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True)
	proc_stdout = process.communicate()[0].strip()
	print(proc_stdout)

def checkKeys():
	rcon = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
	#length = rcon.dbsize()
	tyKeys = rcon.keys()
	return tyKeys

def splitCount(x):
	# ec2 = 26 ( 7 mins)
	# pi = 20 ( 7 mins )
	picount = 0
	#print(x)
	ec2count = 0
	while(x>0):
		#print(x)
		if(x>7):
			picount += 7
		else:
			picount += x

		#if(x>10)
		x = x-7

		if(x>18):
			ec2count += 18
		elif(x>0 and x < 18):
			ec2count += x

		x = x-18
	
	print(picount,ec2count)
	return [picount,ec2count]

#tthread = threading.Thread(target=upload,args=(fname,bucketName,inputResultMapping,))
if __name__ == '__main__':
	#main()
		
	while True:
		start = time()
		try:
			dkeys = list(checkKeys())
			tlen = len(dkeys)
			gh = tlen
			sc = splitCount(tlen)
			bucketName = "project-cloud-r3"
			bucketName_result = "project-cloud-r3-result"
			#bucketName = "my-first-s3-bucket-198bd354-2641-44f6-b5ba-884f5f87c9fa"
			if(gh > 7):
				print("Keys from Redis Queue : ")
				print(dkeys)
				pikeys = dkeys[0:sc[0]]
				s3keys = dkeys[sc[0]:sc[0]+sc[1]]
				piThreads = []
				s3Threads = []
				for value in s3keys:
					#s3 uploading.
					rcon = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
					msg = rcon.get(value)
					rcon.delete(value)
					value = msg.split(",")
					tthread = threading.Thread(target=uploadS3Input,args=(value[0],bucketName,))
					tthread.start()
					s3Threads.append(tthread)
					sleep(1)

				print(" All S3 uploads are done. Now processing on PI will start ")
				
				for value in pikeys:
					rcon = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
					msg = rcon.get(value)
					rcon.delete(value)
					value = msg.split(",")

					tthread = threading.Thread(target=subprocess_cmd,args=(value[0],value[1],value[2],))
					tthread.start()

					tthread_s4 = threading.Thread(target=uploadPIInput,args=(value[0],bucketName,))
					tthread_s4.start()
					piThreads.append(tthread_s4)
					while(tthread.isAlive()):
						continue
					#sleep(30)
					processResult((value[0])+".txt")
					tthread_s3 = threading.Thread(target=uploadPIResult,args=((value[0]),bucketName_result,))
					tthread_s3.start()
					piThreads.append(tthread_s3)

				while(isTreadAlive(s3Threads)):
					continue
				while(isTreadAlive(piThreads)):
					continue

				for value in s3keys:
					os.remove(inputFilesPath+"/"+value)

				for value in pikeys:
					os.remove(inputFilesPath+"/"+value)
					os.remove(resultsFilesPath+"/"+value+".txt")

				s3keys
				piThreads = []
				s3Threads=[]
			elif(gh>0 and gh<7):
				piThreads = []
				print(dkeys)
				#for value in dkeys:
				tfile = dkeys[0]
				rcon = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
				msg = rcon.get(dkeys[0])
				rcon.delete(dkeys[0])
				msg = msg.split(',')
				print(msg)
				filename,inputPath,resultPath = msg[0],msg[1],msg[2]
				tthread = threading.Thread(target=subprocess_cmd,args=(filename,inputPath,resultPath,))
				#threads_s3.append(tthread_s3)
				tthread.start()
				#threads.append(tthread)
				tthread_s4 = threading.Thread(target=uploadPIInput,args=(msg[0],bucketName,))
				tthread_s4.start()
				piThreads.append(tthread_s4)
				while(tthread.isAlive()):
					continue

				processResult((msg[0])+".txt")
				tthread_s3 = threading.Thread(target=uploadPIResult,args=((msg[0]),bucketName_result,))
				tthread_s3.start()
				piThreads.append(tthread_s3)

				while(isTreadAlive(piThreads)):
					continue
					
				os.remove(inputFilesPath+"/"+tfile)
				os.remove(resultsFilesPath+"/"+tfile+".txt")
				piThreads=[]

		except Exception as e:
			raise e

		end = time()-start
		sleep(10)
		print("final time : " + str(end))
		#time.sleep(15)#sleep(10)
		#sleep(10)
