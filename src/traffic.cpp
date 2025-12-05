#include <Arduino.h>
#include "traffic.h"

// ----- PIN DEFINITIONS -----
#define PED_GREEN_PIN   10
#define PED_RED_PIN      9

#define CAR_GREEN_PIN    8
#define CAR_YELLOW_PIN   7
#define CAR_RED_PIN      6

// ----- INITIALIZATION -----
void initTrafficLights() {
    pinMode(PED_GREEN_PIN, OUTPUT);
    pinMode(PED_RED_PIN, OUTPUT);

    pinMode(CAR_GREEN_PIN, OUTPUT);
    pinMode(CAR_YELLOW_PIN, OUTPUT);
    pinMode(CAR_RED_PIN, OUTPUT);

    trafficSetNormal(); // Start in normal mode
}

// ----- NORMAL MODE -----
// Car green, ped red
void trafficSetNormal() {
    digitalWrite(PED_GREEN_PIN, LOW);
    digitalWrite(PED_RED_PIN, HIGH);

    digitalWrite(CAR_GREEN_PIN, HIGH);
    digitalWrite(CAR_YELLOW_PIN, LOW);
    digitalWrite(CAR_RED_PIN, LOW);
}

// ----- TRANSITION: CAR GREEN → YELLOW → RED -----
void trafficTransitionToRed() {

    // Step 1: Car YELLOW
    digitalWrite(CAR_GREEN_PIN, LOW);
    digitalWrite(CAR_YELLOW_PIN, HIGH);
    digitalWrite(CAR_RED_PIN, LOW);

    // Pedestrian still red
    digitalWrite(PED_GREEN_PIN, LOW);
    digitalWrite(PED_RED_PIN, HIGH);

    delay(1500); // 1.5 seconds, adjust as needed

    // Step 2: Car RED
    digitalWrite(CAR_YELLOW_PIN, LOW);
    digitalWrite(CAR_RED_PIN, HIGH);

    // Step 3: Pedestrian GREEN
    digitalWrite(PED_RED_PIN, LOW);
    digitalWrite(PED_GREEN_PIN, HIGH);
}

// ----- MAIN HANDLER FOR COMMANDS -----
void trafficUpdate(char cmd) {
    if (cmd == 'R') {
        trafficTransitionToRed();
    } else {
        trafficSetNormal();
    }
}
