import redis




redis_host = "localhost"
redis_port = 6379
redis_password = ""
inputPath = '/home/pi/cloudProject/inputFiles'
resultPath = '/home/pi/cloudProject/resultsFiles'

'''
1584878976.h264
-rw-r--r-- 1 pi pi 10947542 Mar 22 12:10 1584878997.h264
-rw-r--r-- 1 pi pi 10993494 Mar 22 12:10 1584879022.h264
-rw-r--r-- 1 pi pi 11012416 Mar 22 12:10 1584879027.h264
-rw-r--r-- 1 pi pi 10974794 Mar 22 12:10 1584879032.h264
-rw-r--r-- 1 pi pi 11019633 Mar 22 12:10 1584879038.h264
-rw-r--r-- 1 pi pi 10998090 Mar 22 12:10 1584879043.h264
-rw-r--r-- 1 pi pi 10921950 Mar 22 12:10 1584879048.h264
-rw-r--r-- 1 pi pi 11015255 Mar 22 12:10 1584879053.h264
-rw-r--r-- 1 pi pi 10997690 Mar 22 12:11 1584879059.h264
-rw-r--r-- 1 pi pi 11005207 Mar 22 12:11 1584879064.h264
-rw-r--r-- 1 pi pi 10512281 Mar 22 12:12 1584879130.h264
-rw-r--r-- 1 pi pi  9217914 Mar 22 12:12 1584879145.h264
-rw-r--r-- 1 pi pi 10447728 Mar 22 12:12 1584879150.h264
-rw-r--r-- 1 pi pi  9523433 Mar 22 12:12 1584879156.h264
-rw-r--r-- 1 pi pi  7737661 Mar 22 12:12 1584879162.h264
-rw-r--r-- 1 pi pi 10118830 Mar 22 12:13 1584879187.h264
-rw-r--r-- 1 pi pi  8670087 Mar 22 12:13 1584879192.h264
-rw-r--r-- 1 pi pi  5075035 Mar 22 12:13 1584879197.h264
-rw-r--r-- 1 pi pi  9374172 Mar 22 12:13 1584879203.h264
-rw-r--r-- 1 pi pi   220429 Mar 22 12:13 1584879208.h264
-rw-r--r-- 1 pi pi  2150400 Mar 22 12:34 1584880458.h264
-rw-r--r-- 1 pi pi        0 Mar 22 12:34 1584880464.h264
-rw-r--r-- 1 pi pi        0 Mar 22 12:34 1584880469.h264
-rw-r--r-- 1 pi pi 10386080 Mar 22 12:35 1584880551.h264
-rw-r--r-- 1 pi pi  7587524 Mar 22 12:36 1584880556.h264
-rw-r--r-- 1 pi pi 11055470 Mar 22 12:36 1584880562.h264
-rw-r--r-- 1 pi pi 10794623 Mar 22 12:36 1584880587.h264
-rw-r--r-- 1 pi pi  9170230 Mar 22 12:36 1584880592.h264
-rw-r--r-- 1 pi pi 10661659 Mar 22 12:36 1584880602.h264
-rw-r--r-- 1 pi pi  9841961 Mar 22 12:36 1584880608.h264
-rw-r--r-- 1 pi pi 10954183 Mar 22 12:37 1584880642.h264
-rw-r--r-- 1 pi pi 10957812 Mar 22 12:37 1584880647.h264
-rw-r--r-- 1 pi pi 10927968 Mar 22 12:37 1584880653.h264
-rw-r--r-- 1 pi pi 10416264 Mar 22 12:37 1584880659.h264
-rw-r--r-- 1 pi pi  7985470 Mar 22 12:37 1584880664.h264

'''
key1 = ['testvideo1.h264','testvideo2.h264','testvideo3.h264',\
'testvideo4.h264','testvideo5.h264','testvideo6.h264','testvideo7.h264','testvideo8.h264',\
'testvideo9.h264','testvideo10.h264']
rcon = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
key2= ['dog.jpg','eagle.jpg','experiment_1.png','experiment2.png','experiment3.png','experiment4.png',\
'giraffe.jpg','horses.jpg','person.jpg','scream.jpg']
#for value in key2:
#	rcon.set(str(value),str(value + "," + inputPath + "," + resultPath))

for value in key1[0:10]:
	rcon.set(str(value),str(value + "," + inputPath + "," + resultPath))
		
length = rcon.dbsize()
print("length of queue : " + str(length))
dd = rcon.keys()
print("keys of db")
print(dd)

print("len of keysd")
print(len(dd))


for value in dd:
	print(value)
	
print("splitting")
print(dd[0:5])
