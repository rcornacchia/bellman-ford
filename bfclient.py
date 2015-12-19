import sys
import socket
import select
from collections import namedtuple
import threading
import time

time_since_last_message = time.time()
my_ip = socket.gethostbyname(socket.gethostname())
node = namedtuple("node", ["ip", "port"])
my_port = int(sys.argv[1])      # port number
timeout = int(sys.argv[2])      # timeout
dv = {}                         # dictionary for distance vector
neighbors = {}                  # dictionary for neighbor nodes
linked_down_nodes = {}          # dictionary for linked_down_nodes
deactivated_links = {}          # dictionary for nodes that have sent a LINKED_DOWN msg
next_arg = 3                    # arguments after argv[2] come in triplets
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
    neighbor_port = int(sys.argv[next_arg + 1])         # port number
    neighbor_weight = sys.argv[next_arg + 2]            # weight
    neighbor = node(neighbor_ip, neighbor_port)         # add neighbor to list of neighbors
    dv[neighbor] = neighbor_weight
    neighbors[neighbor] = start
    next_arg += 3
#=====MESSAGES========================================================
# function that sends distance vector to neighbors
def ROUTE_UPDATE():
    # message will be ROUTE_UPDATE + [ip, port] + dv
    msg = "ROUTE_UPDATE" + " " + source[0] + " " + str(source[1]) + " "
    for v in dv:
        msg += v[0] + " " + str(v[1]) + " " + dv[v]
    msg += " EOT"
    # iterate through list of neighbors
    for neighbor in neighbors:
        # send message to each neighbor
        sending_socket.sendto(msg, (neighbor[0], neighbor[1]))
        #reset timer
        time_since_last_message = time.time()
        # message should include the port number from the source
        print dv[node]
def LINK_DOWN(node):
    msg = "LINK_DOWN" + " " + source[0] + " " + str(source[1]) + " "
    sending_socket.sendto(msg, (node[0], node[1]))
def LINK_UP(node):
    msg = "LINK_DOWN" + " " + source[0] + " " + str(source[1]) + " "
    msg += node[0] + " " str(node[1]) + dv[node]
    sending_socket.sendto(msg, (node[0], node[1]))
#====================================================================
# thread function --> checks time to see if it has been more than timeout since last message
# if it has been, then add message to write, so that select will be called
# Function also tests to see if neighbors have been not messaged in 3 * timeout seconds
class myThread (threading.Thread):
    def __init__(self, start_time):
        time_since_last_message = start_time
        threading.Thread.__init__(self)
    def run(self):
        time_since_last_message = time.time()
        while True:
            # print "Thread started"
            now = time.time()
            # print now - time_since_last_message
            # print timeout
            nodes_to_remove = []
            # check neighbors to see if any of the time has passed timeout*3
            for neighbor in neighbors:
                if(now - neighbors[neighbor] > timeout * 3):
                    # remove neighbor
                    nodes_to_remove.append(neighbor)
            for node in nodes_to_remove:
                dv[node] = float("inf")
                print dv
                del neighbors[node]
                ROUTE_UPDATE()
            # Check to see if last message sent is inside the timeout window
            if (now - time_since_last_message > timeout):
                time_since_last_message = time.time()
                ROUTE_UPDATE()
            # else:
            #     print "still time"
            time.sleep(1)
#====================================================================
# spawn thread to handle time checking
thread1 = myThread(time_since_last_message)
thread1.start()
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
                    command_port = int(command[2]) # Port
                    node = node(command_ip, command_port)
                    if node in neighbors:
                        dv[node] = float("inf")
                        linked_down_nodes[node] = dv[node]
                    # remove node from list of neighbors
                    for node in linked_down_nodes:
                        del neighbors[node]
                    else:
                        print "Node is not a neighbor, can't Linkdown"
                        ROUTE_UPDATE()
                        # send linkdown message to neighbor
                        LINK_DOWN(node)
                        # update neighbor's distance vector to infinity
                elif command[0] == "LINKUP":
                    command_ip = command[1] # IP address
                    command_ip = int(command[2]) # Port
                    node = node(command_ip, command_port)
                    if node not in neighbors:
                        #add it back to neighbors
                        neighbors[node] = time.time()
                        #change dv
                        if node in dv:
                            dv[node] = linked_down_nodes[node]
                            # send linkup message to neighbor
                            LINK_UP(node)
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
                print data
                data = data.split()
                print data[0]
                # when receiving distance vector, check to see if there are any nodes that
                # are not in current dv. If there's a new node, add it to dv and send ROUTE_UPDATE
                if data[0] == "ROUTE_UPDATE":
                    sender = node(data[1], int(data[2])) # sender ip, port
                    neighbors[sender] = time.time()
                    size_of_dv = len(data[3:])/3
                    counter = 3
                    new_dv = {}
                    while(counter < size_of_dv+3):
                        new_dv[data[counter], data[counter+1]] = data[counter+2] # ip address, port, weight
                        counter += 3


                    # check to see if any of the weights in the route update are shorter or an infinite weight
                    # if they are, then update the dv with the new weight
                    for node in new_dv:
                        if node in dv:
                            if dv[node] == float("inf") and new_dv[node] != float("inf"):
                                dv[node] = new_dv
                            elif new_dv[node] < dv[node]:
                                dv[node] = new_dv[node]
                        else:
                            # check to see if there is a node that is not yet in the dv
                            # if there isn't then add it
                            dv[node] = new_dv[node]
                    print "NEW DV: "
                    print new_dv
                # s.send(data)
                elif data[0] == "CLOSE":
                    print "CLOSE"
                elif data[0] == "LINKUP":
                    print "linkup"
                elif data[0] == "LINKDOWN":
                    print "linkdown"
                elif data[0] == "SHOW_RT":
                    print "SHOW_RT"
                elif data[0] is not None:
                    print "Unrecognized message received: "
                    print data
                else:
                    s.close()
                    input.remove(s)
    except socket.error, e:
        if e.errno != errno.EAGAIN:
            raise e
        print "blocking with", len(buf), "remaining"
        select.select([], [sock], [])
        print "unblocked"
