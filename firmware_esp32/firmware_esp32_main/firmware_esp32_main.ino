#include <AccelStepper.h>

///////////////////////////////////
///////// IO definitions //////////
///////////////////////////////////
#define DIR 12  // Stepper DIR Pin
#define STEP 14 // Stepper STEP Pin

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
bool calibrated = false;

///////////////////////////////////
/// Linear Actuator Limitations ///
///////////////////////////////////
#define MAX_SPEED 8000
#define STEP_MIN_POSITION 0
#define STEP_MAX_POSITION 64000

void setup() {
    // Initialize USB serial for debugging
    Serial.begin(115200);
    // Configure stepper motor
    stepper.setMaxSpeed(MAX_SPEED);
    stepper.setAcceleration(1000); // Increase acceleration to smooth movement
    stepper.setSpeed(0);  // Initial speed 0
    stepper.setCurrentPosition(0);

    // Create a task to handle serial communication and motor control on Core 0
}

void loop() {
  if (Serial.available() >= 10) {  // Wait until 10 bytes are available
        for (int i = 0; i < 10; i++) {
            received_data[i] = Serial.read();
        }
        // Check if the last byte is 255 (end marker)
        if (received_data[9] == 255) {
            // Reconstruct each 16-bit target
            target_speed_horizontal_stage =
                reconstruct_16bit_value(received_data[6], received_data[7], received_data[8]);
            stepper.setSpeed(target_speed_horizontal_stage);
        }
    }

    int16_t x_fb = 0;
    int16_t y_fb = 0;
    int16_t z_fb = stepper.currentPosition();

    Serial.write(0x00);
    Serial.write(0x00);
    Serial.write(0x00);
    Serial.write(target_speed_horizontal_stage &0x7F);
    Serial.write(target_speed_horizontal_stage >> 7 & 0x7F);
    Serial.write(target_speed_horizontal_stage >> 14 & 0x7F);
    Serial.write(z_fb & 0x7F);
    Serial.write(z_fb >> 7  & 0x7F);
    Serial.write(z_fb >> 14 & 0x7F);
    Serial.write(0xFF);
    
    // Control stepper motor based on z
    if (stepper.currentPosition() > STEP_MAX_POSITION && target_speed_horizontal_stage > 0) {
        stepper.setSpeed(0);
    } else if (stepper.currentPosition() < STEP_MIN_POSITION && target_speed_horizontal_stage < 0) {
        stepper.setSpeed(0);
    }
    stepper.runSpeed();  // Non-blocking stepper control
}

// Reconstruct 16-bit value from received chunks
int16_t reconstruct_16bit_value(uint8_t chunk1, uint8_t chunk2, uint8_t remaining_bits) {
    int32_t data = (remaining_bits << 14) | (chunk2 << 7) | chunk1;
    return int16_t(data);
}
