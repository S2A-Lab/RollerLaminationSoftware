#include <JrkG2.h>
#include <SoftwareSerial.h>
#define S1_TX 25
#define S1_RX 26
#define S2_TX 32
#define S2_RX 33

EspSoftwareSerial::UART S1;
EspSoftwareSerial::UART S2;

JrkG2Serial jrk1(S1);
JrkG2Serial jrk2(S2);

void setup() {
  // For the USB, just use Serial as normal:
    Serial.begin(115200);
    Serial.print("Serial");

    // Configure MySerial0 (-1, -1 means use the default)
    S1.begin(9600, SWSERIAL_8N1, S1_RX, S1_TX,false);

    // And configure MySerial1 on pins RX, TX
    S2.begin(9600, SWSERIAL_8N1, S2_RX, S2_TX,false);
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
      
 
          jrk1.setTarget(x);
          jrk2.setTarget(y);
      }
  }
  
   // Do something with x and y
  Serial.print("x: ");
  Serial.print(jrk1.getScaledFeedback());
  Serial.print(", y: ");
  Serial.println(jrk2.getScaledFeedback());
          
  delay(1);
}
