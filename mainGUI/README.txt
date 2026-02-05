In order to run this program you need to do a few things:

1 - Install the kivy library and virtual environment in the same directory as the main app.

2 - Enable the virtual environment and install numpy.

3 - Also install kivy-garden library so that the real-time graph works at all.

4 - Run the startGUI shell script

5 - If you get the message "Waiting for shared memory..." please make sure you are using the "SharedDataArray" class from "sharedMemComms.cpp". If you don't create an instance of this class, the program will remain stuck waiting...

