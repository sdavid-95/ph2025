#include <Arduino.h>
#include "sensors.h"

void setup() {
  Serial.begin(115200);
  initSensors();
}

void loop() {
  readDHT();
  readAnalogHumidity();

  delay(2000);
}
