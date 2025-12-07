#include <Arduino.h>
#include <DHT.h>
#include <ESP32Servo.h>

Servo bumper;

DHT dht(1, DHT22);

int CarSpeed = 0;
int MaxSpeed;
int MaxSpeedBadWeather = 30;
int MaxSpeedGoodWeather = 50;

void SetTrafficLightsCar(bool isRed)
{
  if (isRed)
  {
    digitalWrite(7, LOW);
    digitalWrite(6, HIGH);
  }
  else
  {
    digitalWrite(6, !isRed);
  }
  delay(500);

  digitalWrite(5, isRed);
  digitalWrite(6, false);
  digitalWrite(7, !isRed);
  digitalWrite(8, !isRed);
  digitalWrite(9, isRed);
}

bool oldBumper = false;
void ToggleBumper()
{
  if (oldBumper == false)
  {
    bumper.write(0);
    SetTrafficLightsCar(true);
    oldBumper = true;
  }
  else
  {
    bumper.write(180);
    SetTrafficLightsCar(false);
    oldBumper = false;
  }
}

void setup()
{

  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);

  digitalWrite(7, HIGH);
  digitalWrite(8, HIGH);

  Serial.begin(115200);
  Serial.setTimeout(400);
  pinMode(A0, INPUT);
  bumper.setPeriodHertz(150); // standard 50 hz servo
  bumper.attach(2, 500, 2500);
  dht.begin();
  bumper.write(180);
}

uint oldMillis = 0;

void loop()
{
  if (analogRead(0) < 3900 && dht.readTemperature() <= 0)
  {
    MaxSpeed = MaxSpeedBadWeather;
  }
  else
  {
    MaxSpeed = MaxSpeedGoodWeather;
  }

  if (Serial.available())
  {
    CarSpeed = Serial.readString().toInt();
  }
  if (CarSpeed == 9898)
  {
    MaxSpeed = 30;
    CarSpeed = 0;
  }
  if (CarSpeed == 8989)
  {
    MaxSpeed = 50;
    CarSpeed = 0;
  }

  if (millis() - oldMillis > 2000)
  {
    Serial.println(MaxSpeed);
    oldMillis = millis();
  }

  Serial.println("MaxSpeed: " + String(MaxSpeed));
  if (CarSpeed > MaxSpeed + 4)
  {
    ToggleBumper();
    delay(4000);
    ToggleBumper();
    CarSpeed = 0;
  }
}