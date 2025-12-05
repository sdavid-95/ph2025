#ifndef TRAFFIC_H
#define TRAFFIC_H

void initTrafficLights();
void trafficSetNormal();        // Car green, Ped red
void trafficTransitionToRed();  // Car green -> yellow -> red
void trafficUpdate(char cmd);   // Called from main

#endif
