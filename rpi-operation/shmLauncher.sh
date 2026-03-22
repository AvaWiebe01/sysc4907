#!/bin/bash
pkill -f "python3"
rm /dev/shm/sem* /dev/shm/shared*
source ../mainGUI/kivy_venv/bin/activate


python3 shared_mem_for_iri.py & 
python3 ../mainGUI/core/shared_mem.py &
sleep 2
./rm.out & 
sleep 0.5
python3 ../mainGUI/RoadMonitorApp.py &



