#ifndef CONTROLLER_H
#define CONTROLLER_H

void processCameraMessage(const String &msg);
bool isRoadConditionBad();
int  getSpeedLimitBasedOnConditions();

#endif
