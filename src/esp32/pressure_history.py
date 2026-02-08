"""
Pressure History - Circular Buffer for 24h Tracking
===================================================

Stores atmospheric pressure readings over 24 hours.
Calculates trends and persists to NVS for deep sleep survival.

Features:
- Circular buffer (24 entries = 1 per hour)
- Trend calculation (hPa per 3 hours)
- NVS persistence (survives deep sleep)
- Memory efficient

Author: ESP32-MeteoCore Project
"""

import time


def log(message, level="INFO"):
    """Simple logging function."""
    try:
        print(f"[{level}] PRESSURE_HISTORY: {message}")
    except:
        pass


class PressureHistory:
    """
    Circular buffer for atmospheric pressure history.
    
    Stores up to 24 hours of pressure readings (1 per hour).
    Calculates pressure trends for weather forecasting.
    """
    
    def __init__(self, max_size=24):
        """
        Initialize pressure history buffer.
        
        Args:
            max_size: Maximum number of entries (default 24 for 24 hours)
        """
        self.buffer = []
        self.max_size = max_size
        log(f"Initialized with max_size={max_size}")
    
    def add(self, pressure, timestamp=None):
        """
        Add a new pressure reading.
        
        Args:
            pressure: Pressure in hPa (float)
            timestamp: Unix timestamp (default: current time)
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Add to buffer
        self.buffer.append((pressure, timestamp))
        
        # Remove oldest if buffer is full
        if len(self.buffer) > self.max_size:
            removed = self.buffer.pop(0)
            log(f"Buffer full, removed oldest: {removed[0]:.1f} hPa", "DEBUG")
        
        log(f"Added: {pressure:.1f} hPa at {timestamp}")
    
    def get_trend(self, hours=3):
        """
        Calculate pressure trend over specified hours.
        
        Args:
            hours: Number of hours to look back (default 3)
        
        Returns:
            float: Pressure change in hPa (positive = rising, negative = falling)
                   Returns 0 if insufficient data
        """
        if len(self.buffer) < 2:
            return 0.0
        
        # Get latest pressure
        latest_pressure, latest_time = self.buffer[-1]
        
        # Find pressure from 'hours' ago
        target_time = latest_time - (hours * 3600)
        
        # Find closest entry to target time
        closest_entry = None
        min_time_diff = float('inf')
        
        for pressure, timestamp in self.buffer:
            time_diff = abs(timestamp - target_time)
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_entry = (pressure, timestamp)
        
        if closest_entry is None:
            return 0.0
        
        # Calculate trend
        old_pressure = closest_entry[0]
        trend = latest_pressure - old_pressure
        
        log(f"Trend ({hours}h): {trend:+.2f} hPa/{hours}h")
        return round(trend, 2)
    
    def get_data(self):
        """
        Get all pressure history data.
        
        Returns:
            list: List of (pressure, timestamp) tuples
        """
        return self.buffer.copy()
    
    def get_pressures(self):
        """
        Get just pressure values (for graphing).
        
        Returns:
            list: List of pressure values in hPa
        """
        return [p for p, t in self.buffer]
    
    def get_min_max(self):
        """
        Get minimum and maximum pressure in history.
        
        Returns:
            tuple: (min_pressure, max_pressure) or (None, None) if empty
        """
        if not self.buffer:
            return None, None
        
        pressures = [p for p, t in self.buffer]
        return min(pressures), max(pressures)
    
    def save_to_nvs(self):
        """
        Save pressure history to NVS (Non-Volatile Storage).
        Survives deep sleep and power cycles.
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Try to import esp32 NVS
            try:
                import esp32
                nvs = esp32.NVS("meteocore")
            except ImportError:
                log("NVS not available (not on ESP32)", "WARNING")
                return False
            
            # Serialize buffer to bytes
            # Format: count (2 bytes) + entries (each 8 bytes: 4 for pressure, 4 for timestamp)
            if not self.buffer:
                log("Buffer empty, nothing to save", "DEBUG")
                return True
            
            # Limit to last 24 entries to fit in NVS
            entries_to_save = self.buffer[-24:]
            
            # Convert to compact format
            data = bytearray()
            data.append(len(entries_to_save) & 0xFF)
            data.append((len(entries_to_save) >> 8) & 0xFF)
            
            for pressure, timestamp in entries_to_save:
                # Pack pressure as integer (hPa * 10 to keep 1 decimal)
                pressure_int = int(pressure * 10)
                data.append(pressure_int & 0xFF)
                data.append((pressure_int >> 8) & 0xFF)
                data.append((pressure_int >> 16) & 0xFF)
                data.append((pressure_int >> 24) & 0xFF)
                
                # Pack timestamp as integer
                timestamp_int = int(timestamp)
                data.append(timestamp_int & 0xFF)
                data.append((timestamp_int >> 8) & 0xFF)
                data.append((timestamp_int >> 16) & 0xFF)
                data.append((timestamp_int >> 24) & 0xFF)
            
            # Write to NVS
            nvs.set_blob("press_hist", bytes(data))
            nvs.commit()
            
            log(f"Saved {len(entries_to_save)} entries to NVS")
            return True
            
        except Exception as e:
            log(f"Error saving to NVS: {e}", "ERROR")
            return False
    
    def load_from_nvs(self):
        """
        Load pressure history from NVS.
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            # Try to import esp32 NVS
            try:
                import esp32
                nvs = esp32.NVS("meteocore")
            except ImportError:
                log("NVS not available (not on ESP32)", "WARNING")
                return False
            
            # Read from NVS
            try:
                data = nvs.get_blob("press_hist")
            except OSError:
                log("No saved history in NVS", "INFO")
                return False
            
            if not data or len(data) < 2:
                log("Invalid or empty NVS data", "WARNING")
                return False
            
            # Parse data
            count = data[0] | (data[1] << 8)
            
            if count > self.max_size or count < 0:
                log(f"Invalid count in NVS: {count} (max: {self.max_size})", "WARNING")
                return False
            
            # Read entries
            self.buffer = []
            offset = 2
            
            for i in range(count):
                if offset + 8 > len(data):
                    log(f"Incomplete data at entry {i}", "WARNING")
                    break
                
                # Unpack pressure
                pressure_int = (data[offset] | 
                               (data[offset+1] << 8) |
                               (data[offset+2] << 16) |
                               (data[offset+3] << 24))
                pressure = pressure_int / 10.0
                
                # Unpack timestamp
                timestamp = (data[offset+4] |
                            (data[offset+5] << 8) |
                            (data[offset+6] << 16) |
                            (data[offset+7] << 24))
                
                self.buffer.append((pressure, timestamp))
                offset += 8
            
            log(f"Loaded {len(self.buffer)} entries from NVS")
            return True
            
        except Exception as e:
            log(f"Error loading from NVS: {e}", "ERROR")
            return False
    
    def clear(self):
        """Clear all history data."""
        self.buffer = []
        log("History cleared")
    
    def __len__(self):
        """Return number of entries in buffer."""
        return len(self.buffer)
    
    def __repr__(self):
        """String representation."""
        if not self.buffer:
            return f"PressureHistory(empty, max_size={self.max_size})"
        
        latest = self.buffer[-1][0]
        trend = self.get_trend()
        return f"PressureHistory({len(self.buffer)} entries, latest={latest:.1f} hPa, trend={trend:+.1f} hPa/3h)"
