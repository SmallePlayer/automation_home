#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#define LED_PIN 2

const char* ssid = "TP-Link_9108";
const char* password = "12345678";
const char* serverURL = "http://192.168.0.109:8000";
const char* serverRunStatus = "http://192.168.0.109:8000/run_status";
const char* serverReg = "http://192.168.0.109:8000/reg";
const char* serverStatus = "http://192.168.0.109:8000/led_control/";

const String device_id = "esp32_0";

int delay_time = 0;


void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");

  sendREG();
  sendRunStatus();
}

void loop() {
  static unsigned long lastGetTime = 0;
  static unsigned long lastRunTime = 0;
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Reconnecting WiFi...");
    WiFi.reconnect();
  }
  delay_time *= 1000;
  if (millis() - lastRunTime >= delay_time) {
    sendRunStatus();
    lastRunTime = millis();
  }

  if (millis() - lastGetTime > 500) {
    sendGetStatus();
    lastGetTime = millis();
  }

}

void sendRunStatus() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected!");
    return;
  }

  HTTPClient http;
  http.begin(serverRunStatus);
  http.addHeader("Content-Type", "application/json");

  String mac = WiFi.macAddress();
  String status = "on";

  String payload = "{\"device_id\":\"" + device_id + "\"}";
  
  int httpCode = http.POST(payload);

  String response = http.getString();
  StaticJsonDocument<200> responseDoc;
  DeserializationError error = deserializeJson(responseDoc, response);
  const char*  char_delay_time = responseDoc["delay"];
  String string_delay_time = String(char_delay_time);
  delay_time = string_delay_time.toInt();
  
  if (httpCode > 0) {
    Serial.printf("Registration response: %d\n", httpCode);
  } else {
    Serial.printf("Registration failed: %s\n", http.errorToString(httpCode).c_str());
  }
  
  http.end();
}


void sendGetStatus() {
  HTTPClient http;
  String url = String(serverStatus) + device_id;
  http.begin(url);
  
  int httpCode = http.GET();
  
  if (httpCode > 0) {
    Serial.printf("[GET] Response code: %d\n", httpCode);
    
    
    if (httpCode == HTTP_CODE_OK) {
      String response = http.getString();

      StaticJsonDocument<128> doc;  
      DeserializationError error = deserializeJson(doc, response);


    if (!error) {
      const char* status = doc["status"];
      Serial.print("LED status: ");
      Serial.println(status);
      
      if (strcmp(status, "on") == 0) {
         digitalWrite(LED_PIN, HIGH); 
      } 
      else if (strcmp(status, "off") == 0) {
        digitalWrite(LED_PIN, LOW);  
      }
      else {
        blinkLED();
      }
    }
    else {
      blinkLED();
    }
  } else {
    Serial.printf("[GET] Failed: %s\n", http.errorToString(httpCode).c_str());
    blinkLED();
  }
  
  http.end();
  }
}

void sendREG() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected!");
    return;
  }

  HTTPClient http;
  http.begin(serverReg);
  http.addHeader("Content-Type", "application/json");
  String mac = WiFi.macAddress();
  String ip = WiFi.localIP().toString();
  
  StaticJsonDocument<200> doc;
  doc["device_id"] = device_id;
  doc["mac"] = WiFi.macAddress();
  doc["ipAddress"] = WiFi.localIP().toString();
  
  String payload; 
  serializeJson(doc, payload);
  int httpCode = http.POST(payload);

  String response = http.getString();
  StaticJsonDocument<200> responseDoc;
  DeserializationError error = deserializeJson(responseDoc, response);
  const char*  char_delay_time = responseDoc["delay"];
  String string_delay_time = String(char_delay_time);
  delay_time = string_delay_time.toInt();
  
  if (httpCode > 0) {
    Serial.printf("Response: %d\n", httpCode);
  } else {
    Serial.printf("Error sending: %s\n", http.errorToString(httpCode).c_str());
  }
  
  http.end();
}

void blinkLED() {
  digitalWrite(LED_PIN, LOW);  // Включить
  delay(100);
  digitalWrite(LED_PIN, HIGH); // Выключить
  delay(100);
}