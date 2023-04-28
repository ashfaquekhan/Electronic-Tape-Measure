const int encoderPinA = 6;
const int encoderPinB = 7;
int previousEncoderState = 0;
int currentEncoderState = 0;
int encoderPosition = 0;
int temp=0;

void setup() {
    pinMode(encoderPinA, INPUT);
    pinMode(encoderPinB, INPUT);
}

void loop() 
{
  rotEnc();
}

void rotEnc() {
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
temp=encoderPosition-temp;
Serial.println(encoderPosition);
temp=encoderPosition;
}
}
