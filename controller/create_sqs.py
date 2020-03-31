import boto3


def list_queue():
    sqs = boto3.client('sqs')

    response = sqs.list_queues()
    print(response)


def list_queue_name(name="testProject"):
    sqs = boto3.resource('sqs')

    response = sqs.get_queue_by_name(QueueName='testProject')
    print(response.url)
    print("VisibilityTimeout: ", response.attributes.get('VisibilityTimeout'))
    print("ApproximateNumberOfMessages: ", response.attributes.get('ApproximateNumberOfMessages'))
    print("ApproximateNumberOfMessagesNotVisible: ", response.attributes.get('ApproximateNumberOfMessagesNotVisible'))
    print(response)
    return response
