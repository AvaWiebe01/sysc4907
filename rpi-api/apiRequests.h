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
        float x_coord;
        float y_coord;
        float roughness;
        std::chrono::time_point<std::chrono::system_clock> timestamp;

        // Default constructor
        RoadData() {
            x_coord = 0.0;
            y_coord = 0.0;
            roughness = 99999.9;
            timestamp = {};
        }

        // Parametrized constructor
        RoadData(float x, float y, float rfns, std::chrono::time_point<std::chrono::system_clock> time) : x_coord(x), y_coord(y), roughness(rfns), timestamp(time) {
        }
};

#endif