import json
import os
import threading
from collections import deque
from datetime import datetime
from urllib.parse import urlparse

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.emqx.io")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_DHT = os.getenv("MQTT_TOPIC_DHT", "weresick/dht11")
MQTT_TOPIC_LED = os.getenv("MQTT_TOPIC_LED", "weresick/led")
MQTT_QOS = int(os.getenv("MQTT_QOS", 1))
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", 60))
MAX_DATA_POINTS = int(os.getenv("MAX_DATA_POINTS", 100))
MQTT_USERNAME = os.getenv("USERNAME")
MQTT_PASSWORD = os.getenv("PASSWORD")
MQTT_CLIENT_ID = os.getenv("CLIENT_ID", "iot-dashboard-dht11")

# Global data storage
sensor_data = {
    "temperature": deque(maxlen=MAX_DATA_POINTS),
    "humidity": deque(maxlen=MAX_DATA_POINTS),
    "timestamps": deque(maxlen=MAX_DATA_POINTS),
}

message_log = deque(maxlen=MAX_DATA_POINTS)

data_lock = threading.Lock()
mqtt_client = None


def _normalize_broker(broker: str) -> str:
    """Remove URI scheme if present so paho can connect."""
    parsed = urlparse(broker)
    if parsed.scheme:
        return parsed.hostname or broker
    return broker


def on_connect(client, userdata, flags, rc):
    """Callback when client connects to the broker."""
    if rc == 0:
        print("✓ Connected to MQTT broker successfully")
        # Subscribe to both DHT and LED topics
        client.subscribe(MQTT_TOPIC_DHT, qos=MQTT_QOS)
        print(f"✓ Subscribed to topic: {MQTT_TOPIC_DHT}")
        client.subscribe(MQTT_TOPIC_LED, qos=MQTT_QOS)
        print(f"✓ Subscribed to topic: {MQTT_TOPIC_LED}")
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
        decoded_payload = msg.payload.decode(errors="replace")
        try:
            payload = json.loads(decoded_payload)
        except json.JSONDecodeError:
            payload = decoded_payload

        timestamp = datetime.now().strftime("%H:%M:%S")

        with data_lock:
            message_log.append(
                {
                    "timestamp": timestamp,
                    "topic": msg.topic,
                    "payload": payload,
                }
            )

            if isinstance(payload, dict):
                sensor_data["temperature"].append(payload.get("temperature", 0))
                sensor_data["humidity"].append(payload.get("humidity", 0))
                sensor_data["timestamps"].append(timestamp)

        if isinstance(payload, dict):
            temp = payload.get("temperature")
            humidity = payload.get("humidity")
            print(f"✓ Data received - Temp: {temp}°C, Humidity: {humidity}%")
        else:
            print(f"✓ Message received: {payload}")
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
    client = mqtt.Client(client_id=MQTT_CLIENT_ID)

    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_unsubscribe = on_unsubscribe
    
    return client


def start_mqtt_connection():
    """Start MQTT connection in a separate thread."""
    global mqtt_client
    client = create_mqtt_client()
    broker_host = _normalize_broker(MQTT_BROKER)
    
    try:
        print(f"🔗 Connecting to {broker_host}:{MQTT_PORT}...")
        client.connect(broker_host, MQTT_PORT, keepalive=MQTT_KEEPALIVE)
        client.loop_start()
        print("✓ MQTT loop started")
        mqtt_client = client
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


def get_recent_messages(limit=None):
    """Return recent MQTT messages as a list of dicts."""
    with data_lock:
        messages = list(message_log)

    if limit is not None:
        return messages[-limit:]
    return messages


def publish_message(topic, payload, qos=None):
    """Publish a message to MQTT topic."""
    global mqtt_client
    if mqtt_client is None:
        print("✗ MQTT client not connected")
        return False

    try:
        qos_to_use = qos if qos is not None else MQTT_QOS
        mqtt_client.publish(topic, payload, qos=qos_to_use)
        print(f"✓ Published to {topic}: {payload}")
        return True
    except Exception as e:
        print(f"✗ Failed to publish: {e}")
        return False
