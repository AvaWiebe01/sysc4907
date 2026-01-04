/*
  MPU6050 Serial Outputter
  Author: Stavros Karamalis, Jackson Fry

  This program utilizes an arduino due to poll z-axis accelerometer data from two MPU6050 sensors 
  and then outputs the data over serial to be read by other devices.

  A small portion of this code was borrowed from a tutorial made by Dejan at https://howtomechatronics.com
  to create a basic skeleton to work off of and modify.
*/

#include <Wire.h>
#define MPU1_ADDR 0x68 // MPU6050 I2C address
#define MPU2_ADDR 0x69 // MPU6050 I2C address
#define GRAVITY_G 9.8067

float getAccelData(int addr){
  float AccZ;
  Wire.beginTransmission(addr);
  Wire.write(0x3F); //Start with register 0x3F (ACCEL_ZOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(addr, 2, true); // Read 2 registers total, z axis value is stored in 2 registers

  //For a range of +-2g, we need to divide the raw values by 16384, according to the datasheet
  AccZ = (((Wire.read() << 8 | Wire.read()) / 16384.0) - 1) * GRAVITY_G; // Z-axis value
  Wire.endTransmission(true);
  return AccZ;
}

//This will be run under the assumption that the sensor is at rest.
float getSensorOffset(int addr){
  float error = 0;
  for(int i = 0; i < 100; i++){
    error += getAccelData(addr);
    delay(5);
  }
  error = error/100;
  return error;
}

float sensorOffset1, sensorOffset2;

void setup() {
  Serial.begin(115200);
  
  Wire.begin();                      // Initialize comunication

  Wire.beginTransmission(MPU1_ADDR);       // Start communication with MPU6050 // MPU=0x68
  Wire.write(0x6B);                  // Talk to the register 6B
  Wire.write(0x00);                  // Make reset - place a 0 into the 6B register
  Wire.endTransmission(true);        //end the transmission
  sensorOffset1 = getSensorOffset(MPU1_ADDR);

  Wire.beginTransmission(MPU2_ADDR);       // Start communication with MPU6050 // MPU=0x69
  Wire.write(0x6B);                  // Talk to the register 6B
  Wire.write(0x00);                  // Make reset - place a 0 into the 6B register
  Wire.endTransmission(true);        //end the transmission
  sensorOffset2 = getSensorOffset(MPU2_ADDR);

  delay(20);
}

void loop() {
  float accelData1, accelData2, accelData;
  float accelDataMax = 0;

  //polls from sensors 20 times and chooses the largest acceleration to write over serial
  for(int i = 0; i < 20; i++){
    accelData1 = getAccelData(MPU1_ADDR) - sensorOffset1;
    accelData2 = getAccelData(MPU2_ADDR) - sensorOffset2;
    accelData = (accelData2 + accelData1) / 2;

    if(abs(accelData) > abs(accelDataMax)) accelDataMax = accelData;
    delay(5);
  }

  //converts the sensor data into bytes which will later be sent to the RPi
  String buffer = String(accelDataMax, 10);  

  //unique character that indicates start of new sensor data
  Serial.write("@");

  //writes the raw data byte by byte
  for(int i = 0; i < sizeof(buffer); i++){
    Serial.write(buffer[i]);
  }

  //unique character that indicates end of new sensor data
  Serial.write("#");
  Serial.println("\n");

}

