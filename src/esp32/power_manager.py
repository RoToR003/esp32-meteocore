"""
Power Management for ESP32-S3 Meteo Station
============================================

Handles:
- Deep Sleep transitions
- Wake reason detection
- WiFi burst mode
- Battery monitoring

Author: ESP32-MeteoCore Project
"""


def log(message, level="INFO"):
    """Simple logging function for both CPython and MicroPython."""
    try:
        print(f"[{level}] POWER: {message}")
    except:
        pass


class PowerManager:
    """
    Manages power states and wake logic.
    """
    
    def __init__(self):
        try:
            import machine
            from machine import Pin, ADC
            import esp32
            from ..core.constants import PhysicalConstants as PC
            
            # Battery ADC
            self.bat_adc = ADC(Pin(PC.BAT_ADC_PIN))
            self.bat_adc.atten(ADC.ATTN_11DB)  # 0-3.3V range
            
            # IR pin for wake
            self.ir_pin = Pin(PC.IR_PIN, Pin.IN, Pin.PULL_UP)
            
            # Wake reason
            self.wake_reason = self._detect_wake_reason()
            
            log(f"PowerManager initialized, wake reason: {self.wake_reason}")
        except Exception as e:
            log(f"Error initializing PowerManager: {e}", "ERROR")
            self.wake_reason = 0  # Default to cold boot
    
    def _detect_wake_reason(self):
        """
        Detect why ESP32 woke up.
        
        Returns:
            0: Cold boot (power-on reset)
            1: Timer wake (hourly)
            2: IR remote wake
        """
        try:
            import machine
            import esp32
            
            reset_cause = machine.reset_cause()
            
            if reset_cause == machine.PWRON_RESET:
                log("Wake reason: Cold boot (power-on)")
                return 0  # Cold boot
            
            elif reset_cause == machine.DEEPSLEEP_RESET:
                # Check wake cause
                wake_cause = esp32.wake_reason()
                
                if wake_cause == esp32.WAKEUP_EXT0:
                    log("Wake reason: IR remote (EXT0)")
                    return 2  # IR remote
                else:
                    log("Wake reason: Timer wake")
                    return 1  # Timer
            
            log("Wake reason: Other (default to cold boot)")
            return 0  # Default
        except Exception as e:
            log(f"Error detecting wake reason: {e}", "ERROR")
            return 0
    
    def read_battery_voltage(self):
        """
        Read battery voltage through ADC.
        
        Returns:
            Voltage in volts (considering divider)
        """
        try:
            from ..core.constants import PhysicalConstants as PC
            
            # Read ADC (average of 10 samples)
            samples = [self.bat_adc.read() for _ in range(10)]
            avg = sum(samples) / len(samples)
            
            # Convert to voltage (ADC: 0-4095 = 0-3.3V)
            voltage = (avg / 4095.0) * 3.3 * PC.BAT_VOLTAGE_DIVIDER
            
            return voltage
        except Exception as e:
            log(f"Error reading battery voltage: {e}", "ERROR")
            return 3.7  # Default safe value
    
    def get_battery_percent(self):
        """
        Calculate battery percentage.
        
        Returns:
            Battery level (0-100%)
        """
        try:
            from ..core.constants import PhysicalConstants as PC
            
            voltage = self.read_battery_voltage()
            
            # Linear interpolation
            percent = ((voltage - PC.BAT_EMPTY) / (PC.BAT_FULL - PC.BAT_EMPTY)) * 100.0
            
            return max(0, min(100, percent))
        except Exception as e:
            log(f"Error calculating battery percent: {e}", "ERROR")
            return 50.0  # Default safe value
    
    def enter_deep_sleep(self, duration_sec, enable_ir_wake=True):
        """
        Enter deep sleep mode.
        
        Args:
            duration_sec: Sleep duration (seconds)
            enable_ir_wake: Enable IR remote wake
        """
        try:
            import machine
            import esp32
            
            log(f"Entering deep sleep for {duration_sec} sec...")
            
            # Configure timer wake
            esp32.wake_on_timer(duration_sec * 1000)  # milliseconds
            
            # Configure IR wake (EXT0)
            if enable_ir_wake:
                esp32.wake_on_ext0(self.ir_pin, esp32.WAKEUP_ALL_LOW)
            
            # Deep sleep
            machine.deepsleep()
        except Exception as e:
            log(f"Error entering deep sleep: {e}", "ERROR")
    
    def wifi_burst(self, callback, timeout=10):
        """
        WiFi burst mode: Connect, execute callback, disconnect.
        
        Args:
            callback: Function to execute while WiFi is on
            timeout: WiFi connection timeout (seconds)
        
        Returns:
            Result from callback
        """
        try:
            import network
            import time
            
            sta_if = network.WLAN(network.STA_IF)
            sta_if.active(True)
            
            # Connect (use saved credentials)
            log("WiFi connecting...")
            start = time.time()
            
            while not sta_if.isconnected():
                if time.time() - start > timeout:
                    log("WiFi timeout!")
                    sta_if.active(False)
                    return None
                time.sleep(0.5)
            
            log(f"WiFi connected: {sta_if.ifconfig()[0]}")
            
            # Execute callback
            try:
                result = callback()
            except Exception as e:
                log(f"WiFi callback error: {e}", "ERROR")
                result = None
            
            # Disconnect
            sta_if.disconnect()
            sta_if.active(False)
            log("WiFi disconnected")
            
            return result
        except Exception as e:
            log(f"WiFi burst error: {e}", "ERROR")
            return None
