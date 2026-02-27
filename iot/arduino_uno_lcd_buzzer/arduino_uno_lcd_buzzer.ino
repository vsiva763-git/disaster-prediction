/*
 * Tsunami Alert System - Arduino UNO + LCD + Buzzer
 * 
 * Hardware:
 * - Arduino UNO
 * - LCD 16x2 (without I2C) - 4-bit mode
 * - Buzzer (active)
 * 
 * LCD Pin Connections (4-bit mode):
 * - RS -> Pin 12
 * - EN -> Pin 11
 * - D4 -> Pin 5
 * - D5 -> Pin 4
 * - D6 -> Pin 3
 * - D7 -> Pin 2
 * - VSS -> GND
 * - VDD -> 5V
 * - V0 -> Potentiometer (contrast)
 * - A (LED+) -> 5V through 220Ω
 * - K (LED-) -> GND
 * 
 * Buzzer: Pin 8
 * 
 * Serial Communication with ESP8266:
 * - UNO TX (Pin 1) -> ESP8266 RX (through voltage divider)
 * - UNO RX (Pin 0) -> ESP8266 TX
 * - Use Software Serial on pins 6, 7 to keep hardware serial free for debugging
 */

#include <LiquidCrystal.h>
#include <SoftwareSerial.h>

// LCD pins (RS, EN, D4, D5, D6, D7)
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// Software Serial for ESP8266 communication
SoftwareSerial espSerial(6, 7); // RX, TX (connect to ESP8266 TX, RX)

// Buzzer pin
const int BUZZER_PIN = 8;

// Alert states
enum AlertLevel {
  ALERT_NONE = 0,
  ALERT_WATCH = 1,
  ALERT_ADVISORY = 2,
  ALERT_WARNING = 3,
  ALERT_CRITICAL = 4
};

// Current state
AlertLevel currentAlert = ALERT_NONE;
String lastMessage = "";
unsigned long lastUpdate = 0;
bool buzzerActive = false;
unsigned long buzzerStartTime = 0;
int buzzerPattern = 0;

// Custom characters for LCD
byte waveChar[8] = {
  B00000,
  B00000,
  B01010,
  B10101,
  B01010,
  B00000,
  B00000,
  B00000
};

byte alertChar[8] = {
  B00100,
  B01110,
  B01110,
  B01110,
  B11111,
  B00000,
  B00100,
  B00000
};

void setup() {
  // Initialize serial for debug
  Serial.begin(9600);
  
  // Initialize ESP8266 communication
  espSerial.begin(9600);
  
  // Initialize LCD
  lcd.begin(16, 2);
  lcd.createChar(0, waveChar);
  lcd.createChar(1, alertChar);
  
  // Initialize buzzer
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  
  // Welcome message
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Tsunami Alert");
  lcd.setCursor(0, 1);
  lcd.print("System Ready");
  
  // Startup beep
  tone(BUZZER_PIN, 1000, 200);
  delay(300);
  tone(BUZZER_PIN, 1500, 200);
  
  Serial.println("Tsunami Alert System Initialized");
  delay(2000);
  
  showNormalStatus();
}

void loop() {
  // Check for commands from ESP8266
  if (espSerial.available()) {
    String command = espSerial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }
  
  // Check for debug commands from Serial Monitor
  if (Serial.available()) {
    String debugCmd = Serial.readStringUntil('\n');
    debugCmd.trim();
    processCommand(debugCmd);
  }
  
  // Handle buzzer patterns
  handleBuzzer();
  
  // Update display periodically
  if (millis() - lastUpdate > 5000 && currentAlert == ALERT_NONE) {
    showNormalStatus();
  }
}

void processCommand(String cmd) {
  Serial.print("Received: ");
  Serial.println(cmd);
  
  if (cmd.startsWith("ALERT:")) {
    // Parse alert command: ALERT:LEVEL:MESSAGE
    int firstColon = cmd.indexOf(':');
    int secondColon = cmd.indexOf(':', firstColon + 1);
    
    if (secondColon > firstColon) {
      String levelStr = cmd.substring(firstColon + 1, secondColon);
      String message = cmd.substring(secondColon + 1);
      
      int level = levelStr.toInt();
      setAlert((AlertLevel)level, message);
    }
  }
  else if (cmd == "CLEAR" || cmd == "RESET") {
    clearAlert();
  }
  else if (cmd == "TEST") {
    testAlert();
  }
  else if (cmd == "STATUS") {
    sendStatus();
  }
  else if (cmd == "PING") {
    espSerial.println("PONG");
    Serial.println("PONG");
  }
}

