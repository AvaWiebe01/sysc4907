#include <Adafruit_MPU6050.h>
#include <string.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu1, mpu2;

void setup() {
  Wire.begin();
  Serial.begin(115200);
  if(!mpu1.begin(0x68) || !mpu2.begin(0x69)){
    Serial.write("ERROR: Failed to detect MPU6050");

    while(true){
      delay(10);
    }
  }

  mpu1.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu1.setFilterBandwidth(MPU6050_BAND_260_HZ);

  mpu2.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu2.setFilterBandwidth(MPU6050_BAND_260_HZ);
}

void loop() {

  sensors_event_t mpu1Accel, mpu2Accel, dummyGyro, dummyTemp;

  mpu1.getEvent(&mpu1Accel, &dummyGyro, &dummyTemp);
  mpu2.getEvent(&mpu2Accel, &dummyGyro, &dummyTemp);

  float accelData = (mpu1Accel.acceleration.z + mpu2Accel.acceleration.z) / 2;

  byte* accelDataBytes = (byte *)&accelData;
  
  Serial.write("$");

  for(int i = 0; i < sizeof(float); i++){
    Serial.write(accelDataBytes[i]);
  }

  Serial.write("#");

  delay(5);

}
