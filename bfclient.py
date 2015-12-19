import sys
import socket
from collections import namedtuple


def send_dv(x):
    print dv
my_ip = socket.gethostbyname(socket.gethostname())
print my_ip


Neighbor = namedtuple("Neighbor", ["ip", "port"])

# port number
my_port =  int(sys.argv[1])

# timeout
my_timeout = sys.argv[2]

# arguments after argv[2] come in triplets
next_arg = 3

# dictionary for neighbors

# dictionary for distance vector
dv = {}

if(len(sys.argv[3:])%3 != 0):
    print "incorrect usage, neighbors should be listed by ip address, port, and weight"
    exit()
number_neighbors = (len(sys.argv[3:]))/3

while(next_arg/3 <= number_neighbors):
    # ip address
    neighbor_ip = sys.argv[next_arg]
    # port number
    neighbor_port = sys.argv[next_arg + 1]
    # weight
    neighbor_weight = sys.argv[next_arg + 2]
    neighbor = Neighbor(neighbor_ip, neighbor_port)
    dv[neighbor] = neighbor_weight
    next_arg += 3


# print dv




print my_ip
print my_port

# receive on socket end
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((my_ip, my_port))

while True:
    send_dv(dv)

    data, addr = sock.recvfrom(1024)
    print "received message:", data

    # if distance vector changes or timeout is reached, resend
