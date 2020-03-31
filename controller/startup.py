import schedule
import time
import create_sqs
import create_server


def job():
    check_queue_to_create_instance()
    print("I'm working...")


def check_queue_to_create_instance():
    response = create_sqs.list_queue_name()
    no_of_messages = int(response.attributes.get('ApproximateNumberOfMessages'))
    print("no_of_messages: ", no_of_messages)
    create_server.create_new_instance(1)
    if no_of_messages > 0:
        schedule.CancelJob
        no_of_instance = int(no_of_messages)
        # no_of_instance = 1
        print("no of instances: ", no_of_instance)
        if no_of_instance > 10:
            no_of_instance = 10
            print("no of instances greater that 5")
        print("new no of instances: ", no_of_instance)
        create_server.create_checking_running_instance(number=no_of_instance)
        time.sleep(20)
    else:
        print("no of messages are less than or equal to 0")
    print("create_instance end")


schedule.every(10).seconds.do(job)
# schedule.every(1).minute.do(job)
# schedule.every().hour.do(job)

while True:
    schedule.run_pending()
    time.sleep(10)
