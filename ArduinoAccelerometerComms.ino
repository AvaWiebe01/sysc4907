#include <Adafruit_MPU6050.h>
#include <string.h>
#include <Adafruit_Sensor.h>

#define START_PIN 7

//creates the two IMU sensors
Adafruit_MPU6050 mpu1, mpu2;

void setup() {
  //initializes serial and sets a baudrate of 115200Hz
  //This value should be agreed upon between the RPi and the arduino
  Serial.begin(115200);
  pinMode(START_PIN, INPUT);

  //wait for signal from RPi to begin polling from sensor
  while(true){
    if(digitalRead(START_PIN) == 1){
      delay(5); //debouncing
      if(digitalRead(START_PIN) == 1) break; //stop waiting
    }
  }

  //if the arduino fails detect one or both of the IMUs, write a unique character dedicated to hardware failure messages
  //the character used to report hardware failures should be agreed upon 
  if(!mpu1.begin(0x68) || !mpu2.begin(0x69)){
    Serial.write("X");

    while(true){
      delay(10);
    }
  }

  //Sets the range and filter bandwidth for the IMUs
  mpu1.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu1.setFilterBandwidth(MPU6050_BAND_260_HZ);

  mpu2.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu2.setFilterBandwidth(MPU6050_BAND_260_HZ);
}

void loop() {

  sensors_event_t mpu1Accel, mpu2Accel, dummyGyro, dummyTemp;

  //polls data from the sensors
  mpu1.getEvent(&mpu1Accel, &dummyGyro, &dummyTemp);
  mpu2.getEvent(&mpu2Accel, &dummyGyro, &dummyTemp);

  //averages the value of the two sensors
  float accelData = (mpu1Accel.acceleration.z + mpu2Accel.acceleration.z) / 2;

  //converts the sensor data into bytes which will later be sent to the RPi
  byte* accelDataBytes = (byte *)&accelData;
  
  //unique character that indicates start of new sensor data
  Serial.write("@");

  //writes the raw data byte by byte
  for(int i = 0; i < sizeof(float); i++){
    Serial.write(accelDataBytes[i]);
  }

  //unique character that indicates end of new sensor data
  Serial.write("#");

  delay(5);

}
