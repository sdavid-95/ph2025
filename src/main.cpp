#include <Arduino.h>
#include <DHT.h>
#include <ESP32Servo.h>

// Definirea Servomotorului
Servo bumper;

// Definirea senzorului DHT
DHT dht(1, DHT22);

// Variabile de stare
int CarSpeed = 0;
int MaxSpeed = 50;
const int MaxSpeedBadWeather = 30;
const int MaxSpeedGoodWeather = 50;

// Variabila pentru a urmari starea rampei (True=Ridicată, False=Coboarată)
bool isBumperRaised = false;

// Definirea Pinilor (presupunand ca pinul 5 este LED-ul Roșu de pe partea rampei)
// (Am modificat SetTrafficLightsCar pentru a folosi pinii direct)
const int PIN_RED_LIGHT = 5;
const int PIN_GREEN_LIGHT = 7;
const int PIN_BUMPER_SERVO = 2;


void SetTrafficLightsCar(bool isRed){
  // Logica semaforului simplificata pentru siguranta
  if(isRed){
    // Rosu ON, Verde OFF
    digitalWrite(PIN_RED_LIGHT, HIGH); 
    digitalWrite(PIN_GREEN_LIGHT, LOW);
  }else{
    // Rosu OFF, Verde ON
    digitalWrite(PIN_RED_LIGHT, LOW);
    digitalWrite(PIN_GREEN_LIGHT, HIGH);
  }
  // Pinii 6, 8, 9 au fost ignorati in aceasta functie pentru simplitate
}

// Functia care gestioneaza ridicarea si coborarea rampei
void ToggleBumper(bool raise) {
  if (raise && !isBumperRaised) {
    // Ridicare
    bumper.write(180);
    SetTrafficLightsCar(true); // Semafor Rosu
    isBumperRaised = true;
    Serial.println("Action: Bumper RAISED");
  } else if (!raise && isBumperRaised) {
    // Coborare
    // Asteapta 4 secunde cat timp rampa este ridicata (simularea duratei obstacolului)
    delay(4000); 
    
    bumper.write(0);
    SetTrafficLightsCar(false); // Semafor Verde
    isBumperRaised = false;
    Serial.println("Action: Bumper LOWERED");
  }
}

void setup() {

pinMode(5, OUTPUT);
pinMode(6, OUTPUT);
pinMode(7, OUTPUT);
pinMode(8, OUTPUT);
pinMode(9, OUTPUT);

digitalWrite(7, HIGH);
digitalWrite(8, HIGH);

  Serial.begin(115200);
  Serial.setTimeout(50);
  pinMode(A0, INPUT);
  
  // Atasare Servomotor
  bumper.setPeriodHertz(50); 	
  bumper.attach(PIN_BUMPER_SERVO, 500, 10000);
  bumper.write(0); // Seteaza rampa jos la pornire
  
  dht.begin();
}

void loop() {
  // 1. Logică de setare a vitezei maxime în funcție de vreme
  if(analogRead(A0) < 3900 && dht.readTemperature() <= 0){
    MaxSpeed = MaxSpeedBadWeather;
  }else{
    MaxSpeed = MaxSpeedGoodWeather;
  }

  // 2. Primire date Serial
  while(Serial.available()){
    // Citim semnalul unic trimis de Python (ex: b'R' sau b'S')
    char receivedChar = Serial.read(); 
    
    if (receivedChar == 'R' || receivedChar == 'E' || receivedChar == 'S') {
      
      // Decizie bazata pe semnal
      if (receivedChar == 'R') {
        // R = Viteză prea mare, Ridică rampa (doar dacă nu e deja ridicată)
        ToggleBumper(true); 
      } else if (receivedChar == 'E' || receivedChar == 'S') {
        // E = Urgență / S = Sigur (sub limită). Asigură-te că rampa este jos.
        ToggleBumper(false);
      }
      
      // IESIRE IMEDIATA DIN LOOP SERIAL
      // Aceasta este cheia. Odată citit un semnal valid, ignorăm restul.
      // Daca nu se iese, se poate re-declansa acțiunea.
      break; 
    }
  }

  // NU MAI AVEM NEVOIE DE LOGICA CarSpeed > MaxSpeed+4 AICI!
  // Decizia de a ridica/coborî este luată ÎN interiorul buclei while(Serial.available()).
}