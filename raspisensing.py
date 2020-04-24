# run code as python3 raspisensing.py raspiID raspiIP raspiPORT intelIP intelPORT

import sys
import time
import raspitointel

import RPi.GPIO as GPIO


# GPIO setup
channel = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

sensor_name = "Vibration"


def callback(channel):
    if GPIO.input(channel):
        data = "Motion detected"
    else:
        data = "Motion detected"

    writeToFile(data)


def writeToFile(data):
    global sensor_name

    # open file to append data
    file_name = 'datafile.txt'
    data_file = open(file_name, 'a')

    # write data with timestamp
    formatted_data = "raspi" + str(my_id) + '%' + "regular" + '%' + "vibration" + "%" + data + "%" + time.ctime() + "\n"
    data_file.write(formatted_data)

    # save file contents
    data_file.close()


GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)  # let us know when the pin goes HIGH or LOW
GPIO.add_event_callback(channel, callback)  # assign function to GPIO PIN, Run function on change

# setup Raspberry PI for transmission of data
my_id = sys.argv[1]
my_ip = sys.argv[2]
my_port = int(sys.argv[3])

server_ip = sys.argv[4]
server_port = int(sys.argv[5])
raspitointel.setupRaspi(my_id, my_ip, my_port, server_ip, server_port, 'datafile.txt')

while True:
    time.sleep(1)
