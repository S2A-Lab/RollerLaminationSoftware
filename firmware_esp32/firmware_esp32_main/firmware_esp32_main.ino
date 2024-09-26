#include <JrkG2.h>
#include <AccelStepper.h>

///////////////////////////////////
///////// IO definitions //////////
///////////////////////////////////
#define DIR 12  // Stepper DIR Pin
#define STEP 14 // Stepper STEP Pin


// Initialize HardwareSerial instances
HardwareSerial S1(1);  // UART1 for JRK1
HardwareSerial S2(2);  // UART2 for JRK2

///////////////////////////////////
//////// Module Initialize ////////
///////////////////////////////////

// Initialize JrkG2 interfaces
JrkG2Serial jrk1(S1);
JrkG2Serial jrk2(S2);

// Initialize stepper interface
AccelStepper stepper(AccelStepper::DRIVER, STEP, DIR);  // Use DRIVER mode for stepper

///////////////////////////////////
///// Communication variables /////
///////////////////////////////////

int target_speed_horizontal_stage = 0;
int target_position_vertical_left_actuator = 0;
int target_position_vertical_right_actuator = 0;
uint8_t received_data[10];  // Array to store received command bytes

///////////////////////////////////
/// Linear Actuator Limitations ///
///////////////////////////////////
#define MAX_SPEED 8000
#define STEP_MIN_POSITION 0
#define STEP_MAX_POSITION 64000


void setup() {
    // Initialize USB serial for debugging
    Serial.begin(115200);

    // Configure HardwareSerial for JRK1
    S1.begin(115385, SERIAL_8N1, 26, 25);  // RX on GPIO 26, TX on GPIO 25

    // Configure HardwareSerial for JRK2
    S2.begin(115385, SERIAL_8N1, 33, 32);  // RX on GPIO 33, TX on GPIO 32

    // Configure stepper motor
    stepper.setMaxSpeed(MAX_SPEED);
    stepper.setAcceleration(1000); // Increase acceleration to smooth movement
    stepper.setSpeed(0);  // Initial speed 0
    stepper.setCurrentPosition(0);

}

void loop() {
    // Control stepper motor based on z
    if (stepper.currentPosition() > STEP_MAX_POSITION && target_speed_horizontal_stage > 0) {
        stepper.setSpeed(0);
    } else if (stepper.currentPosition() < STEP_MIN_POSITION && target_speed_horizontal_stage < 0) {
        stepper.setSpeed(0);
    }
    stepper.runSpeed();  // Non-blocking stepper control
  
    if (Serial.available() >= 10) {  // Wait until 10 bytes are available
      
      while (Serial.read()!=255){}
      for (int i = 0; i < 10; i++) {
        received_data[i] = Serial.read();
      }
  
      // Check if the last byte is 255 (end marker)
      if (received_data[9] == 255) {
        // Reconstruct each 16-bit target
        target_position_vertical_left_actuator =
            reconstruct_16bit_value(received_data[0], received_data[1], received_data[2]);
        target_position_vertical_right_actuator =
            reconstruct_16bit_value(received_data[3], received_data[4], received_data[5]);
        target_speed_horizontal_stage =
            reconstruct_16bit_value(received_data[6], received_data[7], received_data[8]);
        jrk1.setTarget(target_position_vertical_left_actuator);
        jrk2.setTarget(target_position_vertical_right_actuator);
        stepper.setSpeed(target_speed_horizontal_stage);
      }
    }
    
    int16_t x_fb = jrk1.getScaledFeedback();
    int16_t y_fb = jrk2.getScaledFeedback();
    int16_t z_fb = stepper.currentPosition();

    Serial.write(x_fb & 0x7F);
    Serial.write(x_fb >> 7  & 0x7F);
    Serial.write(x_fb >> 14 & 0x7F);
    Serial.write(y_fb & 0x7F);
    Serial.write(y_fb >> 7  & 0x7F);
    Serial.write(y_fb >> 14 & 0x7F);
    Serial.write(z_fb & 0x7F);
    Serial.write(z_fb >> 7  & 0x7F);
    Serial.write(z_fb >> 14 & 0x7F);
    Serial.write(0xFF);
}

int16_t reconstruct_16bit_value(uint8_t chunk1, uint8_t chunk2, uint8_t remaining_bits) {
  // Reconstruct the 16-bit value using the 2-bit remaining bits and two 7-bit chunks
  return (remaining_bits << 14) | (chunk2 << 7) | chunk1;
}
