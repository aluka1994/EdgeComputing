import boto3
import json
import botocore
import subprocess

BUCKET_NAME = 'project-cloud-r3'


def process_message(body):
    message_dict = json.loads(body)

    if message_dict['video_filename'] is not None:
        print(message_dict['video_filename'])
        download_file(message_dict['video_filename'])
        run_darknet(file=message_dict['video_filename'])


def download_file(key):
    s3 = boto3.resource('s3')

    try:
        s3.Bucket(BUCKET_NAME).download_file(key, key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise


def upload_file(key):
    s3 = boto3.resource('s3')

    try:
        processResult("stdout.txt", key)
        s3.Bucket('project-cloud-r3-result').upload_file("stdout.txt", key + ".txt")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise


def run_darknet(file):
    print("starting dark net")
    video = 'video.h264'
    #    video = 'predictions.jpg'
    if file is not None:
        video = file
    #    command = "./darknet detector demo cfg/coco.data cfg/yolov3-tiny.cfg yolov3-tiny.weights "+file+" > output.txt"
    #    print(command)
    #    os.system(command)
    #     subprocess.Popen(['./darknet', 'detector', 'demo', 'cfg/coco.data', 'cfg/yolov3-tiny.cfg', 'yolov3-tiny.weights',
    #                      video]).read()

    with open("stdout.txt", "wb") as out, open("stderr.txt", "wb") as err:
        print("starting subprocess")
        # subprocess.check_output(['./darknet', 'detector', 'demo', 'cfg/coco.data', 'cfg/yolov3-tiny.cfg',
        #                          'yolov3-tiny.weights', video])
        proc = subprocess.Popen(
            ['./darknet', 'detector', 'demo', 'cfg/coco.data', 'cfg/yolov3-tiny.cfg', 'yolov3-tiny.weights', video],
            stdout=out, stderr=err)
        proc.wait()

    print("uploading file")
    upload_file(video)


def processResult(filename, key):
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
    tfile = filename.split(".")[0]
    word_list = []

    for value in pt:
        ty = value.split("Objects:")
        if ty[1] != "":
            ty = ty[1].split("%")
            ty = ty[:-1]
            for tvalue in ty:
                if tvalue != "":
                    file1.write(str(key) + "," + str(tvalue) + "%" + "\n")
                    new = tvalue.split(":")
                    word_list.append(new[0])
                    # rResult.append(["temp",str(tvalue)+"%"])
                else:
                    file1.write(str(key) + "," + "No object detected" + "\n")
                    # rResult.append(["temp","No object detected"])
        else:
            file1.write(str(key) + "," + "No object detected" + "\n")

        file1.write("\n")
    file1.close()
    final_list = set(word_list)
    line = "Final results: "
    if len(final_list) > 0:
        for word in final_list:
            line += word + ","
    else:
        line += "No object detected \n"

    with open(filename, "r+") as f:
        old = f.read()  # read everything in the file
        f.seek(0)  # rewind
        f.write(line + "\n\n" + old)  # write the new line before
