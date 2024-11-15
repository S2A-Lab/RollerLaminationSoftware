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
uint8_t received_data[10];  // Array to store received command bytes
bool homed = false;
int home_state = 0;
bool initialized = false;

///////////////////////////////////
/// Linear Actuator Limitations ///
///////////////////////////////////
#define MAX_SPEED 8000
#define STEP_MIN_POSITION 0
#define STEP_MAX_POSITION 80000

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
    if (Serial.available() > 0) {
      String receivedString = Serial.readStringUntil('\n'); // Read until newline
      target_speed_horizontal_stage = receivedString.toInt();                 // Convert to integer
    }
    int16_t x_fb = 0;
    int16_t y_fb = 0;
    int16_t z_fb = stepper.currentPosition();

    stepper.setSpeed(target_speed_horizontal_stage);
    if (stepper.currentPosition() > STEP_MAX_POSITION && target_speed_horizontal_stage > 0) {
        stepper.setSpeed(0);
    } else if (stepper.currentPosition() < STEP_MIN_POSITION && target_speed_horizontal_stage < 0) {
        stepper.setSpeed(0);
    }
  }
  stepper.runSpeed();  // Non-blocking stepper control
}

// Reconstruct 16-bit value from received chunks
int16_t reconstruct_16bit_value(uint8_t chunk1, uint8_t chunk2, uint8_t remaining_bits) {
    int32_t data = (remaining_bits << 14) | (chunk2 << 7) | chunk1;
    return int16_t(data);
}
