import sys
import socket
import select
from collections import namedtuple
import threading
import time



time_since_last_message = time.time()
my_ip = socket.gethostbyname(socket.gethostname())
Neighbor = namedtuple("Neighbor", ["ip", "port"])
my_port = int(sys.argv[1])     # port number
timeout = int(sys.argv[2])    # timeout

# function that sends distance vector to neighbors
def ROUTE_UPDATE():
    # iterate through list of neighbors
    for neighbor in neighbors:
        # send dv
        time_since_last_message = time.time()
        print dv

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

            if (now - time_since_last_message > timeout):
                print "Time's up" + dv
                ROUTE_UPDATE()
            else:
                print "still time"
            time.sleep(1)

thread1 = myThread()
thread1.start()



next_arg = 3 # arguments after argv[2] come in triplets
dv = {} # dictionary for distance vector
neighbors = {}

if(len(sys.argv[3:])%3 != 0):
    print "incorrect usage, neighbors should be listed:ip address, port, weight"
    exit()
number_neighbors = (len(sys.argv[3:]))/3

while(next_arg/3 <= number_neighbors):
    neighbor_ip = sys.argv[next_arg]            # ip address
    neighbor_port = sys.argv[next_arg + 1]      # port number

    neighbor_weight = sys.argv[next_arg + 2]    # weight

    neighbor = Neighbor(neighbor_ip, neighbor_port)
    dv[neighbor] = neighbor_weight
    neighbors[neighbor] = neighbor_weight
    next_arg += 3

#spawn thread to handle timeout


print my_ip
print my_port
# receive on socket end
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((my_ip, my_port))
# s.listen(10)
input = [s, sys.stdin]
while True:
    # if distance vector changes or timeout is reached, resend
    ROUTE_UPDATE()

    # when receiving distance vector, check to see if there are any nodes that
    # are not in current dv

    try:
        inputready,outputready,exceptready = select.select(input,[],[])
        for s in inputready:
            # if s == server:
            #     # handle the server socket
            #     client, address = server.accept()
            #     input.append(client)
            #
            if s == sys.stdin:
                # handle standard input
                command = sys.stdin.readline()
                print command
            #
            # else:
            # handle all other sockets
            else:
                data = s.recv(1024)
                if data:
                    print data
                    # s.send(data)
                else:
                    s.close()
                    input.remove(s)
    except socket.error, e:
        if e.errno != errno.EAGAIN:
            raise e
        print "blocking with", len(buf), "remaining"
        select.select([], [sock], [])
        print "unblocked"


    # use select to avoid busy waiting
    # result = select.select([sock],[],[])
    # data = result[0][0].recv(1024)
    # print "received message:", data
