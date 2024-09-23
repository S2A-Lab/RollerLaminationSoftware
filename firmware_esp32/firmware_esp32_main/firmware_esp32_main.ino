#include <JrkG2.h>
#include <SoftwareSerial.h>
#include <AccelStepper.h>

/// IO definitions
#define S1_TX 25
#define S1_RX 26
#define S2_TX 32
#define S2_RX 33

#define DIR 2  // Stepper DIR Pin 2
#define STEP 0 // Stepper STEP Pin 0

// Constant definitions
#define step_min_position 0
#define step_max_position 1000

// Initialize serial instances
EspSoftwareSerial::UART S1;
EspSoftwareSerial::UART S2;

// Initialize JrkG2 interfaces
JrkG2Serial jrk1(S1);
JrkG2Serial jrk2(S2);

// Initialize stepper instance
AccelStepper stepper(1, STEP, DIR);  // Set the Stepper Motor

// Define stepper variables
int maxSpeed = 1000;
int speed = 500;
int direction = 1;
int action = 0;

void setup() {
  // Initialize USB serial
    Serial.begin(115200);
    Serial.print("Serial");

    // Configure serial 1
    S1.begin(9600, SWSERIAL_8N1, S1_RX, S1_TX,false);

    // Configure serial 2
    S2.begin(9600, SWSERIAL_8N1, S2_RX, S2_TX,false);

    // Configure stepper motor
    stepper.setMaxSpeed(maxSpeed);   // set the maximum speed
    stepper.setAcceleration(10); // set acceleration
    stepper.setSpeed(0);         // set initial speed
    stepper.setCurrentPosition(0);   // set position to 0
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');  // Read the data until a newline character is received
    
    int first_comma_index = data.indexOf(',');  // Find the position of the first comma
    int second_comma_index = data.indexOf(',', first_comma_index + 1);  // Find the second comma after the first
    
    if (first_comma_index > 0 && second_comma_index > 0) {  // Ensure two commas are found
      String x_str = data.substring(0, first_comma_index);  // Extract the substring before the first comma
      String y_str = data.substring(first_comma_index + 1, second_comma_index);  // Extract the substring between the two commas
      String z_str = data.substring(second_comma_index + 1);  // Extract the substring after the second comma
      
      int x = x_str.toInt();  // Convert the x string to an integer
      int y = y_str.toInt();  // Convert the y string to an integer
      int z = z_str.toInt();  // Convert the z string to an integer
      
      jrk1.setTarget(x);
      jrk2.setTarget(y);
      
      if (stepper.currentPosition()>step_max_position && z > 0) {
        stepper.setSpeed(0);
        stepper.runSpeed();
      } else if (stepper.currentPosition()<step_min_position && z < 0){
        stepper.setSpeed(0);
        stepper.runSpeed();
      } else {
        stepper.setSpeed(z);
        stepper.runSpeed();
      }
    }
  }
  
  // Do something with x and y
  Serial.print("x: ");
  Serial.print(jrk1.getScaledFeedback());
  Serial.print(", y: ");
  Serial.print(jrk2.getScaledFeedback());
  Serial.print(", z: ");
  Serial.println(stepper.currentPosition());
  delay(1);
}
