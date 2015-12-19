import sys
import socket
import select
from collections import namedtuple
import threading
import time

time_since_last_message = time.time()
my_ip = socket.gethostbyname(socket.gethostname())
node = namedtuple("node", ["ip", "port"])
my_port = int(sys.argv[1])     # port number
timeout = int(sys.argv[2])    # timeout
next_arg = 3 # arguments after argv[2] come in triplets
dv = {} # dictionary for distance vector
neighbors = {}
number_neighbors = (len(sys.argv[3:]))/3
start = time.time()
source = node(my_ip, my_port)
#====================================================================
# Get neighbors from command line
if(len(sys.argv[3:])%3 != 0):
    print "incorrect usage, neighbors should be listed:ip address, port, weight"
    exit()
while(next_arg/3 <= number_neighbors):
    neighbor_ip = sys.argv[next_arg]                    # ip address
    neighbor_port = sys.argv[next_arg + 1]              # port number
    neighbor_weight = sys.argv[next_arg + 2]            # weight
    neighbor = node(neighbor_ip, neighbor_port)     # add neighbor to list of neihbors
    dv[neighbor] = neighbor_weight
    neighbors[neighbor] = start
    next_arg += 3
#====================================================================
# function that sends distance vector to neighbors
def ROUTE_UPDATE():
    # message will be ROUTE_UPDATE + [ip, port] + dv
    msg = ["ROUTE_UPDATE", source, dv]
    # iterate through list of neighbors
    for neighbor in neighbors:
        # send message to each neighbor
        sending_socket.sendto()
        #reset timer
        time_since_last_message = time.time()
        # message should include the port number from the source
        print dv
#====================================================================
# thread function --> checks time to see if it has been more than timeout since last message
# if it has been, then add message to write, so that select will be called
# Function also tests to see if neighbors have been not messaged in 3 * timeout seconds
class myThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            # print "Thread started"
            now = time.time()
            print now - time_since_last_message
            print timeout
            nodes_to_remove = []
            # check neighbors to see if any of the time has passed timeout*3
            for neighbor in neighbors:
                if(now - neighbors[neighbor] > timeout * 3):
                    # remove neighbor
                    nodes_to_remove.append(neighbor)
            for node in nodes_to_remove:
                del dv[node]
                del neighbors[node]
                ROUTE_UPDATE()
            # Check to see if last message sent is inside the timeout window
            if (now - time_since_last_message > timeout):
                print "Time's up"
                ROUTE_UPDATE()
            else:
                print "still time"
            time.sleep(1)
#====================================================================
# spawn thread to handle time checking
# thread1 = myThread()
# thread1.start()
#====================================================================
# Create two sockets
sending_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiving_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiving_socket.bind((my_ip, my_port))
input = [receiving_socket, sys.stdin]
#====================================================================
while True:
    try:
        inputready,outputready,exceptready = select.select(input,[],[])
        for s in inputready:
            # if s == server:
            #     # handle the server socket
            #     client, address = server.accept()
            #     input.append(client)
            if s == sys.stdin:
                command = sys.stdin.readline()
                command = command.split()
                if command[0] == "LINKDOWN":
                    command_ip = command[1] # IP address
                    command_ip = int(command[2]) # Port
                    # send linkdown message to neighbor
                    # update neighbor's distance vector to infinity
                    print "Linkdown"
                elif command[0] == "LINKUP":
                    command_ip = command[1] # IP address
                    command_ip = int(command[2]) # Port
                    print "Linkup"
                elif command[0] == "CLOSE":
                    s.close()
                    exit()
                    print "Close"
                else:
                    print command[0] + "Command not recognized"
            else:
                # update neighbor time if message received from neighbor
                # if distance vector changes or timeout is reached, resend
                data = s.recv(1024)
                # when receiving distance vector, check to see if there are any nodes that
                # are not in current dv. If there's a new node, add it to dv and send ROUTE_UPDATE
                if data[0] == "ROUTE_UPDATE":
                    print data
                    # s.send(data)
                elif data[0] == "CLOSE":
                    print "CLOSE"
                elif data[0] == "LINKUP":
                    print "linkup"
                elif data[0] == "LINKDOWN":

                elif data[0] == "SHOW_RT":
                    print "SHOW_RT"
                else:
                    s.close()
                    input.remove(s)
    except socket.error, e:
        if e.errno != errno.EAGAIN:
            raise e
        print "blocking with", len(buf), "remaining"
        select.select([], [sock], [])
        print "unblocked"
