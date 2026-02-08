"""
ESP32-S3 Autonomous Meteo Station Demo
=======================================

Demonstration of the autonomous meteo station functionality
for ESP32-S3 with Deep Sleep, IR wake, and battery power.

This script demonstrates:
1. Hardware initialization
2. Sensor reading (AHT20 + BMP280)
3. Display output (ST7789)
4. Power management
5. Memory optimization

Author: ESP32-MeteoCore Project
"""

import time


def demo_sensors():
    """Demo sensor reading."""
    print("\n" + "=" * 50)
    print("SENSOR DEMO")
    print("=" * 50)
    
    try:
        from machine import I2C, Pin
        from src.core.constants import PhysicalConstants as PC
        from src.esp32.aht20 import AHT20
        from src.esp32.bmp280 import BMP280Sensor
        
        # Initialize I2C
        i2c = I2C(
            0,
            scl=Pin(PC.SENSOR_SCL),
            sda=Pin(PC.SENSOR_SDA),
            freq=PC.SENSOR_FREQ
        )
        
        print(f"I2C devices: {[hex(x) for x in i2c.scan()]}")
        
        # Initialize sensors
        aht20 = AHT20(i2c)
        bmp280 = BMP280Sensor(i2c)
        
        # Read data
        print("\nReading sensors...")
        aht_data = aht20.read()
        bmp_data = bmp280.read()
        
        print(f"\nAHT20:")
        print(f"  Temperature: {aht_data['temperature']:.2f}°C")
        print(f"  Humidity: {aht_data['humidity']:.1f}%")
        
        print(f"\nBMP280:")
        print(f"  Temperature: {bmp_data['temperature']:.2f}°C")
        print(f"  Pressure: {bmp_data['pressure']:.1f} hPa")
        
        # Calculate MSLP
        from src.meteo.barometric import adjust_pressure_to_sea_level_precise
        
        temp_avg = (aht_data['temperature'] + bmp_data['temperature']) / 2
        mslp = adjust_pressure_to_sea_level_precise(
            bmp_data['pressure'],
            temp_avg,
            aht_data['humidity'],
            elevation=PC.ELEVATION
        )
        
        print(f"\nMean Sea Level Pressure: {mslp:.1f} hPa")
        
    except Exception as e:
        print(f"Error in sensor demo: {e}")
        import sys
        sys.print_exception(e)


def demo_display():
    """Demo display functionality."""
    print("\n" + "=" * 50)
    print("DISPLAY DEMO")
    print("=" * 50)
    
    try:
        from src.esp32.st7789_display import MeteoDisplay
        from src.core.constants import PhysicalConstants as PC
        
        # Initialize display
        display = MeteoDisplay(
            width=PC.DISPLAY_WIDTH,
            height=PC.DISPLAY_HEIGHT
        )
        
        # Test data
        test_data = {
            'temperature': 22.5,
            'humidity': 65,
            'pressure': 1013.2,
            'forecast': 'Stable',
            'battery': 85
        }
        
        print("Displaying test data...")
        display.show_meteo_data(test_data)
        
        print("Display will stay on for 10 seconds...")
        time.sleep(10)
        
        # Turn off
        display.display_off()
        print("Display turned off")
        
    except Exception as e:
        print(f"Error in display demo: {e}")
        import sys
        sys.print_exception(e)


def demo_power():
    """Demo power management."""
    print("\n" + "=" * 50)
    print("POWER MANAGEMENT DEMO")
    print("=" * 50)
    
    try:
        from src.esp32.power_manager import PowerManager
        
        # Initialize power manager
        power = PowerManager()
        
        # Check wake reason
        print(f"Wake reason: {power.wake_reason}")
        
        # Read battery
        voltage = power.read_battery_voltage()
        percent = power.get_battery_percent()
        
        print(f"\nBattery:")
        print(f"  Voltage: {voltage:.2f}V")
        print(f"  Level: {percent:.0f}%")
        
    except Exception as e:
        print(f"Error in power demo: {e}")
        import sys
        sys.print_exception(e)


def demo_memory():
    """Demo memory optimization."""
    print("\n" + "=" * 50)
    print("MEMORY OPTIMIZATION DEMO")
    print("=" * 50)
    
    try:
        from src.esp32.memory_optimizer import (
            optimize_memory,
            get_memory_stats,
            CircularBuffer
        )
        
        # Optimize memory
        optimize_memory()
        
        # Show stats
        stats = get_memory_stats()
        print(f"\nMemory stats:")
        print(f"  Free: {stats['free']} bytes")
        print(f"  Allocated: {stats['allocated']} bytes")
        print(f"  Total: {stats['total']} bytes")
        
        # Test circular buffer
        print("\nCircular buffer test:")
        buffer = CircularBuffer(12)
        
        # Simulate pressure readings
        pressures = [1013.2, 1012.8, 1012.5, 1012.0, 1011.5, 1011.0]
        for p in pressures:
            buffer.append(p)
        
        print(f"  Values: {buffer.get_all()}")
        print(f"  Delta: {buffer.calculate_delta():.1f} hPa")
        
    except Exception as e:
        print(f"Error in memory demo: {e}")
        import sys
        sys.print_exception(e)


def demo_fishing():
    """Demo fishing forecast."""
    print("\n" + "=" * 50)
    print("FISHING FORECAST DEMO")
    print("=" * 50)
    
    try:
        from src.fishing.pressure_analyzer import analyze_pressure_trend
        
        # Test scenarios
        scenarios = [
            ([1013.2, 1012.8, 1012.5, 1012.0, 1011.5, 1011.0, 1010.5], "Falling"),
            ([1010.0, 1010.5, 1011.0, 1011.5, 1012.0, 1012.5, 1013.0], "Rising"),
            ([1013.0, 1013.1, 1013.0, 1012.9, 1013.1, 1013.0, 1013.0], "Stable"),
        ]
        
        for pressures, label in scenarios:
            result = analyze_pressure_trend(pressures)
            print(f"\n{label} pressure:")
            print(f"  Delta: {result['delta_6h']} hPa/6h")
            print(f"  Trend: {result['trend']}")
            print(f"  Status: {result['fishing_status']}")
            print(f"  Recommendation: {result['recommendation']}")
        
    except Exception as e:
        print(f"Error in fishing demo: {e}")
        import sys
        sys.print_exception(e)


def main():
    """Run all demos."""
    print("\n" * 2)
    print("#" * 50)
    print("# ESP32-S3 AUTONOMOUS METEO STATION DEMO")
    print("#" * 50)
    
    # Run demos
    demo_sensors()
    demo_display()
    demo_power()
    demo_memory()
    demo_fishing()
    
    print("\n" + "=" * 50)
    print("DEMO COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()
