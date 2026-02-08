# Wokwi Simulation Guide

## Overview

This guide explains how to run the ESP32-MeteoCore project in Wokwi simulator for testing and development.

## What is Wokwi?

Wokwi is an online IoT and embedded systems simulator that supports ESP32 microcontrollers. It allows you to test your firmware without physical hardware.

**Website:** https://wokwi.com/

## Hardware Substitutions

Since Wokwi doesn't support all components, we use compatible alternatives:

| Real Hardware | Wokwi Simulation | Notes |
|---------------|------------------|-------|
| ST7789 Display | ILI9341 Display | Both are SPI TFT displays with similar interfaces |
| AHT20 Sensor | DHT22 Sensor | Both provide temperature + humidity |
| BMP280 | BMP280 | Direct support ✓ |
| DS18B20 | DS18B20 | Direct support ✓ |
| HX1838 IR Receiver | IR Receiver | Direct support ✓ |

## Configuration Files

### `diagram.json`

Defines the hardware connections in Wokwi. Key features:

- **ESP32-S3-DevKitC-1** as the main board
- **ILI9341** 240×320 display (replaces ST7789)
- **BMP280** for pressure measurement
- **DHT22** simulating AHT20 (humidity + temperature)
- **DS18B20** for water temperature
- **IR Receiver** for wake-up

### `wokwi.toml`

Configuration file for Wokwi environment:

```toml
[wokwi]
version = 1
firmware = "main.py"

[wokwi.serial]
baudRate = 115200
```

## How It Works

### Automatic Detection

The code automatically detects whether it's running in Wokwi or on real hardware:

```python
from src.core.wokwi_detect import get_environment

env = get_environment()
if env['platform'] == 'wokwi':
    # Use simulation-compatible drivers
else:
    # Use real hardware drivers
```

### Display Driver Selection

The display wrapper automatically chooses the correct driver:

1. Try ST7789 (real hardware)
2. Try ILI9341 (Wokwi)
3. Fallback to Mock display (testing)

```python
from src.esp32.display_wrapper import get_display

display = get_display(width=240, height=320)
# Returns appropriate driver automatically
```

### Sensor Fallbacks

**AHT20 → DHT22:**

```python
from src.esp32.aht20 import AHT20

# Automatically uses DHT22 if AHT20 not found
aht20 = AHT20(i2c=i2c, pin=dht_pin)
```

## Running in Wokwi

### Step 1: Prepare Your Project

Ensure you have these files:
- `main.py` - Main firmware
- `diagram.json` - Hardware configuration
- `wokwi.toml` - Wokwi settings
- All `src/` modules

### Step 2: Upload to Wokwi

1. Go to https://wokwi.com/
2. Create a new project or open existing
3. Select "ESP32-S3" board
4. Upload your files or link to GitHub repo

### Step 3: Start Simulation

1. Click the green "▶ Start Simulation" button
2. Watch the serial monitor for output
3. Interact with sensors/IR remote

### Step 4: Monitor Output

The serial monitor shows:
```
==================================================
ESP32-S3 METEO STATION - INIT
==================================================
[INFO] WOKWI_DETECT: Platform: wokwi
[INFO] AHT20: DHT22 initialized (Wokwi simulation mode)
[INFO] DISPLAY_WRAPPER: Found ili9341 library, using ILI9341 display (Wokwi)
```

## Testing Scenarios

### 1. Temperature Reading

Change sensor values in `diagram.json`:

```json
{
  "type": "wokwi-dht22",
  "id": "aht20_sim",
  "attrs": {
    "temperature": "25",  // Change this
    "humidity": "70"      // And this
  }
}
```

### 2. Pressure Changes

Modify BMP280 attributes:

```json
{
  "type": "board-bmp280",
  "id": "bmp280",
  "attrs": {
    "temperature": "22.5",
    "pressure": "1015.0"  // Adjust for testing
  }
}
```

### 3. IR Wake-Up

Click the IR receiver in the simulator to trigger wake events.

### 4. Display Screens

Use IR remote to navigate between screens:
- Screen 0: Main (Temperature, humidity, pressure)
- Screen 1: Details (Extended data)
- Screen 2: Pressure Graph (24h trend)
- Screen 3: Fishing Forecast

## Limitations

### What Works ✓

