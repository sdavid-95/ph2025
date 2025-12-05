#include <Arduino.h>
#include <DHT.h>

int myFunction(int, int);

void moveBumper(bool move_bumper)
{

}

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
