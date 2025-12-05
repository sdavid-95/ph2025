#include <Arduino.h>
#include <ESP32Servo.h>
#include "actuator.h"

static Servo bumperServo;
static bool servoInitialized = false;

const int SERVO_PIN = 5;

// Safe angle limits for your bumper
const int ANGLE_MIN = 0;
const int ANGLE_MAX = 60;

// -----------------------------------
void initBumperServo() {
    if (!servoInitialized) {
        bumperServo.attach(SERVO_PIN, 500, 2400);  // recommended pulse range for ESP32
        servoInitialized = true;
        bumperServo.write(0);                      // start flat
        delay(200);
    }
}

// -----------------------------------
void setBumperAngle(int angle) {
    initBumperServo();                  // ensure servo is attached once
    angle = constrain(angle, ANGLE_MIN, ANGLE_MAX);
    bumperServo.write(angle);
}

// -----------------------------------
// Optional helper for speed mapping
void moveBumperBySpeed(int speed) {
    initBumperServo();

    int angle = 0;

    if (speed < 10) angle = 0;
    else if (speed < 20) angle = 10;
    else if (speed < 30) angle = 20;
    else if (speed < 40) angle = 30;
    else angle = 40;

    setBumperAngle(angle);
}
