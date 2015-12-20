#!/bin/bash

port1=$RANDOM
port2=$RANDOM
port3=$RANDOM
port4=$RANDOM
osascript -e 'tell app "Terminal"
    do script with command "echo port 1 && python ~/code/python/bellman-ford/bfclient.py '$port1' 10 160.39.231.6 '$port2' 999 160.39.231.6 '$port3' 30" in window 2
    do script with command "echo port 3 && python ~/code/python/bellman-ford/bfclient.py '$port3' 10 160.39.231.6 '$port1' 30 160.39.231.6 '$port2' 999" in window 3
end tell'

sleep 11

osascript -e 'tell app "Terminal"
    do script with command "echo port 2 && python ~/code/python/bellman-ford/bfclient.py '$port2' 10 160.39.231.6 '$port1' 5 160.39.231.6 '$port3' 5" in window 4
end tell'
sleep 10
echo port 4 && python ~/code/python/bellman-ford/bfclient.py $port4 10 160.39.231.6 $port2 7

# python ~/code/python/bellman-ford/bfclient.py $port2 10 160.39.231.6 $port1 10 160.39.231.6 $port3 5
