'''
    Program to get live stream from secondary web cam and click a picture on press of a button
    This script performs following tasks:
    1> The first argument is the filename for the capture
        1.1> .jpg is appended at the end of the filename
    2> The second argument decides if the script should wait for a key press or capture the shot as soon as the script is run
    3> The images are saved in the TARGET_DIRECTORY directory
'''

import os
import sys
import cv2
import shutil

# Directory where the image will be stored
TARGET_DIRECTORY = "img/"

# Checking arguments
if len(sys.argv) != 3:
    print "Correct Usage : python camera.py <DesiredFilename> <doStop>"
    exit()

# the name for the file to be saved
filename = sys.argv[1] + ".jpg"

# 1 => to use secondary (USB) web camera
cap = cv2.VideoCapture(1)

while (True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Display the resulting frame
    cv2.imshow('frame', frame)

    # for auto click
    if sys.argv[2] == '0':
        cv2.imwrite(filename, frame)
        if not os.path.exists(TARGET_DIRECTORY):
            os.makedirs(TARGET_DIRECTORY)
        shutil.move(filename, TARGET_DIRECTORY + filename)
        break

    # Save the frame and quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.imwrite(filename, frame)
        if not os.path.exists(TARGET_DIRECTORY):
            os.makedirs(TARGET_DIRECTORY)
        shutil.move(filename, TARGET_DIRECTORY + filename)
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
