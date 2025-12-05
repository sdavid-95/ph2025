#include <Arduino.h>
#include "sensors.h"
#include "controller.h"
#include "traffic.h"
#include "actuator.h"

// Buffer to store incoming serial data
String inputString = "";
bool stringComplete = false;

void setup() {
  Serial.begin(115200);
  
  // Initialize all subsystems
  initSensors();
  initTrafficLights();
  initBumperServo();
  
  // Reserve 200 bytes for the inputString
  inputString.reserve(200);
}

void loop() {
  // 1. Read Sensors continuously (non-blocking)
  // Note: In a real app, use millis() timers here instead of delays
  // But for now, we just check them when needed in the controller.
  
  // 2. Process Incoming Serial Commands from Python
  if (stringComplete) {
    // Trim whitespace (newlines)
    inputString.trim(); 
    
    // Pass the message to your logic brain
    processCameraMessage(inputString);
    
    // Clear for next message
    inputString = "";
    stringComplete = false;
  }
}

// Interrupt-like function to read Serial bytes as they arrive
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}