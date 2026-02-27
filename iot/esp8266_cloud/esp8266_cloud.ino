/*
 * ESP8266 Cloud Tsunami Alert Receiver
 * 
 * This version POLLS the cloud server for alerts, enabling:
 * - Cloud deployment (Codespace, Heroku, Railway, etc.)
 * - No need for direct server-to-device connection
 * - Works through NAT and firewalls
 * 
 * How it works:
 * 1. ESP8266 connects to WiFi
 * 2. Every few seconds, it polls the cloud server for alert status
 * 3. If alert is active, it forwards to Arduino via Serial
 * 
 * Hardware Connections:
 * ESP8266 VCC  -> 3.3V
 * ESP8266 GND  -> GND
 * ESP8266 TX   -> Arduino Pin 6 (SoftwareSerial RX)
 * ESP8266 RX   -> Arduino Pin 7 (through voltage divider)
 * ESP8266 CH_PD -> 3.3V
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>

// ============ CONFIGURATION ============
// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Cloud server URL (change this to your deployed server)
// Examples:
// - Codespace: "https://your-codespace-name-5000.app.github.dev"
// - Heroku: "https://your-app.herokuapp.com"
// - Railway: "https://your-app.railway.app"
// - Local: "http://192.168.1.100:5000"
const char* serverUrl = "https://your-server-url.com";

// Device identifier
const char* deviceName = "TsunamiAlert_01";

// Poll interval in milliseconds (5 seconds)
const unsigned long POLL_INTERVAL = 5000;

// ========================================

WiFiClient wifiClient;
HTTPClient http;

// State tracking
bool lastAlertState = false;
int lastAlertLevel = 0;
String lastMessage = "";
unsigned long lastPollTime = 0;
unsigned long lastHeartbeat = 0;

void setup() {
    Serial.begin(9600);
    delay(1000);
    
    Serial.println("\n\n================================");
    Serial.println("Tsunami Alert - Cloud Mode");
    Serial.println("================================");
    Serial.print("Device: ");
    Serial.println(deviceName);
    Serial.print("Server: ");
    Serial.println(serverUrl);
    
    // Connect to WiFi
    connectWiFi();
    
    Serial.println("\nSystem ready - polling for alerts...");
    Serial.println("READY");
}

void loop() {
    // Check WiFi connection
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi lost - reconnecting...");
        connectWiFi();
    }
    
    // Poll server for alerts
    unsigned long currentTime = millis();
    if (currentTime - lastPollTime >= POLL_INTERVAL) {
        lastPollTime = currentTime;
        pollServer();
    }
    
    // Heartbeat every 30 seconds
    if (currentTime - lastHeartbeat >= 30000) {
        lastHeartbeat = currentTime;
        Serial.println("HEARTBEAT");
    }
}

void connectWiFi() {
    WiFi.hostname(deviceName);
    WiFi.begin(ssid, password);
    
    Serial.print("Connecting to WiFi");
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi Connected!");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
        Serial.print("Signal Strength: ");
        Serial.print(WiFi.RSSI());
        Serial.println(" dBm");
    } else {
        Serial.println("\nWiFi connection failed!");
        Serial.println("Restarting in 5 seconds...");
        delay(5000);
        ESP.restart();
    }
}

void pollServer() {
    String url = String(serverUrl) + "/iot/cloud/poll?device=" + String(deviceName);
    
    http.begin(wifiClient, url);
    http.setTimeout(10000);
    http.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);  // Follow redirects
    http.addHeader("User-Agent", "ESP8266-TsunamiAlert/1.0");
    
    int httpCode = http.GET();
    
    if (httpCode == HTTP_CODE_OK) {
        String payload = http.getString();
        
        // Parse JSON response
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, payload);
        
        if (!error) {
            bool alertActive = doc["active"] | false;
            int level = doc["level"] | 0;
            const char* message = doc["message"] | "";
            
            // Check if alert state changed
            if (alertActive && (!lastAlertState || level != lastAlertLevel)) {
                // New alert or level changed
                Serial.print("ALERT:");
                Serial.print(level);
                Serial.print(":");
                Serial.println(message);
                
                lastAlertState = true;
                lastAlertLevel = level;
                lastMessage = String(message);
                
                Serial.println(">>> Alert sent to Arduino");
            }
            else if (!alertActive && lastAlertState) {
                // Alert cleared
                Serial.println("CLEAR");
                
                lastAlertState = false;
                lastAlertLevel = 0;
                lastMessage = "";
                
                Serial.println(">>> Clear sent to Arduino");
            }
            // else: no change, do nothing
        } else {
            Serial.print("JSON parse error: ");
            Serial.println(error.c_str());
        }
    } else if (httpCode > 0) {
        Serial.print("HTTP Error: ");
        Serial.println(httpCode);
    } else {
        Serial.print("Connection failed: ");
        Serial.println(http.errorToString(httpCode));
    }
    
    http.end();
}
