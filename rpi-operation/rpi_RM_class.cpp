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
#include<cmath>
#include <Python.h>
#include "./mainGUI/sharedMemComms.cpp"
#include "GPSWrapper.cpp"


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
	
	//SharedData object to communicate with GUI
	SharedData sharedmem;
	
	//used to manage access to the work queue
	mutex mtx;				
	condition_variable cv;
	bool timedout = false; // if the gps times out exit both threads
	int vehicle_type = -1;
	int vehicle_year = -1;
	int vehicle_class= -1;
	bool recording = true;
	bool exitValue = false;
	
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
        printf ("Successful connection to Arduino Nano \n");
		
		//get data
		//float i = 1.1; test value
		double latlon[2] = {0.0, 0.0}
		while(true){ // loop until program finish
			//end program
			if (exitValue == true){
				exit(0);
			}

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
			gps.getLocation(latlon);

			//put gps loction data into the recorded point struct
			newPoint.lat = latlon[0];//newdata->lat;
			newPoint.lon = latlon[1];//newdata->log;

				
			// releases when lock goes out of scope.
			if (this->recording == true)
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
		float prevTime = 0.0;
		float currentIRI = 0.0;

		//counter to track number of processed points
		int i = 0;

		//strings required to build the CSV
		string segmentfile = "values";

		//create variables to store first and last position;
		float s_lat = 0.0;
		float s_lon = 0.0;
		float e_lat = 0.0;
		float e_lon = 0.0;
		float mp_lat = 0.0;
		float mp_lon = 0.0;

		//make an empty array for the road segments
		float segment[150][2]; //150 data points

		string currentFilename = segmentfile + ".csv";
		ofstream roadSegment; //open road segment file, clearing any trace of old uses
		while(true){ // loop until program finish
		//if gps timed out kill program
			//end program
			exitValue = sharedmem.exited();

			if (exitValue == true){
				exit(0);
			}

			//reset recorded matrix
			if (i <=0){
				//open a titled 
				string currentFilename = segmentfile + ".csv";
				roadSegment.open(currentFilename, ofstream::out | ofstream::trunc);
			}

		std::this_thread::sleep_for(std::chrono::milliseconds(25));
		recorded_point newPoint;
			// releases when lock goes out of scope.
			{
				unique_lock<mutex> lock(mtx);
				//if queue is empty wait for new point
				while (work.empty()) cv.wait(lock);
				newPoint = work.front();
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
			//process data

			//
			if (prevPoint.valid == -1){
				//do nothing -> need more points to have useful information
			}

			//
			else{
				if (i <= 0){
					//record start position of road segment
					s_lat = newPoint.lat;
					s_lon = newPoint.lon;
				}

				if (i == 75)
				{
					mp_lat = newPoint.lat;
					mp_lon = newPoint.lon;
				}

				//get change in time
				int t = static_cast<int>(milliseconds_since_epoch) - \
					static_cast<int>(chrono::duration_cast<chrono::milliseconds>(prevPoint.timestamp.time_since_epoch()).count());
				
				//get change in time in ms
				float dt = float(t)-prevTime;
				
				//convert dt to seconds
				float ts = dt/1000; 

				//get total change in acceleration
				float prevA = prevPoint.collected_data;

				//calculate jerk
				float rocA = (newPoint.collected_data - prevA)/ts; 

				//float vel = prevVel + prevA*t + (1/2) * rocA * (t^2); //calculate velocity
				float position =  prevPos + prevVel*ts + (1/2)*prevA*pow(ts, 2) + (1/6) * rocA * pow(ts, 3); //calculate position

				//log position
				roadSegment << position << ",";
				
				//update position matrix
				segment[i][1] = position;

				//increase counter
				i++;

				//store prev time
				prevTime = t;

				//send accelerometer values and  to GUI
                sharedmem.send_data(ts, newPoint.collected_data, currentIRI);
			}
			prevPoint = newPoint;

			//calculate iri for road segment and reset i
			if (i >=150){
				//record last point position data
				e_lat = newPoint.lat;
				e_lon = newPoint.lon;


				/*  BUILD PYTHON ARGUMENTS    */
				//get distance between start and end position in meters
				float distance = segment_distance(s_lat, s_lon, e_lat, e_lon);

				//get spacing between recorded points -> i is the number of points recorded
				//assuming most points recorded successfully
				float distance_between_points = distance / i;
				for (int j = 0; j <=150; j++)
				{
					segment[j][0] = distance_between_points*j;
				}
				PyObject* roadMatrix = PyUnicode_DecodeFSDefault(segment); //matrix of road profile
				PyObject* startPos = PyUnicode_DecodeFSDefault(0); //start at pos 0
				PyObject* step = PyUnicode_DecodeFSDefault(0); //treat as no overlap

				//create argument tuple
				PyObject* pArgs = PyTuple_New(3);
				PyTuple_SetItem(pArgs, 0, roadMatrix);
				PyTuple_SetItem(pArgs, 1, startPos);
				PyTuple_SetItem(pArgs, 2, step);
				
				//call IRI calculator
				PyObject* pResult = PyObject_CallObject(iriCalculator, pArgs);
				Py_DECREF(pArgs); //deallocate argument tuple

				//process results
				if (pResult == nullptr) {
					//data is useless restart loop
					continue;
				}
				const char* resultStr = PyUnicode_AsUTF8(pResult);
				currentIRI = strtof(resultStr); //change to be output of the python code.

				//reset counter i
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

	//initialize python for IRI calculations
	Py_Initialize();

	// Set PYTHONPATH to the current directory
    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.append('.')");

	//prepare python function object for repeated use
	//choose the IRI calculation file
	PyObject* pName = PyUnicode_DecodeFSDefault("IRI");
	//import the file as a module
	PyObject* pModule = PyImport_Import(pName);

	// deallocate pName as it is no longer needed.
	Py_DECREF(pName);

	//ensure the python module exists
	if (pModule != nullptr) {
		//load target function from python module
		PyObject* iriCalculator = PyObject_GetAttrString(pModule,"iri");
		//ensure the specified function exists
		if (iriCalculator && PyCallable_Check(iriCalculator)){
			//function loaded successfully
		}
		else{
			cerr<<"Fatal error: Could not load IRI calculator python function";
			exit(1);
		}
	}
	else{
		cerr<<"Fatal error: Could not load IRI calculator python module";
		exit(1);
	}

	//set up GPS
	GPSWrapper();

	//create road monitor object
	RoadMonitor rm("rm");

	//start threads
	thread record(&RoadMonitor::record_data, &rm, "data_recorder");
	record.detach();
	thread interpret(&RoadMonitor::interpret_data, &rm, "data_interpreter", filename);
	interpret.join();

}

float segment_distance(float start_lat, float start_lon, float end_lat, float end_lon)
{
	//convert to radians
	float s_lat = start_lat * (M_PI/180);
	float s_lon = start_lon * (M_PI/180);
	float e_lat = end_lat * (M_PI/180);
	float e_lon = end_lon * (M_PI/180);

	//Use the Haversine formula
	//to determine length between two points
	//assuming a spherical Earth with radius r = 6371 km = 6371000 m
	float r = 6371000.0;

	//a = sin^2 ((e_lat - s_lat)/2) + cos(s_lat)  * ( cos(e_lat) ) * ( sin^2 ((e_lon-s_lon)/2) )
	float a = pow(sin((e_lat - s_lat)/2), 2) + cos(s_lat) * cos(e_lat) * pow(sin((e_lon-s_lon)/2), 2);
	//c = 2 * atan (sqrt(a) / (sqrt a-1));
	float c = 2 * atan(sqrt(a) / sqrt(1-a));
	//d = r*c
	float d = r * c;

	return d;
}
