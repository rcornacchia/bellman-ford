import sys
import socket
import select
from collections import namedtuple
import threading
import time
import os

time_since_last_message = time.time()
my_ip = socket.gethostbyname(socket.gethostname())
node = namedtuple("node", ["ip", "port"])
my_port = int(sys.argv[1])      # port number
timeout = int(sys.argv[2])      # timeout
dv = {}                         # dictionary for distance vector
predecessor = {}                # dictionary to store the link with the lowest route
neighbors = {}                  # dictionary to hold neighbors and time since last message from them
linked_down_nodes = {}          # dictionary for linked_down_nodes, so I can keep track of neighbors when they're linked down and restore them as neighbors when they're linked up
deactivated_links = {}          # dictionary for nodes that have sent a LINKED_DOWN msg to me, so I can restore when I get a linkup
next_arg = 3                    # arguments after argv[2] come in triplets
number_neighbors = (len(sys.argv[3:]))/3
start = time.time()
source = (my_ip, my_port)
nodeActive = True
#====================================================================
# Get neighbors from command line
if(len(sys.argv[3:])%3 != 0):
    print "incorrect usage, neighbors should be listed:ip address, port, weight"
    exit()
while(next_arg/3 <= number_neighbors):
    neighbor_ip = sys.argv[next_arg]                    # ip address
    neighbor_port = int(sys.argv[next_arg + 1])         # port number
    neighbor_weight = sys.argv[next_arg + 2]            # weight
    neighbor = (neighbor_ip, neighbor_port)         # add neighbor to list of neighbors
    dv[neighbor] = neighbor_weight
    predecessor[neighbor] = neighbor
    neighbors[neighbor] = start
    next_arg += 3
    # print dv
#=====MESSAGES========================================================
# function that sends distance vector to neighbors
def ROUTE_UPDATE():
    # print "Sending Route Update"
    # message will be ROUTE_UPDATE + ip + port + dv
    msg = "ROUTE_UPDATE" + " " + source[0] + " " + str(source[1]) + " "
    for v in dv:
        # print "DV v"
        # print str(dv[v])
        msg += str(v[0]) + " " + str(v[1]) + " " + str(dv[v]) + " "
    msg += "EOT"
    # print "MESSAGE:" + msg
    # iterate through list of neighbors
    for neighbor in neighbors:
        # send message to each neighbor
        sending_socket.sendto(msg, (neighbor[0], neighbor[1]))
        #reset timer
        time_since_last_message = time.time()
        # message should include the port number from the source
#====================================================================
def LINK_DOWN(node):
    print "SENDING LINKDOWN"
    msg = "LINKDOWN" + " " + source[0] + " " + str(source[1]) + " "
    sending_socket.sendto(msg, (node[0], node[1]))
#====================================================================
def LINK_UP(node):
    print "SENDING LINKUP"
    msg = "LINKUP" + " " + source[0] + " " + str(source[1]) + " "
    sending_socket.sendto(msg, (node[0], node[1]))
