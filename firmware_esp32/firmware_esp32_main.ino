#include <JrkG2.h>
#include <HardwareSerial.h>

JrkG2Serial jrk1(Serial2, 11);
JrkG2Serial jrk2(Serial1, 12);

//Serial.begin(9600);
void setup() {
  // put your setup code here, to run once:
  Serial2.begin(9600, SERIAL_8N1, 16, 17); // GPIO 16, GPIO 17
  Serial.begin(9600, SERIAL_8N1, 3, 1); // USB, pc commnunication
  Serial1.begin(9600); // GPIO 9, GPIO 10
}

void loop() {
  if (Serial.available() > 0) {
      String data = Serial.readStringUntil('\n');  // Read the data until a newline character is received
      int comma_index = data.indexOf(',');  // Find the position of the comma
    
      if (comma_index > 0) {  // If a comma is found
          String x_str = data.substring(0, comma_index);  // Extract the substring before the comma
          String y_str = data.substring(comma_index + 1);  // Extract the substring after the comma
      
          int x = x_str.toInt();  // Convert the x string to an integer
          int y = y_str.toInt();  // Convert the y string to an integer
      
          // Do something with x and y
          Serial.print("x: ");
          Serial.print(x);
          Serial.print(", y: ");
          Serial.println(y);

          jrk1.setTarget(x);
          jrk2.setTarget(y);
      }
  }
    
  delay(1);
}
