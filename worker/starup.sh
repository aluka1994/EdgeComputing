#!/bin/bash
Xvfb :1 & export DISPLAY=:1
cd ~/darknet/
DATE=$(date +'%F %H:%M:%S')
touch test.txt
echo "Current date and time: $DATE" > test.txt
touch hello
python3 startup.py >> hello

