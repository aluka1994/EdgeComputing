import boto3
import time


def get_instance_ids():
    instance_id_list = []
    instances = boto3.client('ec2').describe_instances()
    instances = instances['Reservations'][0]['Instances']
    for instance in instances:
        instance_id_list.append(instance['InstanceId'])
    return instance_id_list


def get_starting_running_worker_instance_id():
    instances = boto3.resource('ec2').instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['pending', 'running']}])
    for instance in instances:
        print(instance.id, instance.instance_type)
    return instances


def get_stopped_worker_instance_id():
    return get_worker_instance_id('stopped')


def get_running_worker_instance_id():
    return get_worker_instance_id('running')


def get_worker_instance_id(state="running"):
    instances = boto3.resource('ec2').instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': [state]}])
    for instance in instances:
        print(instance.id, instance.instance_type)
    return instances


user_data = '''#!/bin/bash
Xvfb :1 & export DISPLAY=:1
cd darknet/
touch hello
touch temph
echo hello > temph
python3 startup.py >> hello'''


def start_instance(instance_id):
    client = boto3.client('ec2')
    response = client.start_instances(
        InstanceIds=[
            instance_id
        ]
    )
    print(response)


def stop_instances(instance_id):
    client = boto3.client('ec2')
    response = client.stop_instances(
        InstanceIds=[
            instance_id
        ]
    )
    print(response)


def terminate_instances(instance_id):
    client = boto3.client('ec2')
    response = client.terminate_instances(
        InstanceIds=[
            instance_id
        ]
    )
    print(response)


def stop_instances(number=1):
    stopped_instances = get_running_worker_instance_id()

    i = 0
    list_id = []
    for instance in stopped_instances:
        list_id.append(instance.id)
        # stop_instances(instance.id)
        print("stopping instance:", instance.id)
        i += 1

    if len(list_id) > 0:
        response = boto3.client('ec2').stop_instances(
            InstanceIds=list_id
        )
        # if i >= number:
        #     break


def start_instances(number=1):
    stopped_instances = get_stopped_worker_instance_id()
    # length = len(stopped_instances)
    # if number < length:
    #     length = number

    i = 0
    is_started = 0
    for instance in stopped_instances:
        start_instance(instance.id)
        print("starting instance:", instance.id)
        i += 1
        is_started = 1
        if i >= number:
            break


def create_checking_running_instance(number=1):
    stopped_instances = get_starting_running_worker_instance_id()

    i = 0
    list_id = []
    max_instance = 10
    instance_to_start = number + 1
    for instance in stopped_instances:
        list_id.append(instance.id)
        print("instance list:", instance.id)
        i += 1

    print("running or pending instance : ", len(list_id))
    if len(list_id) > 0:
        instance_to_start = instance_to_start - len(list_id)

    print("max_instance to start : ", max_instance)
    instance_to_start = min(max_instance, instance_to_start)
    print("instance_to_start : ", instance_to_start)
    if instance_to_start > 0:
        create_new_instance(instance_to_start)
    print("check run instance end")


def create_new_instance(number=1):
    ec2 = boto3.resource('ec2')

    # create a new EC2 instance
    instances = ec2.create_instances(
        ImageId='ami-04a142dab9579dcdf',
        MinCount=1,
        MaxCount=number,
        InstanceType='t2.micro',
        KeyName='ec2-keypair',
        UserData=user_data,
        IamInstanceProfile={
            'Arn': 'arn:aws:iam::560084091417:instance-profile/s3_sqs_full_from_ec2'
        }
    )
    print(instances)
