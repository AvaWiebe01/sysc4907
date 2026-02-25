#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <string>
#include <iomanip>
#include <sstream>
#include <curl/curl.h>

#define FLOAT_PRECISION 5

// Format for sending and receiving condition data from API
// If this class is changed, the class "RoadData" in /server-api/main.py must also be updated.
class RoadData {
    public:
        float x_coord;
        float y_coord;
        float iri;

        // Default constructor
        RoadData() {
            x_coord = 0.0;
            y_coord = 0.0;
            iri = 99999.9;
        }

        // Parametrized constructor
        RoadData(float x, float y, float roughness) : x_coord(x), y_coord(y), iri(roughness) {
        }
};

/******** FUNCTIONS TO INTERACT WITH ROADMONITOR API ********/

// Send road data to the RoadMonitor API
bool sendData(RoadData data) {
    CURL *curl_handle;
    CURLcode response;
    curl_handle = curl_easy_init();

    std::string url = "http://www.roadmonitor.online:8000/data";
    curl_easy_setopt(curl_handle, CURLOPT_URL, url.c_str());

    // Convert floats to strings with 5 decimals of precision
    std::stringstream stream;
    std::string x_coord_str;
    std::string y_coord_str;
    std::string iri_str;

    stream << std::fixed << std::setprecision(FLOAT_PRECISION) << data.x_coord;
    x_coord_str = stream.str();
    stream.str("");
    stream.clear();

    stream << std::fixed << std::setprecision(FLOAT_PRECISION) << data.y_coord;
    y_coord_str = stream.str();
    stream.str("");
    stream.clear();

    stream << std::fixed << std::setprecision(FLOAT_PRECISION) << data.iri;
    iri_str = stream.str();
    stream.str("");
    stream.clear();

    // Format for a proper POST request
    std::string fields =
        "x_coord=" + x_coord_str +
        "&y_coord=" + y_coord_str +
        "&iri=" + iri_str;
    curl_easy_setopt(curl_handle, CURLOPT_POSTFIELDS, fields.c_str());

    std::cout << "Performing cURL POST request...\n";
    response = curl_easy_perform(curl_handle);
    
    if(response != CURLE_OK) {
        fprintf(stderr, "POST failed: %s\n", curl_easy_strerror(response));
    }

    curl_easy_cleanup(curl_handle);

    return response;
}

// Receive road data from the RoadMonitor API using coordinates
RoadData recvDataCoords(float x_coord, float y_coord) {
    CURL *curl_handle;
    CURLcode response;
    curl_handle = curl_easy_init();
    
    std::string url = "http://www.roadmonitor.online:8000/";
    curl_easy_setopt(curl_handle, CURLOPT_URL, url.c_str());
    
    std::cout << "Performing cURL GET request...\n";
    response = curl_easy_perform(curl_handle);

    if(response != CURLE_OK) {
        fprintf(stderr, "GET failed: %s\n", curl_easy_strerror(response));
    }
    
    curl_easy_cleanup(curl_handle);
    
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
/*
int main() {
    // curl_global_init(CURL_GLOBAL_ALL);

    std::cout << "Running API communication test.\n";

    // RoadData testData_1(24.0, 48.0, 0.333);
    // sendData(testData_1);

    // RoadData testData_2(32.0, 64.0, 0.666);
    // sendData(testData_2);

    // RoadData returnData_1 = recvDataStreetname("Main");
    // std::cout << std::to_string(testData_1.iri);

    RoadData returnData_2 = recvDataCoords(32.0, 64.0);
    // std::cout << std::to_string(testData_2.iri); // 

    curl_global_cleanup();
    return 0;
}
*/