#include <Arduino.h>
#include <DHT.h>

#define DHTPIN 1       // GPIO 1 on ESP32-C3 Super Mini
#define DHTTYPE DHT22  // Sensor type

DHT dht(DHTPIN, DHTTYPE);

// Function declaration
void readDHT();

void setup() {
  Serial.begin(115200);
  dht.begin();
}

void loop() {
  readDHT();
  delay(2000);  // DHT22 needs 2 sec between reads
}

// Function to read temperature & humidity
void readDHT() {
  float h = dht.readHumidity();
  float t = dht.readTemperature(); // Celsius

  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT22!");
    return;
  }

  Serial.print("Humidity: ");
  Serial.print(h);
  Serial.print(" %  |  Temperature: ");
  Serial.print(t);
  Serial.println(" °C");
}
