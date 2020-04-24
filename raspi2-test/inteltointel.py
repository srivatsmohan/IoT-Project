import socket

import inteltointernet as gateway


def intelServer(my_ip, my_port):

    intel_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    intel_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)         # reuse port if not free
    intel_server.bind((my_ip, my_port))
    intel_server.listen(5)

    print("Server Started at {}:{}".format(my_ip, my_port))

    while True:
        conn, addr = intel_server.accept()
        recvd_data = (conn.recv(1024)).decode()
        # store recvd_data as file
        downloadFile(host_id, conn, recvd_data)

    conn.close()
    intel_server.close()

    print("Server Closed at {}:{}".format(my_ip, my_port))


def downloadFile(host_id, conn, recvd_data):

    file_name = 'file' + host_id + '.txt'
    # open file to store received data (will overwrite old data)
    recv_file = open(file_name, 'wb')

    while recvd_data:
        print("Receiving...     ")

        # add timestamp to received data
        data_with_timestamp = "Data received at " + time.ctime() + " : " + recvd_data
        recv_file.write(data_with_timestamp)
        recvd_data = conn.recv(1024)
        # print("{} at {}".format(recvd_data, time.ctime()))

    # save file contents
    recv_file.close()

    print("~~ Received! ~~")
