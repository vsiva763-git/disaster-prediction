# IoT Alert System - Hardware Setup Guide

## Overview

This IoT alert system sends tsunami warnings to physical devices (LCD display + buzzer) using ESP8266 WiFi modules and Arduino UNO.

## Hardware Components

| Component | Quantity | Purpose |
|-----------|----------|---------|
| Arduino UNO | 1 | Main controller for LCD and buzzer |
| ESP8266 (NodeMCU/Wemos D1) | 1 | WiFi connectivity |
| LCD 16x2 (without I2C) | 1 | Display alerts |
| Active Buzzer | 1 | Audio alerts |
| 10kΩ Potentiometer | 1 | LCD contrast adjustment |
| 1kΩ Resistor | 1 | Voltage divider |
| 2kΩ Resistor | 1 | Voltage divider |
| Breadboard & Jumper Wires | - | Connections |

## Wiring Diagram

### LCD to Arduino UNO (4-bit mode)

```
LCD Pin    Arduino Pin    Description
-------    -----------    -----------
VSS        GND            Ground
VDD        5V             Power
V0         Potentiometer  Contrast (middle pin)
RS         12             Register Select
RW         GND            Read/Write (Ground for write)
EN         11             Enable
D4         5              Data bit 4
D5         4              Data bit 5
D6         3              Data bit 6
D7         2              Data bit 7
A          5V (220Ω)      Backlight Anode
K          GND            Backlight Cathode
```

### Buzzer to Arduino UNO

```
Buzzer    Arduino
------    -------
+         Pin 8
-         GND
```

### ESP8266 to Arduino UNO (Serial Communication)

```
ESP8266    Arduino         Notes
-------    -------         -----
TX         Pin 6 (RX)      Direct connection
RX         Pin 7 (TX)      Through voltage divider!
GND        GND             Common ground
3.3V       3.3V            Or use external regulator
```

### Voltage Divider for ESP8266 RX

```
Arduino TX (5V) --[1kΩ]--+--[2kΩ]-- GND
                         |
                    ESP8266 RX (3.3V)
```

This converts 5V logic from Arduino to 3.3V for ESP8266.

## Circuit Diagram

```
                              +5V
                               |
                         [10kΩ POT]
                          |    |
                         GND  LCD-V0
                               
    Arduino UNO                          LCD 16x2
    +-----------+                      +--------+
    |        12 |-------------------->| RS     |
    |        11 |-------------------->| EN     |
    |         5 |-------------------->| D4     |
    |         4 |-------------------->| D5     |
    |         3 |-------------------->| D6     |
    |         2 |-------------------->| D7     |
    |           |                     +--------+
    |         8 |---[ BUZZER ]---GND
    |           |
    |         6 |<--------------------| TX  ESP8266 |
    |         7 |---[1kΩ]---+        | RX         |
    |           |           |        |            |
    |       GND |---[2kΩ]---+--------| GND        |
    |      3.3V |--------------------| 3.3V       |
    +-----------+                    +------------+
```

## Software Setup

### 1. Flash ESP8266

1. Open `iot/esp8266_wifi/esp8266_wifi.ino` in Arduino IDE
2. Install ESP8266 board package (Arduino IDE → Preferences → Additional Boards Manager URLs: `http://arduino.esp8266.com/stable/package_esp8266com_index.json`)
3. Install required libraries:
   - ESP8266WiFi
   - ESP8266WebServer
   - ArduinoJson (v6)
4. Edit WiFi credentials:
   ```cpp
   const char* WIFI_SSID = "YOUR_WIFI_SSID";
   const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
   ```
5. Select board: NodeMCU or Wemos D1 Mini
6. Upload code

### 2. Flash Arduino UNO

1. Open `iot/arduino_uno_lcd_buzzer/arduino_uno_lcd_buzzer.ino`
2. Install LiquidCrystal library (usually pre-installed)
3. Select board: Arduino UNO
4. Upload code

### 3. Find ESP8266 IP Address

After flashing, the ESP8266 will:
- Connect to your WiFi network
- Print its IP address to Serial Monitor (115200 baud)
- Example: `IP address: 192.168.1.105`

If WiFi connection fails, it starts in AP mode:
- Connect to WiFi: `TsunamiAlert_Setup`
- Password: `tsunami123`
- Visit: `http://192.168.4.1`

### 4. Register Device in Dashboard

1. Go to your tsunami warning system: `http://your-server/iot`
2. Enter device name and ESP8266 IP address
3. Click "Add Device"
4. Test the connection with "Test" button

## API Endpoints (ESP8266)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Device info page |
| `/health` | GET | Health check |
| `/alert` | POST | Send alert `{level, message}` |
| `/clear` | POST/GET | Clear current alert |
| `/test` | POST/GET | Test LCD and buzzer |
| `/status` | GET | Device status |

### Example: Send Alert via curl

```bash
curl -X POST http://192.168.1.105/alert \
  -H "Content-Type: application/json" \
  -d '{"level": 3, "message": "M7.2 Andaman Sea"}'
```

### Alert Levels

| Level | Name | Buzzer Pattern |
|-------|------|----------------|
| 0 | NONE | Silent |
| 1 | WATCH | Single beep every 5s |
| 2 | ADVISORY | Double beep every 3s |
| 3 | WARNING | Rapid beeping |
| 4 | CRITICAL | Continuous alternating alarm |

## Troubleshooting

### LCD Not Displaying

1. Check contrast potentiometer - turn it
2. Verify all LCD connections
3. Check 5V power supply

### Buzzer Not Working

1. Check polarity (+ to Pin 8)
2. Try different buzzer (active vs passive)
3. Test pin with LED

### ESP8266 Not Connecting

1. Check WiFi credentials
2. Ensure 2.4GHz network (not 5GHz)
3. Check Serial Monitor for errors
4. Verify 3.3V power (not 5V!)

### Arduino Not Receiving Commands

1. Check SoftwareSerial connections (pins 6, 7)
2. Verify voltage divider for ESP8266 RX
3. Check baud rate (9600)
4. Open Serial Monitor on Arduino to debug

## Power Supply

For standalone operation:
- Arduino UNO: USB or 7-12V DC adapter
- ESP8266: Powered from Arduino 3.3V or separate 3.3V regulator
- Total current: ~200-300mA

## Multiple Devices

You can set up multiple alert stations:
1. Each station needs its own ESP8266 + Arduino + LCD + Buzzer
2. Register each device in the dashboard with unique IP
3. Alerts will be sent to all registered devices simultaneously

## Integration with Prediction System

The IoT alert system automatically integrates with the tsunami prediction:
1. Earthquake detected → AI model predicts risk
2. If risk > 30%: System triggers IoT alerts
3. Alert level based on probability:
   - 30-50%: WATCH
   - 50-75%: ADVISORY
   - 75-90%: WARNING
   - >90%: CRITICAL
