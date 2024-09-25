#include <JrkG2.h>
#include <AccelStepper.h>

// IO definitions
#define DIR 12  // Stepper DIR Pin
#define STEP 14 // Stepper STEP Pin

// Constant definitions
#define step_min_position 0
#define step_max_position 64000

// Initialize HardwareSerial instances
HardwareSerial S1(1);  // UART1 for JRK1
HardwareSerial S2(2);  // UART2 for JRK2

// Initialize JrkG2 interfaces
JrkG2Serial jrk1(S1);
JrkG2Serial jrk2(S2);

// Initialize stepper instance
AccelStepper stepper(AccelStepper::DRIVER, STEP, DIR);  // Use DRIVER mode for stepper

// Define stepper variables
int maxSpeed = 8000;
int z = 0;

// Task handles
TaskHandle_t Task1;
TaskHandle_t Task2;

void setup() {
    // Initialize USB serial for debugging
    Serial.begin(115200);

    // Configure HardwareSerial for JRK1
    S1.begin(115385, SERIAL_8N1, 26, 25);  // RX on GPIO 26, TX on GPIO 25

    // Configure HardwareSerial for JRK2
    S2.begin(115385, SERIAL_8N1, 33, 32);  // RX on GPIO 33, TX on GPIO 32

    // Configure stepper motor
    stepper.setMaxSpeed(maxSpeed);
    stepper.setAcceleration(1000); // Increase acceleration to smooth movement
    stepper.setSpeed(0);  // Initial speed 0
    stepper.setCurrentPosition(0);

    xTaskCreatePinnedToCore(
        serialTask,    // Function to run (JRK serial communication)
        "Serial Task", // Name of the task
        10000,         // Stack size
        NULL,          // Parameter to pass
        1,             // Priority
        &Task2,        // Task handle
        0              // Run on Core 0 (dedicated to serial communication)
    );
}

void loop() {
    // Control stepper motor based on z
    if (stepper.currentPosition() > step_max_position && z > 0) {
        stepper.setSpeed(0);
    } else if (stepper.currentPosition() < step_min_position && z < 0) {
        stepper.setSpeed(0);
    }
    stepper.runSpeed();  // Non-blocking stepper control

    // Nothing here as tasks are now running in parallel
}

// Task 2: JRK serial communication on Core 0
void serialTask(void *pvParameters) {
    int fb_counter = 0;
    while (true) {
        if (Serial.available() > 0) {
            String data = Serial.readStringUntil('\n');
            int first_comma_index = data.indexOf(',');
            int second_comma_index = data.indexOf(',', first_comma_index + 1);

            if (first_comma_index > 0 && second_comma_index > 0) {
                String x_str = data.substring(0, first_comma_index);
                String y_str = data.substring(first_comma_index + 1, second_comma_index);
                String z_str = data.substring(second_comma_index + 1);

                int x = x_str.toInt();
                int y = y_str.toInt();
                z = z_str.toInt();
            
                jrk1.setTarget(x);  // Set JRK1 target
                jrk2.setTarget(y);  // Set JRK2 target

                stepper.setSpeed(z);
            }
        }
        fb_counter++;
        if(fb_counter >= 5) {
            int x_fb = jrk1.getScaledFeedback();
            int y_fb = jrk2.getScaledFeedback();
            Serial.print("x: ");
            Serial.print(x_fb);
            Serial.print(", y: ");
            Serial.print(y_fb);
            Serial.print(", z: ");
            Serial.println(stepper.currentPosition());
            fb_counter = 0;
        }
        // Optional delay to avoid hogging CPU
        vTaskDelay(100 / portTICK_PERIOD_MS);  // 10ms delay for serial task
    }
}
