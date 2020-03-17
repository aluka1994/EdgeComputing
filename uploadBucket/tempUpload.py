
import logging
import boto3
from botocore.exceptions import ClientError
import os
import sys
import threading
from boto3.s3.transfer import TransferConfig
from multiprocessing import Pool

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


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')

    try:
        response = s3_client.upload_file(file_name, bucket, object_name,Callback=ProgressPercentage(file_name))
    except ClientError as e:
        logging.error(e)
        return False
    return True

def create_bucket(bucket_name, region=None):
	"""Create an S3 bucket in a specified region

	If a region is not specified, the bucket is created in the S3 default
	region (us-east-1).

	:param bucket_name: Bucket to create
	:param region: String region to create bucket in, e.g., 'us-west-2'
	:return: True if bucket created, else False
	"""

	# Create bucket
	try:
		if region is None:
			s3_client = boto3.client('s3')
			s3_client.create_bucket(Bucket=bucket_name)
		else:
			s3_client = boto3.client('s3', region_name=region)
			location = {'LocationConstraint': region}
			s3_client.create_bucket(Bucket=bucket_name,
									CreateBucketConfiguration=location)
	except ClientError as e:
		logging.error(e)
		return False
	return True


def listBuckets(response):
	TotalBuckets = []
	for bucket in response['Buckets']:
		TotalBuckets.append(bucket["Name"])
	return TotalBuckets

def checkBucketExisted(s3):
	response = s3.list_buckets()
	#print(f'  {bucket["Name"]}')
	TotalBuckets = listBuckets(response)
	print(" Total No of Buckets : " + str(len(TotalBuckets)))

	if(len(TotalBuckets) < 0):
		response = create_bucket("cloud_bucket")

	if response == True:
		return listBuckets(s3.list_buckets())

	return TotalBuckets






if __name__ == '__main__':
	# Retrieve the list of existing buckets
	# s3 = boto3.client('s3')
	# bucketNames = checkBucketExisted(s3)
	# print(bucketNames)
	#
	# upload_file("/Users/alukaraju/PycharmProjects/cloudcc/ty/jt1.mkv",bucketNames[0],"firstfile")
	# # p = Pool(5)
	# # (p.map(upload_file, [("/Users/alukaraju/PycharmProjects/cloudcc/ty/jt1.mkv",bucketNames[0],"firstfile"), ("/Users/alukaraju/PycharmProjects/cloudcc/ty/jt1.mkv",bucketNames[0],"firstfile"), ("/Users/alukaraju/PycharmProjects/cloudcc/ty/jt1.mkv",bucketNames[0],"firstfile")]))
	
	# Create SQS client
	sqs = boto3.client('sqs')
	
	# List SQS queues
	response = sqs.list_queues()
	
	print(response['QueueUrls'][0])
	
	'''
		print(" ### Parallel Threads uploading the file time start #### ")
		start = time()
		for fname in filenames:
			t = threading.Thread(target=upload, args=(fname,"my-first-s3-bucket-198bd354-2641-44f6-b5ba-884f5f87c9fa",)).start()

		t2 = time()-start
		print("time taken to upload : " + str(t2))
		print(" ### Parallel Threads uploading the file time End #### ")
		'''
	'''
	print(" ### Single File upload the file time start #### ")
	start = time()
	for fname in filenames:
		upload(fname,"my-first-s3-bucket-198bd354-2641-44f6-b5ba-884f5f87c9fa",fname)
	t2 = time() - start
	print("time taken to upload : " + str(t2))
	print(" ### Single File upload the file time End #### ")

	'''
	'''
	start = time()

	for fname in filenames:
		t = threading.Thread(target=uploadFileS3,args=(fname, "my-first-s3-bucket-198bd354-2641-44f6-b5ba-884f5f87c9fa",)).start()
		#uploadFileS3(fname,"my-first-s3-bucket-198bd354-2641-44f6-b5ba-884f5f87c9fa")

	t2 = time() - start

	print("time taken to upload 2 files : " + str(t2))
	'''
