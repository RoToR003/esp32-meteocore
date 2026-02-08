"""
MQTT Client for ESP32
=====================

MQTT client for publishing weather and fish forecasts.
Compatible with MicroPython on ESP32.
"""


def log(message, level="INFO"):
    """Simple logging function."""
    try:
        print(f"[{level}] MQTT: {message}")
    except:
        pass


class MQTTClient:
    """
    MQTT client for ESP32.
    Publishes weather forecasts and fish activity data to MQTT broker.
    """
    
    def __init__(self, broker, port=1883, client_id=None):
        """
        Initialize MQTT client.
        
        Args:
            broker: MQTT broker hostname or IP
            port: MQTT broker port (default 1883)
            client_id: Unique client ID (auto-generated if None)
        """
        self.broker = broker
        self.port = port
        self.client = None
        self.connected = False
        
        # Generate client ID if not provided
        if client_id is None:
            try:
                import machine
                import ubinascii
                client_id = b"esp32_" + ubinascii.hexlify(machine.unique_id())
                client_id = client_id.decode('utf-8')
            except:
                client_id = "esp32_meteocore"
        
        self.client_id = client_id
        
        try:
            # Try to import MQTT library for MicroPython
            from umqtt.simple import MQTTClient as UMQTTClient
            self.client = UMQTTClient(self.client_id, self.broker, port=self.port)
            log(f"MQTT client initialized: {client_id}")
        except ImportError:
            log("umqtt.simple not found. Install micropython-umqtt.simple", "WARNING")
        except Exception as e:
            log(f"Failed to initialize MQTT client: {e}", "ERROR")
    
    def connect(self, username=None, password=None):
        """
        Connect to MQTT broker.
        
        Args:
            username: MQTT username (optional)
            password: MQTT password (optional)
            
        Returns:
            True if connected, False otherwise
        """
        if self.client is None:
            log("MQTT client not initialized", "ERROR")
            return False
        
        try:
            # Set credentials if provided
            if username and password:
                self.client.set_auth(username, password)
            
            log(f"Connecting to MQTT broker {self.broker}:{self.port}...")
            self.client.connect()
            log("Connected to MQTT broker")
            self.connected = True
            return True
            
        except Exception as e:
            log(f"Connection error: {e}", "ERROR")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        if self.client is None:
            return
        
        try:
            if self.connected:
                self.client.disconnect()
                log("Disconnected from MQTT broker")
            self.connected = False
        except Exception as e:
            log(f"Error disconnecting: {e}", "ERROR")
    
    def publish(self, topic, message, retain=False, qos=0):
        """
        Publish message to MQTT topic.
        
        Args:
            topic: MQTT topic
            message: Message payload (string or bytes)
            retain: Retain flag (default False)
            qos: Quality of Service (0, 1, or 2)
            
        Returns:
            True if published, False otherwise
        """
        if self.client is None or not self.connected:
            log("Not connected to MQTT broker", "ERROR")
            return False
        
        try:
            # Convert message to bytes if needed
            if isinstance(message, str):
                message = message.encode('utf-8')
            
            self.client.publish(topic, message, retain=retain, qos=qos)
            log(f"Published to {topic}: {len(message)} bytes")
            return True
            
        except Exception as e:
            log(f"Publish error: {e}", "ERROR")
            return False
    
    def publish_json(self, topic, data, retain=False):
        """
        Publish data as JSON to MQTT topic.
        
        Args:
            topic: MQTT topic
            data: Dictionary to publish as JSON
            retain: Retain flag (default False)
            
        Returns:
            True if published, False otherwise
        """
        try:
            # Try ujson (MicroPython) first, then fall back to json (CPython)
            try:
                import ujson as json
            except ImportError:
                import json
            
            message = json.dumps(data)
            return self.publish(topic, message, retain=retain)
            
        except Exception as e:
            log(f"JSON publish error: {e}", "ERROR")
            return False
    
    def publish_weather(self, weather_data, topic="meteo/weather"):
        """
        Publish weather forecast data.
        
        Args:
            weather_data: Dictionary with weather data
            topic: MQTT topic (default "meteo/weather")
            
        Returns:
            True if published, False otherwise
        """
        return self.publish_json(topic, weather_data, retain=True)
    
    def publish_fishing(self, fishing_data, topic="meteo/fishing"):
        """
        Publish fish activity forecast data.
        
        Args:
            fishing_data: Dictionary with KIAR and fish activity data
            topic: MQTT topic (default "meteo/fishing")
            
        Returns:
            True if published, False otherwise
        """
        return self.publish_json(topic, fishing_data, retain=True)
    
    def publish_sensor_data(self, sensor_data, topic="meteo/sensors"):
        """
        Publish raw sensor readings.
        
        Args:
            sensor_data: Dictionary with sensor readings
            topic: MQTT topic (default "meteo/sensors")
            
        Returns:
            True if published, False otherwise
        """
        return self.publish_json(topic, sensor_data, retain=False)
    
    def subscribe(self, topic, callback):
        """
        Subscribe to MQTT topic.
        
        Args:
            topic: MQTT topic to subscribe
            callback: Callback function(topic, msg)
            
        Returns:
            True if subscribed, False otherwise
        """
        if self.client is None or not self.connected:
            log("Not connected to MQTT broker", "ERROR")
            return False
        
        try:
            self.client.set_callback(callback)
            self.client.subscribe(topic)
            log(f"Subscribed to {topic}")
            return True
        except Exception as e:
            log(f"Subscribe error: {e}", "ERROR")
            return False
    
    def check_msg(self):
        """
        Check for new messages (non-blocking).
        Call this periodically in your main loop.
        
        Returns:
            True if message received, False otherwise
        """
        if self.client is None or not self.connected:
            return False
        
        try:
            self.client.check_msg()
            return True
        except:
            return False
    
    def wait_msg(self):
        """
        Wait for new message (blocking).
        """
        if self.client is None or not self.connected:
            return
        
        try:
            self.client.wait_msg()
        except Exception as e:
            log(f"Error waiting for message: {e}", "ERROR")
