"""
WiFi Manager for ESP32
======================

WiFi connection management for MicroPython on ESP32.
"""


def log(message, level="INFO"):
    """Simple logging function."""
    try:
        print(f"[{level}] WIFI: {message}")
    except:
        pass


class WiFiManager:
    """
    WiFi connection manager for ESP32.
    Handles connection, reconnection, and status monitoring.
    """
    
    def __init__(self):
        """Initialize WiFi manager."""
        self.wlan = None
        self.ssid = None
        self.connected = False
        
        try:
            import network
            self.wlan = network.WLAN(network.STA_IF)
            log("WiFi manager initialized")
        except ImportError:
            log("network module not available (not on MicroPython?)", "WARNING")
        except Exception as e:
            log(f"Failed to initialize WiFi manager: {e}", "ERROR")
    
    def connect(self, ssid, password, timeout=10):
        """
        Connect to WiFi network.
        
        Args:
            ssid: WiFi network name
            password: WiFi password
            timeout: Connection timeout in seconds (default 10)
            
        Returns:
            True if connected, False otherwise
        """
        if self.wlan is None:
            log("WiFi not available", "ERROR")
            return False
        
        self.ssid = ssid
        
        try:
            # Activate station interface
            self.wlan.active(True)
            
            # Check if already connected
            if self.wlan.isconnected():
                log(f"Already connected to {ssid}")
                self.connected = True
                return True
            
            log(f"Connecting to {ssid}...")
            self.wlan.connect(ssid, password)
            
            # Wait for connection
            import time
            start_time = time.time()
            while not self.wlan.isconnected():
                if time.time() - start_time > timeout:
                    log(f"Connection timeout after {timeout}s", "ERROR")
                    self.connected = False
                    return False
                time.sleep(0.5)
            
            # Connection successful
            config = self.wlan.ifconfig()
            log(f"Connected! IP: {config[0]}")
            self.connected = True
            return True
            
        except Exception as e:
            log(f"Connection error: {e}", "ERROR")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from WiFi network."""
        if self.wlan is None:
            return
        
        try:
            if self.wlan.isconnected():
                self.wlan.disconnect()
                log("Disconnected from WiFi")
            self.connected = False
        except Exception as e:
            log(f"Error disconnecting: {e}", "ERROR")
    
    def is_connected(self):
        """
        Check if connected to WiFi.
        
        Returns:
            True if connected, False otherwise
        """
        if self.wlan is None:
            return False
        
        try:
            connected = self.wlan.isconnected()
            self.connected = connected
            return connected
        except:
            self.connected = False
            return False
    
    def get_ip(self):
        """
        Get current IP address.
        
        Returns:
            IP address as string, or None if not connected
        """
        if self.wlan is None or not self.wlan.isconnected():
            return None
        
        try:
            config = self.wlan.ifconfig()
            return config[0]
        except:
            return None
    
    def get_rssi(self):
        """
        Get WiFi signal strength (RSSI).
        
        Returns:
            RSSI in dBm, or None if not connected
        """
        if self.wlan is None or not self.wlan.isconnected():
            return None
        
        try:
            # Note: This may not work on all ESP32 firmware versions
            import network
            networks = self.wlan.scan()
            for net in networks:
                if net[0].decode('utf-8') == self.ssid:
                    return net[3]  # RSSI
            return None
        except:
            return None
    
    def scan_networks(self):
        """
        Scan for available WiFi networks.
        
        Returns:
            List of tuples: (ssid, bssid, channel, rssi, authmode, hidden)
        """
        if self.wlan is None:
            return []
        
        try:
            self.wlan.active(True)
            networks = self.wlan.scan()
            
            # Format output
            result = []
            for net in networks:
                ssid = net[0].decode('utf-8')
                rssi = net[3]
                result.append({
                    'ssid': ssid,
                    'rssi': rssi,
                    'channel': net[2],
                    'hidden': net[5]
                })
            
            log(f"Found {len(result)} networks")
            return result
            
        except Exception as e:
            log(f"Error scanning networks: {e}", "ERROR")
            return []
    
    def reconnect(self, password, timeout=10):
        """
        Reconnect to last used network.
        
        Args:
            password: WiFi password
            timeout: Connection timeout in seconds
            
        Returns:
            True if reconnected, False otherwise
        """
        if self.ssid is None:
            log("No SSID stored for reconnection", "ERROR")
            return False
        
        return self.connect(self.ssid, password, timeout)
    
    def auto_reconnect(self, ssid, password, interval=30):
        """
        Keep WiFi connection alive with auto-reconnect.
        Call this periodically in your main loop.
        
        Args:
            ssid: WiFi network name
            password: WiFi password
            interval: Check interval in seconds (default 30)
        """
        if not self.is_connected():
            log("Connection lost, reconnecting...", "WARNING")
            self.connect(ssid, password)
