import json
import time

def processResult(filename):
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
                    file1.write(str(tfile) + "," + str(tvalue) + "%" + "\n")
                    new = tvalue.split(":")
                    word_list.append(new[0])
                    # rResult.append(["temp",str(tvalue)+"%"])
                else:
                    file1.write(str(tfile) + "," + "No object detected" + "\n")
                    # rResult.append(["temp","No object detected"])
        else:
            file1.write(str(tfile) + "," + "No object detected" + "\n")

        file1.write("\n")
    file1.close()
    final_list = set(word_list)
    line = "Final results: "
    if len(final_list) > 0:
        line += ','.join(final_list)
    else:
        line += "No object detected \n"

    with open(filename, "r+") as f:
        old = f.read()  # read everything in the file
        f.seek(0)  # rewind
        f.write(line + "\n\n" + old)  # 



def processResultty(filename):
        fpath = filename
        file1 = open(fpath,"r")
        data =  file1.readlines()
        file1.close()

        wt = ""
        for value in data:
                wt +=  (value.strip("\n")).strip("\x1b[2J\x1b[1;H")

        pt  = str(wt)
        pt = pt.split("FPS:")
        rResult = []
        pt = pt[1:]

        finalResult = []
        fr = []

        tfile = filename.split(".")[0]
        for value in pt:
                ty = value.split("Objects:")
                if ty[1] != "":
                        ty =ty[1].split("%")
                        ty = ty[:-1]
                        for tvalue in ty:
                                if tvalue!="":
                                        finalResult.append(str(tfile)+ "," + str(tvalue)+"%")
                                        ty = str(tvalue).split(":")[0]
                                        if ty not in fr:
                                                fr.append(str(ty))
                                        #rResult.append(["temp",str(tvalue)+"%"])
                                else:
                                        finalResult.append(str(tfile)+ "," + "No object detected")
                                        #file1.write(str(tfile)+ "," + "No object detected" + "\n")
                                        #rResult.append(["temp","No object detected"])
                else:
                        finalResult.append(str(tfile)+ "," + "No object detected")
                finalResult.append("\n")

        file1 = open(fpath,"w")
        df = str(tfile)+".h264"
        strd=""
        strd = ','.join(fr)

        if(strd == ""):
                strd += "No object detected"

        strd = df+ ","+ strd
        file1.write(strd + "\n\n")
        for value in finalResult:
                file1.write(value)
                file1.write("\n")
        file1.close()

def processResulttt(filename):
	fpath =  filename
	file1 = open(fpath,"r") 
	data =  file1.readlines()
	file1.close()

	wt = ""
	for value in data:
		wt +=  (value.strip("\n")).strip("\x1b[2J\x1b[1;H")

	pt  = str(wt)
	pt = pt.split("FPS:")
	rResult = []
	pt = pt[1:]

	finalResult = []
	fr = []
	 
	tfile = filename.split(".")[0]
	for value in pt:
		ty = value.split("Objects:")
		if ty[1] != "":
			ty =ty[1].split("%")
			ty = ty[:-1]
			for tvalue in ty:
				if tvalue!="":
					finalResult.append(str(tfile)+ "," + str(tvalue)+"%")
					ty = str(tvalue).split(":")[0]
					if ty not in fr:
						fr.append(str(ty))
					#rResult.append(["temp",str(tvalue)+"%"])
				else:
					finalResult.append(str(tfile)+ "," + "No object detected")
					#file1.write(str(tfile)+ "," + "No object detected" + "\n")
					#rResult.append(["temp","No object detected"])
		else:
			finalResult.append(str(tfile)+ "," + "No object detected")
		finalResult.append("\n")

	file1 = open(fpath,"w")
	strd = ""

	strd = ','.join(fr)

	if(strd == ""):
		strd += "No object detected"

	file1.write(strd + "\n\n")
	for value in finalResult:
		file1.write(value)
		file1.write("\n")
	file1.close()

if __name__ == '__main__':
	processResult('result.txt')