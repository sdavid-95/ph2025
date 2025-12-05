#include <Arduino.h>
#include "controller.h"
#include "sensors.h"
#include "traffic.h"
#include "actuator.h"

// Thresholds for road condition
#define HUMIDITY_GROUND_WET 2000
#define DHT_HUMIDITY_HIGH 80.0
#define TEMP_FREEZING 3.0

// ----------- Determine Road Condition ------------
bool isRoadConditionBad()
{
    float temperature = getTemperature();     // from sensors.cpp
    float humidityAir = getHumidityAir();     // from sensors.cpp
    int humidityGround = getHumidityGround(); // from sensors.cpp

    if (temperature < TEMP_FREEZING)
        return true;
    if (humidityAir > DHT_HUMIDITY_HIGH)
        return true;
    if (humidityGround > HUMIDITY_GROUND_WET)
        return true;

    return false;
}

// ----------- Speed limit selection --------------
int getSpeedLimitBasedOnConditions()
{
    if (isRoadConditionBad())
        return 30; // bad road → 30 km/h
    return 50;     // good road → 50 km/h
}

// ----------- Main ML message processor ----------
void processCameraMessage(const String &msg)
{

    // 1) HARD RED COMMAND FROM CAMERA
    // "R" means: force red light and flatten bumper, no matter the speed
    if (msg == "R")
    {
        trafficUpdate('R'); // car RED, ped GREEN
        setBumperAngle(0);  // bumper flat (safe)
        return;
    }

    // 2) SPEED MESSAGE: "S:<value>"
    if (msg.startsWith("S:"))
    {
        int speed = msg.substring(2).toInt();

        // Decide if limit is 50 or 30 based on road conditions
        int limit = getSpeedLimitBasedOnConditions();

        // Overspeed = how much the driver exceeds the limit
        int over = speed - limit;

        int angle = 0;

        if (over <= 0)
        {
            // at or below limit → bumper down
            angle = 0;
            trafficUpdate('N'); // normal: car green, ped red
        }
        else
        {
            // over limit → increase angle based on how much over
            if (over <= 10)
                angle = 10;
            else if (over <= 20)
                angle = 20;
            else if (over <= 30)
                angle = 30;
            else
                angle = 40; // way too fast

            // If over the limit by more than 10 km/h -> RED light
            if (over > 10)
            {
                trafficUpdate('R'); // car red, ped green
            }
            else
            {
                trafficUpdate('N'); // still green but with a small bump
            }
        }

        setBumperAngle(angle);
    }
}
