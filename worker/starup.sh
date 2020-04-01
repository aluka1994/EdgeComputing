Xvfb :1 & export DISPLAY=:1
cd darknet
touch testresult
python3 starup.sh > testresult
