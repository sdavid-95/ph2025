#ifndef ACTUATOR_H
#define ACTUATOR_H

void initBumperServo();
void setBumperAngle(int angle);
void moveBumperBySpeed(int speed);  // optional if you use dynamic speed mapping

#endif
