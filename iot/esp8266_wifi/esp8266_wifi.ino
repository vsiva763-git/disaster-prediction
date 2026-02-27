/*
 * Tsunami Alert System - ESP8266 WiFi Module
 * 
 * This code runs on ESP8266 (NodeMCU/Wemos D1)
 * Connects to WiFi and receives HTTP requests from the server
 * Forwards alerts to Arduino UNO via Serial
 * 
 * Hardware Connections:
 * ESP8266 TX (GPIO1/D10) -> Arduino UNO RX (Pin 6 via SoftwareSerial)
 * ESP8266 RX (GPIO3/D9)  -> Arduino UNO TX (Pin 7 via SoftwareSerial) through voltage divider
 * ESP8266 GND -> Arduino UNO GND
 * ESP8266 3.3V -> From Arduino 3.3V or separate regulator
 * 
 * Note: ESP8266 is 3.3V logic, use voltage divider for TX from Arduino (5V)
 * Voltage divider: Arduino TX -> 1kΩ -> ESP RX -> 2kΩ -> GND
 */

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <EEPROM.h>

// ========== CONFIGURATION ==========
// WiFi credentials - CHANGE THESE
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// Server settings
const char* DEVICE_NAME = "TsunamiAlert_01";
const int HTTP_PORT = 80;

// ========== GLOBALS ==========
ESP8266WebServer server(HTTP_PORT);

// Device state
bool alertActive = false;
int currentAlertLevel = 0;
String currentMessage = "";
String lastEarthquake = "None";
unsigned long lastPing = 0;
unsigned long lastServerCheck = 0;
bool arduinoConnected = false;

// Alert levels
const char* ALERT_NAMES[] = {"NONE", "WATCH", "ADVISORY", "WARNING", "CRITICAL"};

void setup() {
  // Initialize serial for Arduino UNO communication
  Serial.begin(9600);
  delay(100);
  
  Serial.println("\n\n=== Tsunami Alert ESP8266 ===");
  
  // Initialize EEPROM
  EEPROM.begin(512);
  
  // Connect to WiFi
  connectWiFi();
  
  // Setup HTTP server routes
  setupRoutes();
  
  // Start server
  server.begin();
  Serial.println("HTTP server started on port " + String(HTTP_PORT));
  Serial.println("Device IP: " + WiFi.localIP().toString());
  
  // Check Arduino connection
  checkArduinoConnection();
}

void loop() {
  // Handle HTTP requests
  server.handleClient();
  
  // Periodic ping to Arduino
  if (millis() - lastPing > 30000) {
    checkArduinoConnection();
    lastPing = millis();
  }
  
  // Check for Arduino responses
  if (Serial.available()) {
    String response = Serial.readStringUntil('\n');
    response.trim();
    handleArduinoResponse(response);
  }
}

void connectWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.println("IP address: " + WiFi.localIP().toString());
    Serial.println("Signal strength (RSSI): " + String(WiFi.RSSI()) + " dBm");
  } else {
    Serial.println("\nWiFi connection failed! Starting AP mode...");
    startAPMode();
  }
}

void startAPMode() {
  WiFi.mode(WIFI_AP);
  WiFi.softAP("TsunamiAlert_Setup", "tsunami123");
  Serial.println("AP Mode started");
  Serial.println("Connect to 'TsunamiAlert_Setup' with password 'tsunami123'");
  Serial.println("Then visit http://192.168.4.1 to configure");
}

void setupRoutes() {
  // Root - device info
  server.on("/", HTTP_GET, handleRoot);
  
  // Health check
  server.on("/health", HTTP_GET, handleHealth);
  
  // Receive alert from main server
  server.on("/alert", HTTP_POST, handleAlert);
  
  // Clear alert
  server.on("/clear", HTTP_POST, handleClear);
  server.on("/clear", HTTP_GET, handleClear);
  
  // Test alert
  server.on("/test", HTTP_GET, handleTest);
  server.on("/test", HTTP_POST, handleTest);
  
  // Get status
  server.on("/status", HTTP_GET, handleStatus);
  
  // Configure WiFi
  server.on("/configure", HTTP_POST, handleConfigure);
  
  // CORS preflight
  server.on("/alert", HTTP_OPTIONS, handleCORS);
  server.on("/clear", HTTP_OPTIONS, handleCORS);
  server.on("/test", HTTP_OPTIONS, handleCORS);
}

void handleCORS() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.send(200, "text/plain", "");
}

