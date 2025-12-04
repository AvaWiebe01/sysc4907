#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <string>
#include <curl/curl.h>

// #ifdef _WIN32
//     #include "..\curl-8.17.0\curl-8.17.0\include\curl\curl.h"
// #else
//     #include "../curl-8.17.0/curl-8.17.0/include/curl/curl.h"
// #endif

// Format for sending and receiving condition data from API
// If this class is changed, the class "RoadData" in /server-api/main.py must also be updated.
class RoadData {
    public:
        float x_coord;
        float y_coord;
        std::string street_name;
        float iri;

        // Default constructor
        RoadData() {
            x_coord = 0.0;
            y_coord = 0.0;
            street_name = "No Data";
            iri = 99999.9;
        }

        // Parametrized constructor
        RoadData(float x, float y, std::string streetnm, float roughness) : x_coord(x), y_coord(y), street_name(streetnm), iri(roughness) {
        }
};

/******** FUNCTIONS TO INTERACT WITH ROADMONITOR API ********/

// Send road data to the RoadMonitor API
bool sendData(RoadData data) {
    return true;
}

// Receive road data from the RoadMonitor API using coordinates
RoadData recvDataCoords(float x_coord, float y_coord) {
    RoadData data;
    return data;
}

// Receive road data from the RoadMonitor API using streetname
RoadData recvDataStreetname(std::string street_name) {
    RoadData data;
    return data;
}

/******** END OF PROVIDED FUNCTIONS ********/

// Only use for testing - otherwise, make use of the API communication functions above
int main() {
    curl_global_init(CURL_GLOBAL_ALL);

    printf("Running API communication test.");

    RoadData testData_1(24.0, 48.0, "Main", 0.333);
    sendData(testData_1);

    RoadData testData_2(32.0, 64.0, "Stoneview", 0.666);
    sendData(testData_2);

    RoadData returnData_1 = recvDataStreetname("Main");
    std::cout << std::to_string(testData_1.iri);

    RoadData returnData_2 = recvDataCoords(32.0, 64.0);
    std::cout << std::to_string(testData_2.iri); // 

    curl_global_cleanup();
    return 0;
}