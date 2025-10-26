import paho.mqtt.client as mqtt
import json
from datetime import datetime
from collections import deque
import threading

# Configuration
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "dht11/sensor"
MAX_DATA_POINTS = 100

# Global data storage
sensor_data = {
    "temperature": deque(maxlen=MAX_DATA_POINTS),
    "humidity": deque(maxlen=MAX_DATA_POINTS),
    "timestamps": deque(maxlen=MAX_DATA_POINTS),
}

data_lock = threading.Lock()


def on_connect(client, userdata, flags, rc):
    """Callback when client connects to the broker."""
    if rc == 0:
        print("✓ Connected to MQTT broker successfully")
        client.subscribe(MQTT_TOPIC)
        print(f"✓ Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"✗ Connection failed with code {rc}")


def on_disconnect(client, userdata, rc):
    """Callback when client disconnects from the broker."""
    if rc != 0:
        print(f"✗ Disconnected unexpectedly with code {rc}")
    else:
        print("✓ Disconnected from broker")


def on_message(client, userdata, msg):
    """Callback when a message is received."""
    try:
        payload = json.loads(msg.payload.decode())
        
        with data_lock:
            sensor_data["temperature"].append(payload.get("temperature", 0))
            sensor_data["humidity"].append(payload.get("humidity", 0))
            sensor_data["timestamps"].append(datetime.now().strftime("%H:%M:%S"))
        
        print(f"✓ Data received - Temp: {payload.get('temperature')}°C, Humidity: {payload.get('humidity')}%")
    except json.JSONDecodeError:
        print(f"✗ Failed to decode message: {msg.payload}")
    except Exception as e:
        print(f"✗ Error processing message: {e}")


def on_subscribe(client, userdata, mid, granted_qos):
    """Callback when subscription is confirmed."""
    print(f"✓ Subscription confirmed with QoS: {granted_qos}")


def on_unsubscribe(client, userdata, mid):
    """Callback when unsubscription is confirmed."""
    print("✓ Unsubscribed from topic")


def create_mqtt_client():
    """Create and configure MQTT client."""
    client = mqtt.Client(client_id="iot-dashboard-dht11")
    
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_unsubscribe = on_unsubscribe
    
    return client


def start_mqtt_connection():
    """Start MQTT connection in a separate thread."""
    client = create_mqtt_client()
    
    try:
        print(f"🔗 Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
        print("✓ MQTT loop started")
        return client
    except Exception as e:
        print(f"✗ Failed to connect to MQTT broker: {e}")
        return None


def get_sensor_data():
    """Get current sensor data in a thread-safe manner."""
    with data_lock:
        return {
            "temperature": list(sensor_data["temperature"]),
            "humidity": list(sensor_data["humidity"]),
            "timestamps": list(sensor_data["timestamps"]),
        }


def get_latest_reading():
    """Get the latest sensor reading."""
    with data_lock:
        if sensor_data["temperature"]:
            return {
                "temperature": sensor_data["temperature"][-1],
                "humidity": sensor_data["humidity"][-1],
                "timestamp": sensor_data["timestamps"][-1],
            }
    return {"temperature": 0, "humidity": 0, "timestamp": "N/A"}
