import schedule
import time
import read_sqs
import process_video
import subprocess
import boto3


def job():
    check_queue_message()
    print("I'm working...")


schedule.every(10).seconds.do(job)


def check_queue_message():
    response = read_sqs.receive_message()
    if response is not None and response.body is not None:
        print("cancelling sheduled jobs")
        schedule.CancelJob
        print(response.body)
        process_video.process_message(response.body)
        print("scheduling 10s")
        schedule.every(10).seconds.do(job)
    else:
        delete_instance()
        # terminate_instance()


def delete_instance():
    rec = subprocess.check_output(["ec2metadata", "--instance-id"], universal_newlines=True).strip()
    print("current instance is:", rec)

    client = boto3.client('ec2')
    response = client.stop_instances(
        InstanceIds=[
            rec
        ]
    )
    print(response)


def terminate_instance():
    rec = subprocess.check_output(["ec2metadata", "--instance-id"], universal_newlines=True).strip()
    print("current instance is:", rec)

    client = boto3.client('ec2')
    response = client.terminate_instances(
        InstanceIds=[
            rec
        ]
    )
    print(response)

# schedule.every(10).seconds.do(job)
# schedule.every(1).minute.do(job)
# schedule.every().hour.do(job)

while True:
    schedule.run_pending()
    time.sleep(10)
