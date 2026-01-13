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
#include <ctime>
#include <fstream>


#define GPS_TIMEOUT 50000000 //timeout in x for GPS Hat
//header file for the RoadMonitor data structures

using namespace std;
struct recorded_point{
	float lat;
	float lon;
	float collected_data;
	chrono::time_point<chrono::system_clock> timestamp;
	int valid = 1;
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
		//float i = 1.1; test value

		while(true){ // loop until program finish
			recorded_point newPoint; //struct that all 
			//i = i+1.1;
			//get new point from arduino
			/*********/
			char buffer[11];

            serial.readString(buffer, '\n', 14, 2000);
            //printf("String read: %s\n", measured_accel); 
            //remove indicators
            string buffer_str(buffer);
            size_t pos1 = buffer_str.find("@");
            size_t pos2 = buffer_str.find("#");

            string measured_accel = buffer_str.substr(pos1+1, pos2-1);
            
            if(measured_accel.length() <= 2) {
				continue;
			}
			
			newPoint.timestamp = chrono::system_clock::now();

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
	
	int interpret_data(const string iname, string filename){
		ofstream logFile(filename);
		logFile << "Accel, lat, lon, time"<< endl;
		
		//store previous data point as well
		recorded_point prevPoint;
		//need 2 data points for calculation
		prevPoint.valid = -1;

		//initialize previous position and velocity
		float prevPos = 0.0;
		float prevVel = 0.0;

		//counter to track number of processed points
		int i = 0;

		//counter to track number of road segments
		int j = 0;
		//strings required to build the CSV
		string segmentfile = "values";

		

		string currentFilename = segmentfile + to_string(j) + ".csv";
		ofstream roadSegment; //open road segment file, clearing any trace of old uses
		while(true){ // loop until program finish
		//if gps timed out kill program
			if (timedout){
			return 1;
		}

		if (i <=0){
			//open a titled 
			string currentFilename = segmentfile + to_string(j) + ".csv";
			roadSegment.open(currentFilename, ofstream::out | ofstream::trunc);
			j++;
		}

		std::this_thread::sleep_for(std::chrono::milliseconds(25));
		recorded_point newPoint;
			// releases when lock goes out of scope.
			{
				unique_lock<mutex> lock(mtx);
				//if queue is empty wait for new point
				while (work.empty()) cv.wait(lock);
				newPoint = work.front();
				cerr << work.size();
				work.pop();
			} 
			
			//print to console for debug purposes
			cerr<< newPoint.collected_data <<" " <<newPoint.lat <<" " <<newPoint.lon <<endl;

			//get time since epoch in milliseconds from recorded timestamp for data point
			//
			auto milliseconds_since_epoch = chrono::duration_cast<chrono::milliseconds>(
        		newPoint.timestamp.time_since_epoch()).count();
			//write data point to log file
			logFile << newPoint.collected_data <<", " <<newPoint.lat <<", " <<newPoint.lon << ", " << milliseconds_since_epoch<<endl; 
			
			/**********/
			//process
			if (prevPoint.valid == -1){
				//do nothing
			}
			else{
				//get change in time
				int t = static_cast<int>(milliseconds_since_epoch) - \
					static_cast<int>(chrono::duration_cast<chrono::milliseconds>(prevPoint.timestamp.time_since_epoch()).count());
				float prevA = prevPoint.collected_data; //get total change in acceleration
				float rocA = (newPoint.collected_data - prevA)/t; //calculate jerk
				//float vel = prevVel + prevA*t + (1/2) * rocA * (t^2); //calculate velocity
				float position =  prevPos + prevVel*t + (1/2)*prevA*(t^2) + (1/6) * rocA * (t^3); //calculate position
				//prevPos = position;
				//prevVel = vel;

				roadSegment << position << ",";
				//increase counter
				i++;

			}
			prevPoint = newPoint;
			if (i >=150){
				i = 0;
			}



			//send to database
			/**********/
			
	
		}
		return 0;
	}
	
	
	
};	




int main(){
	string filename = "";
	cout<<"Enter a name for the log data with no file extension: ";
	cin>>filename;
	filename = filename + ".txt";

	RoadMonitor rm("rm");
	thread record(&RoadMonitor::record_data, &rm, "data_recorder");
	record.detach();
	thread interpret(&RoadMonitor::interpret_data, &rm, "data_interpreter", filename);
	interpret.join();

}
