
#Client(raspberry pi) side:
1) Motion sensor: when a motion is sensed by a sensor, a command to record video for 5 seconds starts. After recording the video, a message is sent to redis queue that there is an input video to process. Before running this, create a cloudProject/inputFiles, cloudProject/resultFiles folders to store the data.Place the survillence_cc.py file in the darknet folder of PI and then run the following command:

python survillence_cc.py

2) Redis queue: We are maintaining this queue to see what all inputs to be processed. This queue is a key value store and it will be easy for retrieval.

Installation of redis queue on PI: ( https://redis.io/download )
$ wget http://download.redis.io/releases/redis-5.0.8.tar.gz
$ tar xzf redis-5.0.8.tar.gz
$ cd redis-5.0.8
$ make
$ src/redis-server ( to start the server )

3) Pi Controller: Now based on the input size of the queue we will decide the number of videos to process on Pi and cloud. Ideally for darkent to process a 5 seconds video takes 30 - 40 seconds to process and get the result.  Similarly for darknet on aws ec2 it takes 4-5 minutes to process a single 5 seconds to process. So, if the queue size is greater than 7, then we send the remaining ( max 18 ) videos to the cloud using parallel processing.

Copy the controller.py to darknet folder. We have to install python3 on PI to run the controller.py because we are using python boto3 to access the results. 

Please follow this link for the installation of python-3 on pi : installation
Now install virtualenv and activate the virtualenv.
After that  install the dependencies boto3 using the command pip3 install boto3
python controller.py
This will run in a loop and checks if there are any messages in the queue and based on this it will decide whether to process the videos on PI or cloud.

====

#Server side:

There are two main programs: 1) controller 2) worker

1) controller: 
Controller project contains logic for controller code. starup.py is the entry point for the project and running that file starts a scheduler which polls SQS queue size every 20 seconds. We can start controller using following commands:

cd controller
pip3 install -r requirements.txt
python3 startup.py

2) worker: 
The worker project contains logic for worker code. Entry point for the project is starup.py and running that file starts a scheduler which reads messages from SQS queue and based on key name it’ll download a video file from s3 bucket. After downloading the video it’ll run darknet detection command on that video and upload results to s3 bucket. After finishing one video, the scheduler will check for a new message in the SQS queue again and if it finds the message then it’ll process that or if the queue is empty then the worker node will terminate itself. We can manually start worker using following commands:

cd worker
pip3 install -r requirements.txt
python3 startup.py

For creating a worker AMI image first create an EC2 instance from darknet AMI given to us then deploy worker code to the darknet folder and put the startup script(starup.sh) given in the project to the home directory. Add script to crontab: using “crontab -e” add following line to crontab:
@reboot starup.sh
After that form AWS dashboard select that particular instance and create AMI. Use that AMI id to the controller project code in create_instace.py file.

