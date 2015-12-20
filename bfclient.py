import sys
import socket
import select
from collections import namedtuple
import threading
import time

time_since_last_message = time.time()
my_ip = socket.gethostbyname(socket.gethostname())
# node = namedtuple("node", ["ip", "port"])
my_port = int(sys.argv[1])      # port number
timeout = int(sys.argv[2])      # timeout
dv = {}                         # dictionary for distance vector
predecessor = {}                # dictionary to store the link with the lowest route
neighbors = {}                  # dictionary to hold neighbors and time since last message from them
neighbor_distance = {}
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
    neighbor_weight = int(sys.argv[next_arg + 2])            # weight
    neighbor = (neighbor_ip, neighbor_port)             # add neighbor to list of neighbors
    dv[neighbor] = int(neighbor_weight)
    neighbor_distance[neighbor] = int(neighbor_weight)
    predecessor[neighbor] = neighbor
    neighbors[neighbor] = start
    next_arg += 3
#=====MESSAGES========================================================
# function that sends distance vector to neighbors
def ROUTE_UPDATE():
    # print "Sending Route Update"
    # message will be ROUTE_UPDATE + ip + port + weight + dv

    # print "MESSAGE:" + msg
    # iterate through list of neighbors
    for neighbor in neighbors:
        msg = None
        if neighbor_distance.has_key(neighbor):
            msg = "ROUTE_UPDATE" + " " + my_ip + " " + str(my_port) + " " + str(neighbor_distance[neighbor]) + " "
        for v in dv:
            # print "DV v"
            # print str(dv[v])
            if msg is None:
                msg = "ROUTE_UPDATE "
            msg += str(v[0]) + " " + str(v[1]) + " " + str(dv[v]) + " "
        if msg is not None:
            msg += "EOT"
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
def SHOW_RT():
    now = time.strftime("%H:%M:%S", time.localtime(time.time()))
    print str(now) + "\tDistance vector list is: "
    for node in dv:
        print "Destination=" + node[0] + ":" + str(node[1]) + "\tCost=" + str(dv[node])
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
time.sleep(1)
ROUTE_UPDATE()
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
                command = command.split()
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
                            dv[node] = int(linked_down_nodes[node])
                            # send linkup message to neighbor
                            LINK_UP(node)
                elif command[0] == "CLOSE":
                    print "Node shutting down"
                    nodeActive = False
                elif command[0] == "SHOW_RT":
                    SHOW_RT()
                else:
                    print command[0] + "Command not recognized"
            else:
                # update neighbor time if message received from neighbor
                # if distance vector changes or timeout is reached, resend
                data = s.recv(1024)
                # print "Received Message: "
                # print data
                SHOW_RT()
                data = data.split()
                print data
                # print data
                # print data
                # when receiving distance vector, check to see if there are any nodes that
                # are not in current dv. If there's a new node, add it to dv and send ROUTE_UPDATE
# ['ROUTE_UPDATE', '160.39.231.6', '1964', '5', '160.39.231.6', '6363', '5', '160.39.231.6', '31389', '5', 'EOT']

                if data[0] == "ROUTE_UPDATE":
                    sender_ip = data[1]
                    sender_port = int(data[2])
                    if data[3] is float("inf"):
                        sender_weight = data[3]
                    else:
                        sender_weight = int(data[3])
                    sender = (sender_ip, sender_port) # sender ip, port
                    # check to see if sender is in neighbors list
                    if(neighbors.has_key(sender)):
                        neighbors[sender] = time.time()
                        print "have neighbor already"
                        if neighbor_distance.has_key(sender):
                            if(neighbor_distance[sender] > data[3]):
                                neighbor_distance[sender] = sender_weight
                                neighbors[sender] = time.time()
                                dv[sender] = sender_weight
                        else:
                            # neighbor_distance[sender] = sender_weight
                            # dv[sender] = sender_weight
                            print "don't have neighbor in neighbor distance for some reason"
                    else:
                        neighbors[sender] = time.time()
                        print "adding neighbor"
                        neighbor_distance[sender] = sender_weight
                        dv[sender] = sender_weight
                    end_of_message = False
                    counter = 4
                    new_dv = {}
                    print "MY NEIGHBORS ARE"
                    print len(neighbors)

                    while(end_of_message is False):
                        if data[counter+2] is float("inf"):
                            weight = float("inf")
                        else:
                            weight = int(data[counter+2])
                        new_dv[data[counter], int(data[counter+1])] = weight # ip address, port, weight
                        counter += 3
                        if(data[counter] == "EOT"):
                            end_of_message = True
                    print new_dv
                    # check to see if any of the weights in the route update are shorter or an infinite weight

                    for node in new_dv:
                        # print node
                        # check to make sure node isn't me
                        if str(node[0]) != str(my_ip) or str(node[1]) != str(my_port):
                            if dv.has_key(node):
                                # if distance to neighbor + neighbor distance to node < my distance to node, replace my distance to node with my neighbor and record that as predecessor
                                # if dv[node] == float("inf") and new_dv[node] != float("inf"):
                                #     dv[node] = new_dv[node]
                                #     predecessor[node] = [sender_ip, sender_port]
                                # if neighbors.has_key(sender):
                                #     if dv.has_key(sender):
                                #         if new_dv[sender] < dv[sender]:
                                #             dv[sender] = new_dv[sender]
                                #     else:
                                #         dv[sender] = new_dv[sender]
                                if int(neighbor_distance[sender]) + int(new_dv[node]) < int(dv[node]):
                                    print "REWRITING NODE"
                                    del dv[node]
                                    dv[node] = int(new_dv[node]) + int(neighbor_distance[sender])
                                    neighbor_weight = int(new_dv[node])
                                    predecessor[node] = [sender_ip, sender_port]
                            else:
                                print "adding node"

                                # node doesn't exist in routing table yet, add it
                                dv[node] = int(new_dv[node]) + int(data[3])
                                predecessor[node] = [sender_ip, sender_port]
                    print "from source"
                elif data[0] == "LINKUP":
                    print "LINKUP"
                    sender = (data[1], int(data[2])) # sender ip, port
                    if(dv[sender] == float("inf")):
                        if(deactivated_links[sender] is not None):
                            dv[sender] = int(deactivated_links[sender])
                            del deactivated_links[sender]
                            neighbors[sender] = time.time()
                            ROUTE_UPDATE()
                            print "LINK RESTORED"
                elif data[0] == "LINKDOWN":
                    sender = (data[1], int(data[2])) # sender ip, port
                    deactivated_links[sender] = int(dv[sender])
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
