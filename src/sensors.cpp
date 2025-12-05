#include <Arduino.h>
#include <DHT.h>
#include "sensors.h"

// --- PIN DEFINITIONS ---
#define DHTPIN 1
#define DHTTYPE DHT22
#define HUMIDITY_PIN 0

// Create DHT object
DHT dht(DHTPIN, DHTTYPE);

void initSensors() {
    dht.begin();
    analogReadResolution(12);
}

// ---- DHT22 FUNCTION ----
void readDHT() {
    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (isnan(h) || isnan(t)) {
        Serial.println("Failed to read from DHT22!");
        return;
    }

    Serial.print("DHT22 Humidity: ");
    Serial.print(h);
    Serial.print(" % | Temp: ");
    Serial.print(t);
    Serial.println(" °C");
}

// ---- ANALOG HUMIDITY FUNCTION ----
void readAnalogHumidity() {
    int raw = analogRead(HUMIDITY_PIN);
    float voltage = (raw / 4095.0) * 3.3;

    Serial.print("Analog Humidity Raw: ");
    Serial.print(raw);
    Serial.print(" | Voltage: ");
    Serial.print(voltage);
    Serial.println(" V");
}
