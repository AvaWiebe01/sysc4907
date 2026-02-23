#ifndef API_REQUESTS
#define API_REQUESTS

#include <stdlib.h>
#include <string>
#include <chrono>
#include <ctime>

// Format for sending and receiving condition data from API
// If this class is changed, the class "RoadData" in /server-api/main.py must also be updated.
class RoadData {
    public:
        float lat;
        float lng;
        float roughness;
        std::chrono::time_point<std::chrono::system_clock> timestamp;

        // Default constructor
        RoadData() {
            lat = 0.0;
            lng = 0.0;
            roughness = 99999.9;
            timestamp = {};
        }

        // Parametrized constructor
        RoadData(float latitude, float longitude, float rfns, std::chrono::time_point<std::chrono::system_clock> time) : lat(latitude), lng(longitude), roughness(rfns), timestamp(time) {
        }
};

#endif