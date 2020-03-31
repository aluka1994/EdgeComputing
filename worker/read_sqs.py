import boto3


def receive_message(name="testProject"):
    sqs = boto3.resource('sqs')
    queue = sqs.Queue('https://queue.amazonaws.com/560084091417/testProject')
    response = queue.receive_messages(
        # QueueUrl='https://queue.amazonaws.com/560084091417/testProject',
        AttributeNames=[
            'All'
        ],
        MaxNumberOfMessages=1,
        VisibilityTimeout=120,
        WaitTimeSeconds=2
    )
    print(response)
    for message in response:
        message.delete()
        return message


def delete_message(queue, receiptHandle):
    sqs = boto3.client('sqs')
    response = sqs.delete_message(
        QueueUrl=queue,
        ReceiptHandle=receiptHandle
    )
    print(response)
