import sys

import inteltoraspberrypi
import inteltofirebase

# my_status = sys.argv[6]     # must be 'head' or 'firebase'
my_ip = sys.argv[1]
my_port = int(sys.argv[2])

if sys.argv[3]:                 # cluster head intel board
    print("I am a cluster-head intel board")
    server_ip = sys.argv[3]
    server_port = int(sys.argv[4])
    my_id = int(sys.argv[5])
    inteltoraspberrypi.setupIntel(my_id, my_ip, my_port, server_ip, server_port)

else:                           # firebase-connected intel board
    print("I am a firebase-connected intel board")
    inteltofirebase.setupIntel(my_ip, my_port)
