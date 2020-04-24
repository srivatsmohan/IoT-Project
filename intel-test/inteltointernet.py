import pyrebase
import socket
import threading
import time
import sys

clusterHead = True
PORT = 44444


def stream_handler(message):
    data = message["data"]
    print(data)
    if data:
        if type(data) is not list:
            raspiResponse = communicateWithDevice(data["query"], data["ip"], data["port"])
        else:
            raspiResponse = communicateWithDevice(data[-1]["query"], data[-1]["ip"], data[-1]["port"])  # Latest query
        # print(raspiResponse)
        db2 = configureFirebase()
        putIntoFirebase(db2, raspiResponse)
    else:
        print("No data in firebase?")


def streamFromFirebase(db):
    try:
        my_stream = db.child("query").stream(stream_handler)
    except Exception as e:
        print("Can't log in to firebase : {}".format(e))


def configureFirebase():
    config = {'apiKey': 'AIzaSyCRXmyBl6WXfA0oKTJQvTBcmBuz_yI_92k', 'databaseURL': 'https://intel-project-5587a.firebaseio.com/', 'authDomain': 'intel-project-5587a.firebaseapp.com', 'storageBucket': 'gs://intel-project-5587a.appspot.com/'}
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    return db


def putIntoFirebase(db, data):
    try:
        data_firebase = {'data': data}
        results = db.child("flame").push(data_firebase)
        return results
    except Exception as e:
        print("Exception in putting data to firebase : {}".format(e))
        print(data)


def getFromFirebase(db):
    data = db.child("query").get()
    return data


def createSocket(port=44444):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("Socket successfully created")
    try:
        s.bind(('0.0.0.0', port))
        print("Socket binded to {}".format(port))
    except:
        print("Binding problem")
    return s


def closeSocket(s):
    s.close()


def communicateWithDevice(ip, message, port=PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    s.send(message.encode())
    print("Sending : {}, {}, {}".format(ip, port, message))
    recvd_data = s.recv(1024).decode()
    print(recvd_data)
    return recvd_data


def forwardToDestination(data, nextDestination):
    if clusterHead:
        db = configureFirebase()
        print("Inserting into firebase {}".format(data))
        putIntoFirebase(db, data)
    else:
        communicateWithDevice(nextDestination, data)


def receiveFromDevice(s, nextDestination):
    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")
    while True:
        # Establish connection with client.
        c, addr = s.accept()
        data = c.recv(1024).decode()
        c.send("Thank you".encode())
        forwardToDestination(data, nextDestination)
    # Close the connection with the client
    c.close()

# Select only one intel board as cluster head
# By default, intel board will be cluster head
# nextDestination : Firebase URL if cluster head, currently it can be anything random
# nextDestination : IP of next intel if non-cluster head


def main(nextDestination, clusterHead_argument="True", port=44444):
    global clusterHead, PORT
    if clusterHead_argument.strip().lower() == "false":
        clusterHead = False
        print("Node reports to {}".format(nextDestination))
    else:
        print("Node is the cluster-head")

    PORT = port
    # Cluster head roles:
    # 1. Receive from firebase  (EXCLUSIVE)     [streamer]                                      DONE
    # 2. Put into firebase      (EXCLUSIVE)     [receiveFromDevice] [forwardToDestination]      Automatic
    # 3. Receive from other intel               [receiveFromDevice] [forwardToDestination]      DONE
    # 4. Send to intel                          [communicateWithDevice]                         Automatic
    # 5. Receive from raspi                     [receiveFromRaspi]                              DONE
    # 6. Send to raspi                          [communicateWithDevice]                         Automatic

    # For all intel boards
    s = createSocket(PORT)

    if clusterHead:
        db = configureFirebase()
        db_streamer_thread = threading.Thread(target=streamFromFirebase, args=(db,))
        db_streamer_thread.start()

    receiver_thread = threading.Thread(target=receiveFromDevice, args=(s, nextDestination,))
    receiver_thread.start()

    try:
        while True:
            time.sleep(1 * 60 * 60)
    except Exception as e:
        print(e)
    finally:
        # db_streamer_thread.join()
        receiver_thread.join()


main(*sys.argv[1:])
