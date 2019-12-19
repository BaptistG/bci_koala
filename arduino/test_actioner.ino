const int RIGHT_LED = 7;
const int FORWARD_LED = 9;
const int LEFT_LED = 11;
const int BAUDRATE = 9600;
int incomingByte;      // a variable to read incoming serial data into

void setup() {
  pinMode(RIGHT_LED, OUTPUT);
  pinMode(FORWARD_LED, OUTPUT);
  pinMode(LEFT_LED, OUTPUT);
  Serial.begin(BAUDRATE);

  digitalWrite(RIGHT_LED, LOW);
  digitalWrite(FORWARD_LED, LOW);
  digitalWrite(LEFT_LED, LOW);
}

void loop() {
 if (Serial.available() > 0) {
    // read the oldest byte in the serial buffer:
    incomingByte = Serial.read();
    
    if (incomingByte == 'R') {
      digitalWrite(RIGHT_LED, HIGH);
      digitalWrite(FORWARD_LED, LOW);
      digitalWrite(LEFT_LED, LOW);
    }
    
    if (incomingByte == 'F') {
      digitalWrite(FORWARD_LED, HIGH);
      digitalWrite(RIGHT_LED, LOW);
      digitalWrite(LEFT_LED, LOW);
    }
    
    if (incomingByte == 'L') {
      digitalWrite(LEFT_LED, HIGH);
      digitalWrite(RIGHT_LED, LOW);
      digitalWrite(FORWARD_LED, LOW);
    }

    if (incomingByte == 'N') {
      digitalWrite(LEFT_LED, LOW);
      digitalWrite(RIGHT_LED, LOW);
      digitalWrite(FORWARD_LED, LOW);
    }
  }
  
}
