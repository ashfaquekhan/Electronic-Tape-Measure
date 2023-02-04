#include <Wire.h>

// Pin definitions for rotary encoder
const int encoderPinA = 4;
const int encoderPinB = 5;

// State tracking variables
int previousEncoderState = 0;
int currentEncoderState = 0;
int encoderPosition = 0;

void setup() {
// Set up rotary encoder pins as inputs
pinMode(encoderPinA, INPUT);
pinMode(encoderPinB, INPUT);

// Start serial communication
Serial.begin(9600);
}

void loop() {
// Read the state of the rotary encoder
previousEncoderState = currentEncoderState;
currentEncoderState = digitalRead(encoderPinA) << 1 | digitalRead(encoderPinB);

// Check for rotary encoder movement
if (previousEncoderState != currentEncoderState) {
// Determine the direction of the rotary encoder
if ((previousEncoderState == 0b00 && currentEncoderState == 0b01) ||
(previousEncoderState == 0b01 && currentEncoderState == 0b11) ||
(previousEncoderState == 0b11 && currentEncoderState == 0b10) ||
(previousEncoderState == 0b10 && currentEncoderState == 0b00)) {
// Encoder is turning clockwise
encoderPosition++;
} else {
// Encoder is turning counterclockwise
encoderPosition--;
}
Serial.println(encoderPosition);
}
}
