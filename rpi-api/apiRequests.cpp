#include <stdlib.h>
#include <stdio.h>
#include <string>
// #include <curl/curl.h>
// install curl and use libcurl API

//using namespace std;

// Format for sending and receiving condition data from API
// If this class is changed, the class "RoadData" in /server-api/main.py must also be updated.
class RoadData {
    public:
        float x_coord;
        float y_coord;
        std::string street_name;
        float iri;

        RoadData() {
            x_coord = 0;
            y_coord = 0;
            street_name = "Unknown";
            iri = 99999;
        }

        RoadData(float x, float y, std::string streetnm, float roughness) : x_coord(x), y_coord(y), street_name(streetnm), iri(roughness) {

        }
};

// Only use for testing - otherwise, make use of the API communication functions themselves
int main() {
    printf("Running API communication test.");

    return 0;
}

// Send road data to the RoadMonitor API
bool sendData(RoadData data) {
    return true;
}

// Receive road data from the RoadMonitor API
RoadData recvData() {
    RoadData data;
    return data;
}
