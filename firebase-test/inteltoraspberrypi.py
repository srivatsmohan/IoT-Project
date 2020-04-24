import socket
import threading
import time
import sys
import os


# maintain a dictionary of host ID and IP address
host_dict = dict()
time_info = '60%3'     # TODO : modify if no. of hosts unknown


def intelServer(my_ip, my_port, phase):
    global host_dict
    global time_info

    host_count = 0
    slot = 0

    intel_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    intel_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)         # reuse port if not free
    intel_server.bind((my_ip, my_port))
    intel_server.listen(5)

    print("Server Started at {}:{}".format(my_ip, my_port))

    while True:
        conn, addr = intel_server.accept()
        recvd_data = (conn.recv(1024)).decode()
        print("{} at {}".format(recvd_data, time.ctime()))

        if phase == 0:
            # data received as 'raspi1%192.168.0.1%8000'

            host_id = (recvd_data.split('%'))[0]
            host_ip = (recvd_data.split('%'))[1]
            host_port = int((recvd_data.split('%'))[2])

            # add host information to host dictionary
            host_dict[host_count] = [host_id, (host_ip, host_port)]
            host_count = host_count + 1
            # reply time information
            conn.send(time_info.encode())

            # TODO : modify if no. of hosts unknown
            if host_count == 2:
                break
        else:
            host_id = host_dict[slot][0]
            # store recvd_data as file
            downloadFile(host_id, conn, recvd_data)
            slot = (slot + 1) % 2
            # reply time information
            conn.send(time_info.encode())

    conn.close()
    intel_server.close()

    print("Server Closed at {}:{}".format(my_ip, my_port))


def intelClient(server_ip, server_port, message):
    intel_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    intel_client.connect((server_ip, server_port))

    if message.split('.')[1] == 'txt':
        # send file to gateway
        uploadFile(intel_client, message)
    else:
        intel_client.send(message.encode())

    recvd_data = (intel_client.recv(1024)).decode()
    print(recvd_data)

    print("Closing connection")
    intel_client.close()


def uploadFile(intel_client, file_name):

    # open file to send data
    send_file = open(file_name, 'r')
    message = send_file.readline()
    print(message)

    # send_buffer = ""

    while message:
        # print("Sending...       ")
        intel_client.send(message.encode())
        # send_buffer += message
        # print(send_buffer)
        message = send_file.readline()

    # intel_client.send(send_buffer.encode())
    os.remove(file_name)

    send_file.close()
    print("~~ Sent! ~~")


def downloadFile(host_id, conn, recvd_data):

    file_name = host_id + '.txt'
    # open file to store received data (will overwrite old data)
    recv_file = open(file_name, 'w')

    # while recvd_data != 'END':
    #     print("Receiving...    {} ".format(recvd_data))

    # add timestamp to received data
    data_with_timestamp = "Data received at " + time.ctime() + " : " + str(recvd_data)
    recv_file.write(data_with_timestamp)
    # recvd_data = conn.recv(1024)
    # print("{} at {}".format(recvd_data, time.ctime()))

    # save file contents
    recv_file.close()

    print("~~ Received! ~~")


def generateTime(default):
    global host_dict

    default_time_period = 1 * 60
    num_of_slots = len(host_dict) + 1       # add one for intel board time slot

    if default:
        time_info = str(default_time_period) + "%" + str(num_of_slots)

    else:
        time_period = int(input("Enter time period: "))
        time_info = str(time_period) + "%" + str(num_of_slots)

    return time_info


def sendData(host_dict, time_info, server_ip, server_port):

    wait_counter = 0

    while True:
        time_period = int((time_info.split("%"))[0])         # total time period
        num_of_slots = int((time_info.split("%"))[1])        # number of slots
        num_of_hosts = len(host_dict)       # number of PIs connected to Intel Board

        time_slots = time_period / num_of_slots
        print("{} and {} and {}".format(time_period, num_of_hosts, time_slots))

        print(host_dict)
        wait_time = (num_of_hosts * time_slots)     # assign last time slot to intel board

        if not wait_counter:
            print("Waiting for my slot... {}".format(wait_time))
            time.sleep(wait_time)
            wait_counter = 1

        print("Sending...")
        file_name = host_dict[0][0] + '.txt'
        print(file_name)
        intelClient(server_ip, server_port, file_name)

        file_name = host_dict[1][0] + '.txt'
        intelClient(server_ip, server_port, file_name)


def setupIntel(my_id, my_ip, my_port, server_ip, server_port):
    global host_dict
    global time_info

    # start server and accept raspi connections
    intelServer(my_ip, my_port, 0)

    time.sleep(1)

    # start client and connect to firebase-intel board
    my_data = "intel" + str(my_id) + '%' + my_ip + '%' + str(my_port)
    client_thread = threading.Thread(target=intelClient, args=(server_ip, server_port, my_data,))
    client_thread.start()

    # use default time information
    time_info = generateTime(True)

    server_thread = threading.Thread(target=intelServer, args=(my_ip, my_port, 1, ))
    server_thread.start()

    sendData(host_dict, time_info, server_ip, server_port)

    # if time information is to be changed
    time_info = generateTime(False)
    # intelServer(my_ip, my_port, 1, time_info)
