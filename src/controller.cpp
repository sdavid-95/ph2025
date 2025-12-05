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
    // Clean the message just in case (remove whitespace/newlines)
    String cleanMsg = msg;
    cleanMsg.trim();

    // 1) HARD RED COMMAND FROM CAMERA
    // "R" means: force red light and flatten bumper (or raise, depending on safety logic)
    if (cleanMsg == "R")
    {
        trafficUpdate('R'); // car RED, ped GREEN
        setBumperAngle(0);  // bumper flat (safe)
        return;
    }
    
    // 2) SPEED MESSAGE: "S:<value>" (e.g., "S:45")
    else if (cleanMsg.startsWith("S:"))
    {
        // Extract the number part after "S:"
        // substring(2) takes everything from index 2 to the end
        String speedString = cleanMsg.substring(2);
        int speed = speedString.toInt();

        // LOGIC: Decide on action based on speed vs. condition
        
        // Decide if limit is 50 or 30 based on road conditions
        int limit = getSpeedLimitBasedOnConditions();

        // Overspeed = how much the driver exceeds the limit
        int over = speed - limit;

        int angle = 0;

        if (over <= 0)
        {
            // At or below limit → bumper down, green light
            angle = 0;
            trafficUpdate('N'); // normal: car green, ped red
        }
        else
        {
            // Dynamic Bumper: The faster they go, the higher the bump
            if (over <= 10)
                angle = 10;
            else if (over <= 20)
                angle = 20;
            else if (over <= 30)
                angle = 30;
            else
                angle = 40; // way too fast

            // Traffic Light Logic:
            // If slightly speeding (<=10 km/h over), maybe just warn with the bump
            // If recklessly speeding (>10 km/h over), turn RED to stop them
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
    
    // 3) EMERGENCY COMMAND "L" (Legacy/Simple Lower)
    // Sometimes helpful to have a direct "L" command for testing
    else if (cleanMsg == "L") 
    {
        trafficUpdate('N');
        setBumperAngle(0);
    }
}