void setAlert(AlertLevel level, String message) {
  currentAlert = level;
  lastMessage = message;
  lastUpdate = millis();
  
  lcd.clear();
  
  switch(level) {
    case ALERT_WATCH:
      lcd.setCursor(0, 0);
      lcd.write(byte(0)); // Wave icon
      lcd.print(" WATCH ");
      lcd.write(byte(0));
      buzzerPattern = 1;
      break;
      
    case ALERT_ADVISORY:
      lcd.setCursor(0, 0);
      lcd.write(byte(1)); // Alert icon
      lcd.print(" ADVISORY ");
      lcd.write(byte(1));
      buzzerPattern = 2;
      break;
      
    case ALERT_WARNING:
      lcd.setCursor(0, 0);
      lcd.print("!! WARNING !!");
      buzzerPattern = 3;
      break;
      
    case ALERT_CRITICAL:
      lcd.setCursor(0, 0);
      lcd.print("*** TSUNAMI ***");
      buzzerPattern = 4;
      break;
      
    default:
      showNormalStatus();
      return;
  }
  
  // Display message on second line (scroll if needed)
  lcd.setCursor(0, 1);
  if (message.length() <= 16) {
    lcd.print(message);
  } else {
    lcd.print(message.substring(0, 16));
  }
  
  // Start buzzer
  buzzerActive = true;
  buzzerStartTime = millis();
  
  // Send acknowledgment
  espSerial.println("ACK:ALERT_SET");
  Serial.println("Alert set: " + String(level) + " - " + message);
}

void clearAlert() {
  currentAlert = ALERT_NONE;
  buzzerActive = false;
  buzzerPattern = 0;
  digitalWrite(BUZZER_PIN, LOW);
  noTone(BUZZER_PIN);
  
  showNormalStatus();
  
  espSerial.println("ACK:ALERT_CLEARED");
  Serial.println("Alert cleared");
}

void testAlert() {
  // Test sequence
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("SYSTEM TEST");
  lcd.setCursor(0, 1);
  lcd.print("Testing...");
  
  // Test buzzer tones
  tone(BUZZER_PIN, 500, 200);
  delay(300);
  tone(BUZZER_PIN, 1000, 200);
  delay(300);
  tone(BUZZER_PIN, 1500, 200);
  delay(300);
  tone(BUZZER_PIN, 2000, 200);
  delay(500);
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("TEST COMPLETE");
  lcd.setCursor(0, 1);
  lcd.print("All OK!");
  
  espSerial.println("ACK:TEST_OK");
  Serial.println("Test completed");
  
  delay(2000);
  showNormalStatus();
}

void sendStatus() {
  String status = "STATUS:";
  status += String(currentAlert);
  status += ":";
  status += lastMessage;
  
  espSerial.println(status);
  Serial.println(status);
}

void showNormalStatus() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.write(byte(0));
  lcd.print(" No Tsunami ");
  lcd.write(byte(0));
  lcd.setCursor(0, 1);
  lcd.print("India Coast Safe");
  lastUpdate = millis();
}

void handleBuzzer() {
  if (!buzzerActive) {
    return;
  }
  
  unsigned long elapsed = millis() - buzzerStartTime;
  
  switch(buzzerPattern) {
    case 1: // Watch - single beep every 5 seconds
      if (elapsed < 200) {
        tone(BUZZER_PIN, 800);
      } else {
        noTone(BUZZER_PIN);
        if (elapsed > 5000) {
          buzzerStartTime = millis();
        }
      }
      break;
      
    case 2: // Advisory - double beep every 3 seconds
      if (elapsed < 150) {
        tone(BUZZER_PIN, 1000);
      } else if (elapsed < 300) {
        noTone(BUZZER_PIN);
      } else if (elapsed < 450) {
        tone(BUZZER_PIN, 1000);
      } else {
        noTone(BUZZER_PIN);
        if (elapsed > 3000) {
          buzzerStartTime = millis();
        }
      }
      break;
      
    case 3: // Warning - rapid beeping
      if ((elapsed / 200) % 2 == 0) {
        tone(BUZZER_PIN, 1500);
      } else {
        noTone(BUZZER_PIN);
      }
      // Auto-stop after 30 seconds, then repeat
      if (elapsed > 30000) {
        buzzerStartTime = millis();
      }
      break;
      
    case 4: // Critical - continuous alarm
      // Alternating tones
      if ((elapsed / 500) % 2 == 0) {
        tone(BUZZER_PIN, 2000);
      } else {
        tone(BUZZER_PIN, 1500);
      }
      break;
      
    default:
      noTone(BUZZER_PIN);
      break;
  }
}
