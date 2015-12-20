#!/bin/bash

port1=$RANDOM
port2=$RANDOM
port3=$RANDOM
osascript -e 'tell app "Terminal"
    do script with command "python ~/code/python/bellman-ford/bfclient.py '$port1' 10 160.39.231.6 '$port2' 5 160.39.231.6 '$port3' 30" in window 2
    do script with command "python ~/code/python/bellman-ford/bfclient.py '$port3' 10 160.39.231.6 '$port2' 5 160.39.231.6 '$port1' 30" in window 3
end tell'

sleep 15

osascript -e 'tell app "Terminal"
    do script with command "python ~/code/python/bellman-ford/bfclient.py '$port2' 10 160.39.231.6 '$port1' 5 160.39.231.6 '$port3' 20" in window 4
end tell'
# python ~/code/python/bellman-ford/bfclient.py $port2 10 160.39.231.6 $port1 10 160.39.231.6 $port3 5
