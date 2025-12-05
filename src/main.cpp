#include <Arduino.h>
#include <DHT.h>

#define DHTPIN 1       // GPIO 1 on ESP32-C3 Super Mini
#define DHTTYPE DHT22  // Sensor type
#define HUMIDITY_PIN 0 

DHT dht(DHTPIN, DHTTYPE);

// Function declaration
void readDHT();
void readAnalogHumidity();

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

void readAnalogHumidity() {
    int raw = analogRead(HUMIDITY_PIN);   // Read ADC (0–4095 on ESP32-C3)
    
    float voltage = (raw / 4095.0) * 3.3;
    
    Serial.print("Humidity Sensor Raw: ");
    Serial.print(raw);
    Serial.print(" | Voltage: ");
    Serial.print(voltage);
    Serial.println(" V");
}
