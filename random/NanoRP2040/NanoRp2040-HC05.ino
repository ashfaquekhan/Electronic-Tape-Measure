#include <Arduino_LSM6DSOX.h>

//#include <SPI.h>
//#include <Wire.h>  
#include <MadgwickAHRS.h>
#include <Math.h>

float yawFilteredOld;
Madgwick filter;
const float sensorRate = 104.00;
float htemp=0;
void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
  while (!Serial);
  if(!IMU.begin())  {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
  filter.begin(sensorRate);
  Serial.println("Setup complete!");
  while (!Serial1);
}  
void loop() {
  float xAcc, yAcc, zAcc;
  float xGyro, yGyro, zGyro;
  float roll, pitch, heading;
  if(IMU.accelerationAvailable() && IMU.gyroscopeAvailable()){
    IMU.readAcceleration(xAcc, yAcc, zAcc);
    IMU.readGyroscope(xGyro, yGyro, zGyro); 
    filter.updateIMU(xGyro, yGyro, zGyro, xAcc, yAcc, zAcc);
    pitch = filter.getPitch();
    heading = filter.getYaw();
    roll =filter.getRoll();
    float yawFiltered = 0.1 * heading + 0.9 * yawFilteredOld; // low pass filter
    Serial.println("pitch: " + String(pitch) + " yaw: " + String(yawFiltered));
    yawFilteredOld = yawFiltered;
    int16_t x=yawFiltered*100;
    int16_t y=pitch*100;
    int16_t z=roll*100;
    int16_t r = (int16_t)1;
    byte buf[8];
    buf[0] = x & 255;
    buf[1] = (x >> 8) & 255;
    buf[2] = y & 255;
    buf[3] = (y >> 8) & 255;
    buf[4] = z & 255;
    buf[5] = (z >> 8) & 255;
    buf[6] = r & 255;
    buf[7] = (r >> 8) & 255;
    Serial1.write(buf,sizeof(buf)); 
  }
}
