#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <string>
#include <iomanip>
#include <sstream>
#include <chrono>
#include <ctime>
#include "apiRequests.h"
#include <curl/curl.h>

#define FLOAT_PRECISION 6

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
    std::string roughness_str;
    std::string timestamp_str;

    stream << std::fixed << std::setprecision(FLOAT_PRECISION) << data.x_coord;
    x_coord_str = stream.str();
    stream.str("");
    stream.clear();

    stream << std::fixed << std::setprecision(FLOAT_PRECISION) << data.y_coord;
    y_coord_str = stream.str();
    stream.str("");
    stream.clear();

    stream << std::fixed << std::setprecision(FLOAT_PRECISION) << data.roughness;
    roughness_str = stream.str();
    stream.str("");
    stream.clear();

    auto timestamp_duration = std::chrono::duration_cast<std::chrono::milliseconds>(timestamp.time_since_epoch());
    int64_t millis_since_epoch = timestamp_duration.count();
    stream << millis_since_epoch;
    std::string timestamp_str = stream.str();
    stream.str("");
    stream.clear();

    // Format for a proper POST request
    std::string fields =
        "x_coord=" + x_coord_str +
        "&y_coord=" + y_coord_str +
        "&roughness=" + roughness_str +
        "&timestamp=" + timestamp_str;
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, fields.c_str());

    std::cout << "Performing cURL POST request...\n";
    response = curl_easy_perform(curl_handle);
    
    if(response != CURLE_OK) {
        fprintf(stderr, "POST failed: %s\n", curl_easy_strerror(response));
    }

    curl_easy_cleanup(curl_handle);

    return response;
}

// Receive road data from the RoadMonitor API using coordinates
// x_coord: longitude
// y_coord: latitude
// radius: positive integer that defines the radius of the road conditions to check. Default 100
// start: integer start of the date range to search in UNIX epoch milliseconds. Default 0 (no date range)
// end: integer end of the date range to search in UNIX epoch milliseconds. Default 0 (no date range)
RoadData recvDataCoords(float x_coord, float y_coord, int radius = 200, int64_t start = 0, int64_t end = 0) {
    CURL *curl_handle;
    CURLcode response;
    curl_handle = curl_easy_init();

    // Convert floats to strings
    std::stringstream stream;
    std::string x_coord_str;
    std::string y_coord_str;
    std::string radius_str;

    stream << std::fixed << std::setprecision(FLOAT_PRECISION) << x_coord;
    x_coord_str = stream.str();
    stream.str("");
    stream.clear();

    stream << std::fixed << std::setprecision(FLOAT_PRECISION) << y_coord;
    y_coord_str = stream.str();
    stream.str("");
    stream.clear();

    radius_str = std::to_string(radius);
    
    // Construct proper URL with coordinates
    std::string url = "http://www.roadmonitor.online:8000/conditions/coords/"
        + "?x_coord=" + x_coord_str
        + "&y_coord=" + y_coord_str
        + "&radius=" + radius_str;
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

/******** END OF PROVIDED FUNCTIONS ********/

// Only use for testing - otherwise, make use of the API communication functions above
int main() {
    // curl_global_init(CURL_GLOBAL_ALL);

    std::cout << "Running API communication test.\n";

    // RoadData testData_1(24.0, 48.0, 0.333);
    // sendData(testData_1);

    // RoadData testData_2(32.0, 64.0, 0.666);
    // sendData(testData_2);

    RoadData returnData = recvDataCoords(32.0, 64.0);
    // std::cout << std::to_string(testData_2.iri); // 

    curl_global_cleanup();
    return 0;
}
