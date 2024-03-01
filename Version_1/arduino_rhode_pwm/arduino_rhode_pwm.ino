// Define pin connections
const int dirPin_2 = 2;
const int stepPin_2 = 3; //probe

const int dirPin = 4;
const int stepPin = 5;

const int trig_pin = 6;

int init_v = 0;

void setup() {
  
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(trig_pin, OUTPUT);

  pinMode(stepPin_2, OUTPUT);
  pinMode(dirPin_2, OUTPUT);

  digitalWrite(dirPin_2, HIGH);
  digitalWrite(dirPin, LOW);

}

bool run_probe() {
  //Spin Probe//
  digitalWrite(stepPin_2, HIGH);
  delayMicroseconds(2000);
  digitalWrite(stepPin_2, LOW);
  delayMicroseconds(2000);
  digitalWrite(stepPin_2, HIGH);
  delayMicroseconds(2000);
  digitalWrite(stepPin_2, LOW);
  delayMicroseconds(2000);
  return true;
}

bool run_plate() {
  //Spin plate//
  for(int i = 0; i <9; i++){
  digitalWrite(stepPin, HIGH);
  delayMicroseconds(2000);
  digitalWrite(stepPin, LOW);
  delayMicroseconds(2000);}
  return true;
}

bool init_f() {
  while (true) {
    if (Serial.available() > 0) {
      // read the incoming bytes:
      int8_t x = Serial.read();
      if (x == 3) {
        return true;
      }
    }
  }
}


bool confirmed() {
  while (true) {
    if (Serial.available() > 0) {
      // read the incoming bytes:
      int8_t x = Serial.read();
      if (x == 3) {
        return true;
      }
    }
  }
}

void loop() {

  for (int j = 0; j < 37; j++)
  { //spin plate
    for (int x = 0; x < 50; x++) //spin probe
    { if (confirmed()) {
        run_probe();
        delay(100);
        Serial.write(3);
        digitalWrite(trig_pin, HIGH);
        delay(1);
        digitalWrite(trig_pin, LOW); 
      }
    }
    digitalWrite(dirPin_2, !digitalRead(dirPin_2));
    run_plate();
  }

  while (1);
}
