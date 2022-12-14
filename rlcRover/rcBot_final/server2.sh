#!/bin/bash



python3 /home/orangepi/rlcRover/rcBot_final/servercam2.py &

### To sleep for 1.5 seconds: ##
sleep 20
python3 /home/orangepi/rlcRover/rcBot_final/robotcam2.py &
