import socket
import time
import pyrebase
import threading

host_dict = dict()


# def stream_handler(message):
#     data = message["data"]
#     print(data)
#     if data:
#         if type(data) is not list:
#             nodeIsIntendedRecepient = processQuery(data)
#             if not nodeIsIntendedRecepient:
#                 forwardQuery(data)
#         else:
#             nodeIsIntendedRecepient = processQuery(data[-1])
#             if not nodeIsIntendedRecepient:
#                 forwardQuery(data[-1])  # Latest query
#         # print(raspiResponse)
#         #db2 = configureFirebase()
#         #putIntoFirebase(db2, raspiResponse)
#     else:
#         print("No data in firebase?")


# def streamFromFirebase(db):
#     try:
#         my_stream = db.child("query").stream(stream_handler)
#     except Exception as e:
#         print("Can't log in to firebase : {}".format(e))


def configureFirebase():
    config = {'apiKey': 'AIzaSyCRXmyBl6WXfA0oKTJQvTBcmBuz_yI_92k', 'databaseURL': 'https://intel-project-5587a.firebaseio.com/', 'authDomain': 'intel-project-5587a.firebaseapp.com', 'storageBucket': 'gs://intel-project-5587a.appspot.com/'}
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    return db


def putIntoFirebase(db, data):
    try:
        fb_data = data.split('%')
        data_firebase = {'message type': fb_data[1], 'sensor': fb_data[2], 'sense_data': fb_data[3], 'timestamp': fb_data[4]}
        results = db.child("response/" + fb_data[0]).push(data_firebase)
        return results
    except Exception as e:
        print("Exception in putting data to firebase : {}".format(e))
        print(data)


def intelServer(my_ip, my_port, phase, reply):
    global host_dict

    intel_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    intel_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)         # reuse port if not free
    intel_server.bind((my_ip, my_port))
    intel_server.listen(5)

    print("Server Started at {}:{}".format(my_ip, my_port))

    conn, addr = intel_server.accept()
    recvd_data = (conn.recv(1024)).decode()

    while recvd_data:

        if not phase:
            # store host information
            host_id = (recvd_data.split('%'))[0]
            host_ip = (recvd_data.split('%'))[1]
            host_port = int((recvd_data.split('%'))[2])

            host_dict[host_id] = ((host_ip, host_port))
            recvd_data = ''         # to ensure loop runs only once (redundant)

        else:
            print("Receiving... \n{}".format(recvd_data))
            putIntoFirebase(configureFirebase(), recvd_data)
            recvd_data = (conn.recv(1024)).decode()

    conn.send(reply.encode())
    conn.close()

    intel_server.close()
    print("Server Closed at {}:{}".format(my_ip, my_port))


def setupIntel(my_ip, my_port):

    # phase 0 - obtain host information
    intelServer(my_ip, my_port, 0, 'ACK')

    time.sleep(1)

    query = 'my query'

    # phase 1 - receive data from hosts
    server_thread = threading.Thread(target=intelServer, args=(my_ip, my_port, 0, query, ))
    server_thread.start()
