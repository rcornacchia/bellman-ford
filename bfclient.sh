#!/bin/bash

port1=$RANDOM
port2=$RANDOM
osascript -e 'tell app "Terminal"
    do script with command "python ~/code/python/bellman-ford/bfclient.py '$port1' 5 160.39.231.6 '$port2' 30" in window 2
end tell'

sleep .1
python ~/code/python/bellman-ford/bfclient.py $port2 5 160.39.231.6 $port1 10


LINKUP 160.39.231.6 30998