void handleRoot() {
  String html = "<!DOCTYPE html><html><head><title>Tsunami Alert Device</title>";
  html += "<style>body{font-family:Arial;margin:20px;background:#1a1a2e;color:#eee;}";
  html += ".card{background:#16213e;padding:20px;border-radius:10px;margin:10px 0;}";
  html += ".alert{color:#ff6b6b;}.ok{color:#4ecdc4;}</style></head><body>";
  html += "<h1>🌊 Tsunami Alert Device</h1>";
  html += "<div class='card'>";
  html += "<h2>Device Info</h2>";
  html += "<p><b>Name:</b> " + String(DEVICE_NAME) + "</p>";
  html += "<p><b>IP:</b> " + WiFi.localIP().toString() + "</p>";
  html += "<p><b>WiFi:</b> " + String(WIFI_SSID) + " (" + String(WiFi.RSSI()) + " dBm)</p>";
  html += "<p><b>Arduino:</b> <span class='" + String(arduinoConnected ? "ok" : "alert") + "'>";
  html += String(arduinoConnected ? "Connected" : "Disconnected") + "</span></p>";
  html += "</div>";
  html += "<div class='card'>";
  html += "<h2>Current Status</h2>";
  html += "<p><b>Alert Level:</b> <span class='" + String(currentAlertLevel > 0 ? "alert" : "ok") + "'>";
  html += String(ALERT_NAMES[currentAlertLevel]) + "</span></p>";
  html += "<p><b>Message:</b> " + currentMessage + "</p>";
  html += "</div>";
  html += "<div class='card'>";
  html += "<h2>API Endpoints</h2>";
  html += "<p>POST /alert - Send alert {level, message, earthquake}</p>";
  html += "<p>GET/POST /clear - Clear current alert</p>";
  html += "<p>GET/POST /test - Test buzzer and LCD</p>";
  html += "<p>GET /status - Get device status</p>";
  html += "<p>GET /health - Health check</p>";
  html += "</div></body></html>";
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "text/html", html);
}

void handleHealth() {
  StaticJsonDocument<256> doc;
  doc["status"] = "online";
  doc["device"] = DEVICE_NAME;
  doc["ip"] = WiFi.localIP().toString();
  doc["rssi"] = WiFi.RSSI();
  doc["arduino_connected"] = arduinoConnected;
  doc["uptime_seconds"] = millis() / 1000;
  
  String response;
  serializeJson(doc, response);
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", response);
}

void handleAlert() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  
  if (!server.hasArg("plain")) {
    server.send(400, "application/json", "{\"error\":\"No body provided\"}");
    return;
  }
  
  String body = server.arg("plain");
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, body);
  
  if (error) {
    server.send(400, "application/json", "{\"error\":\"Invalid JSON\"}");
    return;
  }
  
  int level = doc["level"] | 1;
  const char* message = doc["message"] | "Alert!";
  const char* earthquake = doc["earthquake"] | "Unknown";
  
  // Validate level
  if (level < 0 || level > 4) level = 1;
  
  // Update state
  currentAlertLevel = level;
  currentMessage = String(message);
  lastEarthquake = String(earthquake);
  alertActive = (level > 0);
  
  // Send to Arduino
  String cmd = "ALERT:" + String(level) + ":" + currentMessage;
  Serial.println(cmd);
  
  // Response
  StaticJsonDocument<256> resp;
  resp["success"] = true;
  resp["level"] = level;
  resp["level_name"] = ALERT_NAMES[level];
  resp["message"] = message;
  resp["sent_to_arduino"] = true;
  
  String respStr;
  serializeJson(resp, respStr);
  server.send(200, "application/json", respStr);
}

void handleClear() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  
  currentAlertLevel = 0;
  currentMessage = "";
  alertActive = false;
  
  // Send to Arduino
  Serial.println("CLEAR");
  
  server.send(200, "application/json", "{\"success\":true,\"message\":\"Alert cleared\"}");
}

void handleTest() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  
  // Send test command to Arduino
  Serial.println("TEST");
  
  server.send(200, "application/json", "{\"success\":true,\"message\":\"Test command sent to Arduino\"}");
}

void handleStatus() {
  StaticJsonDocument<512> doc;
  
  doc["device_name"] = DEVICE_NAME;
  doc["ip_address"] = WiFi.localIP().toString();
  doc["wifi_ssid"] = WIFI_SSID;
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["arduino_connected"] = arduinoConnected;
  doc["alert_active"] = alertActive;
  doc["alert_level"] = currentAlertLevel;
  doc["alert_level_name"] = ALERT_NAMES[currentAlertLevel];
  doc["current_message"] = currentMessage;
  doc["last_earthquake"] = lastEarthquake;
  doc["uptime_ms"] = millis();
  doc["free_heap"] = ESP.getFreeHeap();
  
  String response;
  serializeJson(doc, response);
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", response);
}

void handleConfigure() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  
  if (!server.hasArg("plain")) {
    server.send(400, "application/json", "{\"error\":\"No configuration provided\"}");
    return;
  }
  
  String body = server.arg("plain");
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, body);
  
  if (error) {
    server.send(400, "application/json", "{\"error\":\"Invalid JSON\"}");
    return;
  }
  
  // WiFi configuration would be saved to EEPROM here
  // For now, just acknowledge
  server.send(200, "application/json", "{\"success\":true,\"message\":\"Configuration received. Restart device to apply.\"}");
}

void checkArduinoConnection() {
  Serial.println("PING");
  delay(100);
  
  unsigned long startTime = millis();
  while (millis() - startTime < 500) {
    if (Serial.available()) {
      String response = Serial.readStringUntil('\n');
      response.trim();
      if (response == "PONG") {
        arduinoConnected = true;
        return;
      }
    }
  }
  arduinoConnected = false;
}

void handleArduinoResponse(String response) {
  if (response.startsWith("ACK:")) {
    // Acknowledgment from Arduino
    // Could log or handle specific acks
  }
  else if (response.startsWith("STATUS:")) {
    // Status update from Arduino
    // Parse and update local state if needed
  }
  else if (response == "PONG") {
    arduinoConnected = true;
  }
}
