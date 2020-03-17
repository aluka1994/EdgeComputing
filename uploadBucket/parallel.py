
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

inputFilesPath = '/Users/alukaraju/PycharmProjects/cloudcc/inputFiles'
resultsFilesPath = '/Users/alukaraju/PycharmProjects/cloudcc/resultsFiles'

def isTreadAlive(threads):
  for t in threads:
    if t.isAlive():
      return 1
  return 0

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


'''
	Multipart uploading of the file to s3.
'''
def uploadFileS3(filename,bucketName):
	s3_client = boto3.client(
		's3',
		aws_access_key_id=aws_access_key_id,
		aws_secret_access_key=aws_secret_access_key,
		aws_session_token=aws_session_token,
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


'''
	Simple upload of the file to s3.
'''
def upload(myfile,bucketName,inputResultMapping,object_name=None):
	s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token,
	)
	
	if object_name is None:
		object_name = myfile
	
	try:
		message = {}
		response = s3_client.upload_file(inputFilesPath+"/"+myfile,bucketName,object_name, Callback=ProgressPercentage(inputFilesPath+"/"+myfile))
		print(" Uploading video file : " + str(myfile)  + " : " + str(response))
		if inputResultMapping[myfile] != "nofile":
			resultfile = inputResultMapping[myfile]
			response = s3_client.upload_file(resultsFilesPath+"/"+resultfile,bucketName,resultfile, Callback=ProgressPercentage(resultsFilesPath+"/"+resultfile))
			print(" Uploading result file : " + str(resultfile)  + " : " + str(response))
			message = createSQSMessage(myfile,resultfile,True,"1234")
		else:
			message = createSQSMessage(myfile,"nofile",False, "1234")
		
		sqs_client = boto3.client(
			'sqs',
			aws_access_key_id=aws_access_key_id,
			aws_secret_access_key=aws_secret_access_key,
			aws_session_token=aws_session_token,
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

def main(inputPath,resultsPath):
	start = time()
	bucketName = "my-first-s3-bucket-198bd354-2641-44f6-b5ba-884f5f87c9fa"
	inputFiles = [f for f in listdir(inputPath) if isfile(join(inputPath, f))]
	resultsFiles = [f for f in listdir(resultsPath) if isfile(join(resultsPath, f))]
	inputResultMapping = {}
	
	for fname in inputFiles:
		inputResultMapping[fname] = "nofile"
	
	print(" ----- Input Files ------- ")
	print(inputFiles)
	
	print(" -------- Result Files -----------")
	print(resultsFiles)
	
	for fname in resultsFiles:
		tfname = fname.split(".")[0] + ".mkv"
		if tfname in inputResultMapping:
				inputResultMapping[tfname] = fname
		
	print(" ----- Input - result Mapping Files ------ ")
	print(inputResultMapping)

	print("###### InputFiles started Uploading start  #######")
	threads = []
	for fname in inputFiles:
		tthread = threading.Thread(target=upload,args=(fname,bucketName,inputResultMapping,))
		#print(tthread)
		threads.append(tthread)
		tthread.start()
		
	print("###### InputFiles started Uploading Complete  #######")
	flag = 1
	while (flag):
		#time.sleep(0.5)
		flag = isTreadAlive(threads)
		
	endtime = time()-start
	print(" ### Program end ## : " + str(endtime))
	
if __name__ == '__main__':
	main(inputFilesPath,resultsFilesPath)