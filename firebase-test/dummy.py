# run code as python3 raspisensing.py raspiID raspiIP raspiPORT intelIP intelPORT

import sys
import time
import threading
import raspitointel


def writeToFile(data):

    # open file to append data
    file_name = 'datafile.txt'
    data_file = open(file_name, 'a')

    # write data with timestamp
    formatted_data = "raspi" + str(my_id) + '%' + "regular" + '%' + "vibration" + "%" + data + "%" + time.ctime() + "\n"
    data_file.write(formatted_data)

    # save file contents
    data_file.close()


# setup Raspberry PI for transmission of data
my_id = sys.argv[1]
my_ip = sys.argv[2]
my_port = int(sys.argv[3])

server_ip = sys.argv[4]
server_port = int(sys.argv[5])

setup = threading.Thread(target=raspitointel.setupRaspi, args=(my_id, my_ip, my_port, server_ip, server_port, 'datafile.txt', ))
setup.start()

while True:
    writeToFile('Test')
    time.sleep(1)
