#ifndef SENSORS_H
#define SENSORS_H

void initSensors();
void readDHT();
void readAnalogHumidity();

float getTemperature();
float getHumidityAir();
int   getHumidityGround();

#endif