#====================================================================
# thread function --> checks time to see if it has been more than timeout since last message
# if it has been, then add message to write, so that select will be called
# Function also tests to see if neighbors have been not messaged in 3 * timeout seconds
class myThread (threading.Thread):
    def __init__(self, start_time):
        threading.Thread.__init__(self)
        self.process = None
        time_since_last_message = start_time
    def run(self):
        time_since_last_message = time.time()
        while nodeActive:
            # print "Thread started"
            now = time.time()
            # print now - time_since_last_message
            # print timeout
            nodes_to_remove = []
            # check neighbors to see if any of the time has passed timeout*3
            for neighbor in neighbors:
                if(now - neighbors[neighbor] > timeout * 3):
                    # remove neighbor
                    print "REMOVING DEACTIVATED NEIGHBOR"
                    nodes_to_remove.append(neighbor)
            for node in nodes_to_remove:
                dv[node] = float("inf")
                del neighbors[node]
                ROUTE_UPDATE()
            # Check to see if last message sent is inside the timeout window
            if (now - time_since_last_message > timeout):
                time_since_last_message = time.time()
                ROUTE_UPDATE()
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
output = [sys.stdin]
#====================================================================
while nodeActive:
    try:
        inputready,outputready,exceptready = select.select(input,[],[])
        for s in inputready:
            # if s == server:
            #     # handle the server socket
            #     client, address = server.accept()
            #     input.append(client)
            if s == sys.stdin:
                command = sys.stdin.readline()
                # print command
                command = command.split()
                # print command[0]
                if command[0] == "LINKDOWN":
                #TODO RETURNand len(command) > 2:

                    # command_ip = command[1] # IP address
                    # command_port = int(command[2]) # Port
                    # FOR TESTING PURPOSES TODO change back
                    command_ip = neighbor_ip
                    command_port = neighbor_port
                    node = (command_ip, command_port)
                    if node in neighbors:
                        # print "Neighbor"
                        dv[node] = float("inf")
                        linked_down_nodes[node] = dv[node]
                    else:
                        print "Node is not a neighbor, can't Linkdown"
                        # send linkdown message to neighbor
                        # update neighbor's distance vector to infinity
                    # remove node from list of neighbors
                    for node in linked_down_nodes:
                        del neighbors[node]
                        LINK_DOWN(node)
                        ROUTE_UPDATE()
                elif command[0] == "LINKUP":
                #TODO return and len(command) > 2:
                    # print command[1]
                    # print command[2]
                    # command_ip = command[1] # IP address
                    # command_port = int(command[2]) # Port
                    # FOR TESTING PURPOSES TODO change back
                    command_ip = neighbor_ip
                    command_port = neighbor_port
                    node = (command_ip, command_port)
                    if node not in neighbors:
                        #add it back to neighbors
                        neighbors[node] = time.time()
                        #change dv
                        if node in dv:
                            dv[node] = linked_down_nodes[node]
                            # send linkup message to neighbor
                            LINK_UP(node)
                elif command[0] == "CLOSE":
                    print "Node shutting down"
                    nodeActive = False
                elif command[0] == "SHOW_RT":
                    now = time.strftime("%H:%M:%S", time.localtime(time.time()))
                    print str(now) + "\tDistance vector list is: "
                    for node in dv:
                        print "Destination=" + node[0] + ":" + str(node[1]) + "\tCost=" + dv[node]

                else:
                    print command[0] + "Command not recognized"
            else:
                # update neighbor time if message received from neighbor
                # if distance vector changes or timeout is reached, resend
                data = s.recv(1024)
                # print "Received Message: "
                # print data
                data = data.split()
                # print data
                # when receiving distance vector, check to see if there are any nodes that
                # are not in current dv. If there's a new node, add it to dv and send ROUTE_UPDATE
                if data[0] == "ROUTE_UPDATE":
                    sender_ip = data[1]
                    sender_port = int(data[2])
                    # print sender_ip
                    # print sender_port
                    sender = sender_ip, sender_port # sender ip, port
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
                        print node
                        if node[0] != my_ip and node[1] != my_port:
                            if node in dv:
                                if dv[node] == float("inf") and new_dv[node] != float("inf"):
                                    dv[node] = new_dv
                                    predecessor[node] = [sender_ip, sender_port]
                                elif new_dv[node] < dv[node]:
                                    print "REWRITING NODE"
                                    dv[node] = new_dv[node]
                                    predecessor[node] = [sender_ip, sender_port]
                            elif node not in dv:
                                # check to see if there is a node that is not yet in the dv
                                # if there isn't then add it
                                dv[node] = new_dv[node]
                                predecessor[node] = [sender_ip, sender_port]
                    # print "NEW DV: "
                    # print new_dv
                # elif data[0] == "CLOSE":
                #     print "CLOSE"
                elif data[0] == "LINKUP":
                    print "LINKUP"
                    sender = (data[1], int(data[2])) # sender ip, port
                    if(dv[sender] == float("inf")):
                        if(deactivated_links[sender] is not None):
                            dv[sender] = deactivated_links[sender]
                            del deactivated_links[sender]
                            neighbors[sender] = time.time()
                            ROUTE_UPDATE()
                            print "LINK RESTORED"
                elif data[0] == "LINKDOWN":
                    sender = (data[1], int(data[2])) # sender ip, port
                    deactivated_links[sender] = dv[sender]
                    dv[sender] = float("inf");
                    del neighbors[sender]
                    ROUTE_UPDATE
                    print "LINK DEACTIVATED"
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
        select.select([], [input], [])
        print "unblocked"
thread1.join()
