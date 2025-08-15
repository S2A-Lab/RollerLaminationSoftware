#include <AccelStepper.h>

///////////////////////////////////
///////// IO definitions //////////
///////////////////////////////////
#define DIR 9  // Stepper DIR Pin
#define STEP 10 // Stepper STEP Pin
#define HOME 23 // Home sensor Pin

///////////////////////////////////
//////// Module Initialize ////////
///////////////////////////////////

// Initialize stepper interface
AccelStepper stepper(AccelStepper::DRIVER, STEP, DIR);  // Use DRIVER mode for stepper

///////////////////////////////////
///// Communication variables /////
///////////////////////////////////

int target_speed_horizontal_stage = 0;
int target_position_vertical_left_actuator = 0;
int target_position_vertical_right_actuator = 0;
char buf[16];
bool homed = false;
int home_state = 0;
bool initialized = false;

///////////////////////////////////
/// Linear Actuator Limitations ///
///////////////////////////////////
#define MAX_SPEED 8000
#define STEP_MIN_POSITION 0
#define STEP_MAX_POSITION 110000

void setup() {
    // Initialize USB serial for debugging
    Serial.begin(115200);
    // Configure stepper motor
    stepper.setMaxSpeed(MAX_SPEED);
    stepper.setAcceleration(1000); // Increase acceleration to smooth movement
    stepper.setSpeed(0);  // Initial speed 0
    stepper.setCurrentPosition(0);
    pinMode(HOME, INPUT_PULLUP);
}

void loop() {
  if(!homed){
    switch(home_state) {
      case 0: // Wait for home sensor to be triggered
        if (digitalRead(HOME)){
          stepper.setSpeed(-1000);
        } else {
          stepper.setSpeed(1000);
          stepper.setCurrentPosition(0);
          home_state = 1;
        }
        break;
      case 1: // Wait for home sensor to move back a little bit
        if (stepper.currentPosition()> 1000) {
          stepper.setSpeed(0);
          home_state = 2;
        } else {
          stepper.setSpeed(1000);
        }
        break;
      case 2: // End
        homed = true;
        stepper.setSpeed(0);
        break;
    }
  } else {
    if (Serial.available()) {
      String cmd = Serial.readStringUntil('\n');
      cmd.trim();
      if (cmd.startsWith("sp")) { // Set max speed
        long spd = cmd.substring(2).toInt();
        stepper.setMaxSpeed(spd);
      }
      else if (cmd.startsWith("ac")) { // Set max acceleration
        long acc = cmd.substring(2).toInt();
        stepper.setAcceleration(acc);
      }
      else if (cmd.startsWith("tp")) { // Move to target position
        long pos = cmd.substring(2).toInt();
        pos = constrain(pos, STEP_MIN_POSITION, STEP_MAX_POSITION);
        stepper.moveTo(pos);
      }
      else if (cmd.equalsIgnoreCase("fb")) { // Feedback: send current position
        sprintf(buf, "%06ld", stepper.currentPosition()); // 6 digits, pad with zeros
        Serial.println(buf);
      }
    }
  }
  stepper.run();  // Non-blocking stepper control
}