- ✓ All sensors read correctly
- ✓ Display shows data
- ✓ Serial output
- ✓ Basic MicroPython functions
- ✓ I2C communication
- ✓ SPI display

### What Doesn't Work ✗

- ✗ Deep sleep (Wokwi doesn't support it)
- ✗ WiFi (not yet supported in Wokwi)
- ✗ NVS storage (limited support)
- ✗ Real-time clock
- ✗ Power management

### Workarounds

**Deep Sleep:**
```python
# In Wokwi, sleep is replaced with delay
if env['platform'] == 'wokwi':
    time.sleep(1)  # Just wait
else:
    machine.deepsleep(3600000)  # Real sleep
```

**WiFi:**
```python
# Skip WiFi in Wokwi
if env['platform'] != 'wokwi':
    wifi_connect()
```

## Debugging Tips

### 1. Check Serial Output

All logs go to serial monitor:
```python
print(f"[INFO] Current temperature: {temp}°C")
```

### 2. Use Mock Display

If display issues occur, mock display logs all operations:
```
[INFO] DISPLAY_WRAPPER: Mock display initialized
[DEBUG] DISPLAY: TEXT: 'Temp: 22.5C' at (20, 40)
```

### 3. Inspect I2C Devices

Check detected devices:
```python
devices = i2c.scan()
print(f"I2C devices: {[hex(x) for x in devices]}")
```

### 4. Validate Sensor Types

Check which sensor type is active:
```python
print(f"AHT20 sensor type: {aht20.sensor_type}")
# Output: "AHT20" or "DHT22" or "MOCK"
```

## Performance Notes

### Simulation Speed

Wokwi runs slower than real hardware:
- Real ESP32-S3: 240 MHz
- Wokwi: Variable (depends on browser/computer)

### Memory Usage

Wokwi has the same RAM/Flash as real hardware:
- RAM: 512 KB (N16R8 variant)
- Flash: 16 MB

## GitHub Integration

### Link Wokwi to GitHub

1. In Wokwi project settings
2. Connect to GitHub repository
3. Select branch (e.g., `copilot/improve-st7789-display`)
4. Auto-sync files

### Share Simulation

Share link format:
```
https://wokwi.com/projects/YOUR_PROJECT_ID
```

## Troubleshooting

### Display Not Working

**Problem:** Blank display or errors

**Solutions:**
1. Check `diagram.json` connections
2. Verify ILI9341 library is available
3. Check SPI pins (SCK=14, MOSI=13, DC=11, RST=12)

### Sensor Not Found

**Problem:** "Sensor not found" errors

**Solutions:**
1. Verify I2C connections (SDA=4, SCL=5)
2. Check sensor I2C address (0x38 for AHT20/DHT22, 0x76 for BMP280)
3. Try DHT22 fallback mode

### Code Not Running

**Problem:** Simulation crashes or freezes

**Solutions:**
1. Check for syntax errors
2. Reduce serial output (flooding can cause issues)
3. Simplify graphics (too many pixels slow down simulation)
4. Disable deep sleep calls

## Advanced Features

### Custom Scenarios

Create test scenarios in `diagram.json`:

**Scenario 1: Hot Day**
```json
"aht20_sim": {
  "temperature": "35",
  "humidity": "30"
},
"bmp280": {
  "pressure": "1005"
}
```

**Scenario 2: Storm Approaching**
```json
"aht20_sim": {
  "temperature": "18",
  "humidity": "90"
},
"bmp280": {
  "pressure": "995"  // Falling pressure
}
```

### Automated Testing

Use Wokwi CLI for automated tests:

```bash
wokwi-cli test --project diagram.json --timeout 60
```

## Next Steps

After successful Wokwi testing:

1. ✓ Code works in simulation
2. → Flash to real ESP32-S3 hardware
3. → Test with real sensors
4. → Validate battery life
5. → Deploy to field

## Resources

- Wokwi Documentation: https://docs.wokwi.com/
- ESP32-S3 Guide: https://docs.wokwi.com/parts/board-esp32-s3-devkitc-1
- ILI9341 Display: https://docs.wokwi.com/parts/wokwi-ili9341
- Wokwi Discord: https://wokwi.com/discord

## Support

Issues with Wokwi simulation? Check:

1. GitHub Issues: Report bugs specific to simulation
2. Wokwi Forum: Ask about simulator behavior
3. Project README: General setup instructions
