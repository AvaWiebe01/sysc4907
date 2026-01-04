#include <iostream>
#include <queue>
#include <string>
#include <thread>
#include <chrono>
//#include <libgpsmm.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <mutex>
#include <condition_variable>
#include "ArduinoReadSerial.cpp"


#define GPS_TIMEOUT 50000000 //timeout in x for GPS Hat
//header file for the RoadMonitor data structures

using namespace std;
struct recorded_point{
	float lat;
	float lon;
	float collected_data;
};

class RoadMonitor{
	private:
	queue<recorded_point> work;
	
	//used to manage access to the work queue
	mutex mtx;				
	condition_variable cv;
	bool timedout = false; // if the gps times out exit both threads
	
	
	public:
	string name;
	
	RoadMonitor(const string iname){ //constructor
		this->name = iname;
	}
	
	int record_data(const string iname){
        //initialize serial
        
        // Serial object
        serialib serial;
        // Connection to serial port
        char errorOpening = serial.openDevice("/dev/ttyUSB0", 115200);

        // If connection fails, return the error code otherwise, display a success message
        if (errorOpening != 1){
            printf("error opening");
            return errorOpening;
        }
        printf ("Successful connection to com10 \n");

		//initialize gps 
			//declare GPS object
		//gpsmm gps_rec("localhost", DEFAULT_GPSD_PORT);

		//gps issue return
		/*if (gps_rec.stream(WATCH_ENABLE|WATCH_JSON) == NULL) {
			cerr << "No GPSD running.\n";
			return 1;
		}*/
		
		
		//get data
		float i = 1.1;
		while(true){ // loop until program finish
			recorded_point newPoint; //struct that all 
			i = i+1.1;
			std::this_thread::sleep_for(std::chrono::milliseconds(100));
			//get new point from arduino
			/*********/
			char buffer[11];

            serial.readString(buffer, '\n', 14, 2000);
            //printf("String read: %s\n", measured_accel); 
            //remove indicators
            string buffer_str(buffer);
            size_t pos1 = buffer_str.find("@");
            size_t pos2 = buffer_str.find("#");

            string measured_accel = buffer_str.substr(pos1+1, pos2);

			//convert from string to float:
			newPoint.collected_data = stof(measured_accel);
			 
			//get location data
			/*struct gps_data_t * newdata; // create struct to hold gps data 
			while (!gps_rec.waiting(GPS_TIMEOUT)) {
				
			}
			
			if ((newdata = gps_rec.read()) == NULL) {
				cerr << "Read error.\n";
				//retry to see if the error persists
				while (!gps_rec.waiting(GPS_TIMEOUT)){}
				
				//check read again
				if ((newdata = gps_rec.read()) == NULL){
					cerr << "Read error persists. Exiting Program\n";
					timedout = true; //set timedout kill flag
					return 1;
				}
				
			}*/
			
			//put gps loction data into the recorded point struct
			newPoint.lat = 0.0;//newdata->lat;
			newPoint.lon = 0.0;//newdata->log;

				
			// releases when lock goes out of scope.
			{
				unique_lock<mutex> lock(mtx);
				work.push(newPoint);
				//notify waiting thread
				cv.notify_all();		
			}
			
		}
        serial.closeDevice();
		
		return 0;
	}
	
	int interpret_data(const string iname){
		
		while(true){ // loop until program finish
		if (timedout){
			return 1;
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(100));
		recorded_point newPoint;
		
			// releases when lock goes out of scope.
			{
				unique_lock<mutex> lock(mtx);
				//if queue is empty wait for new point
				while (work.empty()) cv.wait(lock);
				newPoint = work.front();
				work.pop();
			} 
			cerr<<newPoint.collected_data;
			cerr<<" ";
			cerr<<newPoint.lat;
			cerr<<" ";
			cerr<<newPoint.lon;
			cerr<<"\n";
			/*process data*/
			/**********/
			
			//send to database
			/**********/
			
	
		}
		return 0;
	}
	
	
	
};	




int main(){
	RoadMonitor rm("rm");
	thread record(&RoadMonitor::record_data, &rm, "data_recorder");
	record.detach();
	thread interpret(&RoadMonitor::interpret_data, &rm, "data_interpreter");
	interpret.join();

}