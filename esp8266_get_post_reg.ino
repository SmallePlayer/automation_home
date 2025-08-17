#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

#define LED_PIN LED_BUILTIN  // Используем встроенный светодиод

const char* ssid = "TP-Link_9108";
const char* password = "12345678";
const char* serverRunStatus = "http://192.168.0.109:8000/run_status";
const char* serverReg = "http://192.168.0.109:8000/reg";
const char* serverStatus = "http://192.168.0.109:8000/led_control/";

const String device_id = "esp8266_0";
WiFiClient client;  // Общий клиент для HTTP-запросов

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  // LED OFF (инверсная логика)
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  sendREG();
}

void loop() {
  static unsigned long lastStatusCheck = 0;
  static unsigned long lastHeartbeat = 0;
  
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
    delay(1000);
    return;
  }

  // Проверка статуса каждые 500 мс
  if (millis() - lastStatusCheck >= 500) {
    sendGetStatus();
    lastStatusCheck = millis();
  }

  // Отправка heartbeat каждые 60 секунд
  if (millis() - lastHeartbeat >= 60000) {
    sendRunStatus();
    lastHeartbeat = millis();
  }
}

void sendRunStatus() {
  HTTPClient http;
  http.begin(client, serverRunStatus);  // Исправлено здесь
  http.addHeader("Content-Type", "application/json");

  String mac = WiFi.macAddress();
  String payload = "{\"mac\":\"" + mac + "\",\"run_status\":\"run\"}";
  
  int httpCode = http.POST(payload);
  
  if (httpCode > 0) {
    Serial.printf("Heartbeat sent. Status: %d\n", httpCode);
  } else {
    Serial.printf("Heartbeat failed: %s\n", http.errorToString(httpCode).c_str());
  }
  
  http.end();
}

void sendGetStatus() {
  HTTPClient http;
  String url = String(serverStatus) + device_id;
  http.begin(client, url);  // Исправлено здесь
  
  int httpCode = http.GET();
  
  if (httpCode == HTTP_CODE_OK) {
    String response = http.getString();

    StaticJsonDocument<128> doc;
    DeserializationError error = deserializeJson(doc, response);
    
    if (!error) {
      const char* status = doc["status"];
      Serial.print("LED status: ");
      Serial.println(status);
      
      if (strcmp(status, "on") == 0) {
        digitalWrite(LED_PIN, LOW);  // Включение (инверсная логика)
      } 
      else if (strcmp(status, "off") == 0) {
        digitalWrite(LED_PIN, HIGH);  // Выключение
      }
      else {
        blinkLED();
      }
    } else {
      Serial.println("JSON parsing error!");
      blinkLED();
    }
  } else if (httpCode > 0) {
    Serial.printf("HTTP error: %s\n", http.errorToString(httpCode).c_str());
    blinkLED();
  } else {
    Serial.printf("Connection failed: %s\n", http.errorToString(httpCode).c_str());
    blinkLED();
  }
  
  http.end();
}

void sendREG() {
  HTTPClient http;
  http.begin(client, serverReg);  // Исправлено здесь
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<200> doc;
  doc["device_id"] = device_id;
  doc["mac"] = WiFi.macAddress();
  doc["ipAddress"] = WiFi.localIP().toString();
  
  String payload;
  serializeJson(doc, payload);
  
  int httpCode = http.POST(payload);
  
  if (httpCode > 0) {
    Serial.printf("Registration successful: %d\n", httpCode);
  } else {
    Serial.printf("Registration failed: %s\n", http.errorToString(httpCode).c_str());
  }
  
  http.end();
}

void blinkLED() {
  digitalWrite(LED_PIN, LOW);
  delay(100);
  digitalWrite(LED_PIN, HIGH);
  delay(100);
}