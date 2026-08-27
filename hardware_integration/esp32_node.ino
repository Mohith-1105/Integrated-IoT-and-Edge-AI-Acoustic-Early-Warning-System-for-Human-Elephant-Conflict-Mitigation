/*
 * Integrated IoT and Edge-AI Acoustic Early Warning System
 * ESP32 Field Node Hardware Firmware
 * Department of AI & ML, Sri Sairam College of Engineering (Batch 10)
 * 
 * Sensors: PIR (GPIO 13), Acoustic Mic (ADC GPIO 34), Vibration (GPIO 35), GPS (UART2)
 */

#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://YOUR_LAPTOP_IP:5000/api/nodes";

#define PIR_PIN 13
#define VIB_PIN 35
#define MIC_PIN 34

void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);
  pinMode(VIB_PIN, INPUT);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nESP32 Field Node Connected to Control Station!");
}

void loop() {
  int pirVal = digitalRead(PIR_PIN);
  int vibVal = analogRead(VIB_PIN);
  int micVal = analogRead(MIC_PIN);

  // Convert raw analog mic sample to estimated dB
  float acousticDb = (micVal / 4095.0) * 100.0;
  float vibrationMs2 = (vibVal / 4095.0) * 9.8;

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"id\":\"ESP32-NODE-PHYSICAL\",\"pir\":" + String(pirVal) + 
                         ",\"vibration\":" + String(vibrationMs2) + 
                         ",\"acoustic_db\":" + String(acousticDb) + "}";

    int httpResponseCode = http.POST(jsonPayload);
    Serial.print("Telemetry Sent, Response Code: ");
    Serial.println(httpResponseCode);
    http.end();
  }

  delay(2000); // 2-second telemetry cycle
}
