#include <gps.h>
#include <iostream>
#include <unistd.h>
#include <thread>
#include <chrono>

using namespace std;
class GPSWrapper{
    private:
    //gps data struct to store recorded data
    struct gps_data_t gps_data;
    int gps_timeout = 150000; // microseconds

    public:
    GPSWrapper(){
        gps_open("localhost", "2947", &gps_data);
        gps_stream(&gps_data, WATCH_ENABLE | WATCH_JSON, NULL);
    }


    int getLocation(double latlon[2]){
        //returns false if no new data arrived within gps_timeout in μs
        if(gps_waiting(&gps_data, gps_timeout)){ 
            //read gps
            if (gps_read(&gps_data, NULL, 0) == -1)
            {
                cerr<<"GPS read error";
                return 1;
            }

            //only use data if we have a fix
            //returns false if no fix
            if (gps_data.fix.mode >= MODE_2D){
                //update values of passed location array
                latlon[0] = gps_data.fix.latitude;
                latlon[1] = gps_data.fix.longitude;
                return 0;
            }
        }
        //failed to read
        return 1;
    }
};

//gps test program
int main(){
    GPSWrapper gpsobj;
    double latlon[2] = {0.0, 0.0};

    while (true){
        if ((gpsobj.getLocation(latlon) == 0){
            cout<<"\nThe returned Lat Lon is: \n";
            cout<<latlon[0]<<"\n";
            cout<<latlon[1];
        }
        else{
            cout<<"\n failed to read gps \n";
        }
        this_thread::sleep_for(chrono::milliseconds(100));
    }
}
