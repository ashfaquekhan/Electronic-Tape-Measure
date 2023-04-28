const byte AInput = 6;
const byte BInput = 7;
const int led = 9;
byte lastState = 0;
byte steps = 0;
int cw = 0;
byte AState = 0;
byte BState = 0;
byte State = 0;

void setup() {
  Serial.begin(9600);
  pinMode(AInput, INPUT);
  pinMode(BInput, INPUT);
}

void loop() {
  AState = digitalRead(AInput);
  BState = digitalRead(BInput) << 1;
  State = AState | BState;

  static const int8_t table[] = {
    0, 1, -1, 0, -1, 0, 0, 1, 1, 0, 0, -1, 0, -1, 1, 0
  };
  int8_t delta = table[(lastState << 2) | State];
  if (delta != 0) {
    steps += delta;
    cw = delta;
  }
  lastState = State;
  
  analogWrite(led, steps);
  Serial.print(State);
  Serial.print('\t');
  Serial.print(cw);
  Serial.print('\t');
  Serial.println(steps);
  // Replace delay(1) with a non-blocking delay using millis()
  static unsigned long lastUpdate = 0;
  if (millis() - lastUpdate >= 1) {
    lastUpdate += 1;
  }
}
