// serial control commands
#define CMD_STEP_PROBE_CLKWISE  's'
#define CMD_STEP_PLATE_CLKWISE 'd'
#define CMD_STEP_PROBE_ANTI_CLKWISE 'w'
#define CMD_STEP_PLATE_ANTI_CLKWISE 'a'
#define CMD_OSC_TRIGGER 't'
#define CMD_RECEIVED 'r'

// step magnitudes
const int probe_num_steps_per_cmd = 2;
const int plate_num_steps_per_cmd = 9;

// probe stepper pins:
const int pin_probe_dir = 2;
const int pin_probe_step = 3;

// plate stepper pins:
const int pin_plate_dir = 4;
const int pin_plate_step = 5;

// oscilliscope trigger pin
const int pin_trigger = 6;

// stepper control parameters
const unsigned int stepper_pulse_width = 2000; // us
const bool stepper_clkwise_dir = 0;

// trigger parameters
const unsigned int movement_to_trigger_delay = 100; // ms
const unsigned int trigger_pulse_width = 2000; // us

void stepper_pulse(bool direction, int num_steps, int pin_dir, int pin_step){
  digitalWrite(pin_dir, direction);

  for (int i=0; i<num_steps; i++) {
    digitalWrite(pin_step, HIGH);
    delayMicroseconds(stepper_pulse_width);
    digitalWrite(pin_step, LOW);
    delayMicroseconds(stepper_pulse_width);
  }

  delay(movement_to_trigger_delay);
  digitalWrite(pin_trigger, HIGH);
  delayMicroseconds(trigger_pulse_width);
  digitalWrite(pin_trigger, LOW);
  delayMicroseconds(trigger_pulse_width);

  //confirm the move of the stepper

  Serial.write(3);
}

void setup() {
  Serial.begin(9600);

  pinMode(pin_probe_dir, OUTPUT);
  pinMode(pin_probe_step, OUTPUT);
  pinMode(pin_plate_dir, OUTPUT);
  pinMode(pin_plate_step, OUTPUT);

  pinMode(pin_trigger, OUTPUT);


}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();

    if (cmd == CMD_STEP_PROBE_CLKWISE)
      stepper_pulse(stepper_clkwise_dir, probe_num_steps_per_cmd, pin_probe_dir, pin_probe_step);

    else if (cmd == CMD_STEP_PROBE_ANTI_CLKWISE)
      stepper_pulse(!stepper_clkwise_dir, probe_num_steps_per_cmd, pin_probe_dir, pin_probe_step);

    else if (cmd == CMD_STEP_PLATE_CLKWISE)
      stepper_pulse(stepper_clkwise_dir, plate_num_steps_per_cmd, pin_plate_dir, pin_plate_step);

    else if (cmd == CMD_STEP_PLATE_ANTI_CLKWISE)
      stepper_pulse(!stepper_clkwise_dir, plate_num_steps_per_cmd, pin_plate_dir, pin_plate_step);

    else if (cmd == CMD_OSC_TRIGGER){
      digitalWrite(pin_trigger, HIGH);
      delayMicroseconds(trigger_pulse_width);
      digitalWrite(pin_trigger, LOW);
      delayMicroseconds(trigger_pulse_width);
    }
      
    Serial.write(CMD_RECEIVED);
  }
}
