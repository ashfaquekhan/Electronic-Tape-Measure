#include <ArduinoJson.h>
#include "I2Cdev.h"
#include <SoftwareSerial.h>
#include "MPU6050_6Axis_MotionApps20.h"
#include <Wire.h>

#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif

MPU6050 mpu;
//MPU6050 mpu(0x69); // <-- use for AD0 high

//#define OUTPUT_READABLE_YAWPITCHROLL_SERIAL
#define OUTPUT_READABLE_YAWPITCHROLL_SERIAL1

char buff[100];
#define BAUD_RATE 9600
#define INTERRUPT_PIN 2  // use pin 2 on Arduino Uno & most boards

// MPU control/status vars
bool dmpReady = false;  // set true if DMP init was successful
uint8_t mpuIntStatus;   // holds actual interrupt status byte from MPU
uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64]; // FIFO storage buffer

// orientation/motion vars
Quaternion q;           // [w, x, y, z]         quaternion container
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free accel sensor measurements
VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;    // [x, y, z]            gravity vector
float euler[3];         // [psi, theta, phi]    Euler angle container
float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector


const int encoderPinA = 4;
const int encoderPinB = 5;
int previousEncoderState = 0;
int currentEncoderState = 0;
int encoderPosition = 0,temp=0;
// ================================================================
// ===               INTERRUPT DETECTION ROUTINE                ===
// ================================================================

volatile bool mpuInterrupt = false;     // indicates whether MPU interrupt pin has gone high
void dmpDataReady() {
    mpuInterrupt = true;
}

// ================================================================
// ===                      INITIAL SETUP                       ===
// ================================================================

void setup() {
    pinMode(encoderPinA, INPUT);
    pinMode(encoderPinB, INPUT);
    #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
        Wire.setClock(400000); 
    #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
        Fastwire::setup(400, true);
    #endif

    Serial.begin(BAUD_RATE);
    #ifdef OUTPUT_READABLE_YAWPITCHROLL_SERIAL1
           Serial1.begin(BAUD_RATE);
    #endif
    
//    while (!Serial);
//    // initialize device
//    Serial.println(F("Initializing I2C devices..."));
//    mpu.initialize();
//    pinMode(INTERRUPT_PIN, INPUT);
//    // verify connection
//    Serial.println(F("Testing device connections..."));
//    Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));
//    // wait for ready
//    Serial.println(F("\nSend any character to begin DMP programming and demo: "));
//    while (Serial.available() && Serial.read()); // empty buffer
//    while (!Serial.available());                 // wait for data
//    while (Serial.available() && Serial.read()); // empty buffer again
    while (!Serial1);
    
    mpu.initialize();
    pinMode(INTERRUPT_PIN, INPUT);
    if(Serial1.available())
    Serial.println(mpu.testConnection() ? F("P") : F("F"));
    while (Serial1.available() && Serial1.read()); // empty buffer
    while (!Serial1.available());                 // wait for data
    while (Serial1.available() && Serial1.read()); // empty buffer again
    

    // load and configure the DMP
    //Serial1.println(F("Initializing DMP..."));
    devStatus = mpu.dmpInitialize();

    // supply your own gyro offsets here, scaled for min sensitivity
    mpu.setXGyroOffset(220);
    mpu.setYGyroOffset(76);
    mpu.setZGyroOffset(-85);
    mpu.setZAccelOffset(1788); // 1688 factory default for my test chip

    // make sure it worked (returns 0 if so)
    if (devStatus == 0) {
        // Calibration Time: generate offsets and calibrate our MPU6050
        mpu.CalibrateAccel(6);
        mpu.CalibrateGyro(6);
        mpu.PrintActiveOffsets();
        // turn on the DMP, now that it's ready
        Serial.println(F("Enabling DMP..."));
        mpu.setDMPEnabled(true);

        // enable Arduino interrupt detection
        Serial.print(F("Enabling interrupt detection (Arduino external interrupt "));
        Serial.print(digitalPinToInterrupt(INTERRUPT_PIN));
        Serial.println(F(")..."));
        attachInterrupt(digitalPinToInterrupt(INTERRUPT_PIN), dmpDataReady, RISING);
        mpuIntStatus = mpu.getIntStatus();

        // set our DMP Ready flag so the main loop() function knows it's okay to use it
        Serial.println(F("DMP ready! Waiting for first interrupt..."));
        dmpReady = true;

        // get expected DMP packet size for later comparison
        packetSize = mpu.dmpGetFIFOPacketSize();
    } else {
        // ERROR!
        // 1 = initial memory load failed
        // 2 = DMP configuration updates failed
        // (if it's going to break, usually the code will be 1)
        Serial.print(F("DMP Initialization failed (code "));
        Serial.print(devStatus);
        Serial.println(F(")"));
    }
}

void rotEnc() {
// Read the state of the rotary encoder
previousEncoderState = currentEncoderState;
currentEncoderState = digitalRead(encoderPinA) << 1 | digitalRead(encoderPinB);

// Check for rotary encoder movement
if (previousEncoderState != currentEncoderState) 
{
  if ((previousEncoderState == 0b00 && currentEncoderState == 0b01) ||(previousEncoderState == 0b01 && currentEncoderState == 0b11) ||
      (previousEncoderState == 0b11 && currentEncoderState == 0b10) || (previousEncoderState == 0b10 && currentEncoderState == 0b00)) 
      {
       encoderPosition++;
      } 
  else 
      {
        encoderPosition--;
      }
  }
}

void loop() {
    rotEnc();
    // if programming failed, don't try to do anything
    if (!dmpReady) return;
    // read a packet from FIFO
    if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) { // Get the Latest packet 

        
        #ifdef OUTPUT_READABLE_YAWPITCHROLL_SERIAL
            mpu.dmpGetQuaternion(&q, fifoBuffer);
            mpu.dmpGetGravity(&gravity, &q);
            mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
            Serial.print(ypr[0] * 180/M_PI);
            Serial.print(",");
            Serial.print(ypr[1] * 180/M_PI);
            Serial.print(",");
            Serial.print(ypr[2] * 180/M_PI);
            Serial.print(",");
            Serial.println(encoderPosition);
            
        #endif    

        #ifdef OUTPUT_READABLE_YAWPITCHROLL_SERIAL1
            // display Euler angles in degrees
//            Serial1.println("HELLO/n");
            mpu.dmpGetQuaternion(&q, fifoBuffer);
            mpu.dmpGetGravity(&gravity, &q);
            mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);

            temp=encoderPosition-temp;
            int16_t x=ypr[0]*180/M_PI * 100;
            int16_t y=ypr[1]*180/M_PI * 100;
            int16_t z=ypr[2]*180/M_PI * 100;
            int16_t r = (int16_t) temp;
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
            temp=encoderPosition;
//            Serial1.print(ypr[0]*180/M_PI);
//            Serial1.print(",");
//            Serial1.print(ypr[1]*180/M_PI);
//            Serial1.print(",");
//            Serial1.println(ypr[2]*180/M_PI);
          
        #endif 
   
    }
}
