import sys
import socket

class Neighbor:
    def __init__(ip, port, weight):
        self.ip_address = ip
        self.port = port
        self.weight = weight

# executable name
# sys.argv[0]

my_ip = socket.gethostbyname(socket.gethostname())
print my_ip

# port number
my_port =  sys.argv[1]

# timeout
my_timeout = sys.argv[2]

# arguments after argv[2] come in triplets
next_arg = 3

number_neighbors = (len(sys.argv[3:]))/3

while(next_arg/3 <= number_neighbors):
    neighbor = Neighbor()
    # ip address
    neighbor.ip_address = sys.argv[next_arg]
    # port number
    neighbor.port = sys.argv[next_arg + 1]
    # weight
    neighbor.weight = sys.argv[next_arg + 2]
    print neighbor
