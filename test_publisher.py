"""
Test script to simulate DHT11 sensor data publishing to MQTT broker.
This generates realistic temperature and humidity variations.
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# Configuration
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "dht11/sensor"

# Base values
BASE_TEMPERATURE = 24.0  # °C
BASE_HUMIDITY = 60.0     # %


def on_connect(client, userdata, flags, rc):
    """Callback on connection."""
    if rc == 0:
        print("✓ Connected to MQTT broker")
    else:
        print(f"✗ Connection failed with code {rc}")


def on_disconnect(client, userdata, rc):
    """Callback on disconnection."""
    if rc != 0:
        print(f"✗ Disconnected with code {rc}")


def simulate_sensor_data():
    """Generate realistic sensor data with slight variations."""
    # Add small random variations to simulate real sensor readings
    temp_variation = random.gauss(0, 0.5)  # Gaussian noise
    humidity_variation = random.gauss(0, 2.0)
    
    # Add gradual drift (sine wave pattern for realism)
    time_factor = (time.time() % 3600) / 3600.0  # 1-hour cycle
    temp_drift = 3 * (1 - 2 * abs(time_factor - 0.5))  # Varies from -1.5 to +1.5
    humidity_drift = 10 * (1 - 2 * abs(time_factor - 0.5))  # Varies from -5 to +5
    
    temperature = BASE_TEMPERATURE + temp_variation + temp_drift
    humidity = BASE_HUMIDITY + humidity_variation + humidity_drift
    
    # Clamp values to realistic ranges
    temperature = max(15.0, min(35.0, temperature))
    humidity = max(20.0, min(99.0, humidity))
    
    return {
        "temperature": round(temperature, 1),
        "humidity": round(humidity, 1),
    }


def main():
    """Main function to publish sensor data."""
    print("=" * 50)
    print("DHT11 MQTT Test Publisher")
    print("=" * 50)
    print(f"Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Topic: {MQTT_TOPIC}")
    print(f"Interval: 2 seconds")
    print("=" * 50)
    print()
    
    client = mqtt.Client(client_id=f"test-publisher-{int(time.time())}")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    try:
        print("🔗 Connecting to broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
        
        print("\n📤 Publishing sensor data (Press Ctrl+C to stop)...\n")
        
        message_count = 0
        while True:
            try:
                # Generate and publish data
                sensor_data = simulate_sensor_data()
                payload = json.dumps(sensor_data)
                
                result = client.publish(MQTT_TOPIC, payload, qos=1)
                message_count += 1
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                status = "✓" if result.rc == mqtt.MQTT_ERR_SUCCESS else "✗"
                
                print(
                    f"[{timestamp}] {status} Message #{message_count}: "
                    f"Temp={sensor_data['temperature']}°C, "
                    f"Humidity={sensor_data['humidity']}%"
                )
                
                time.sleep(2)  # Publish every 2 seconds
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"✗ Error publishing: {e}")
                time.sleep(2)
    
    except ConnectionRefusedError:
        print("✗ Failed to connect to MQTT broker")
        print("  Make sure the broker is running and accessible")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        print("\n\n🛑 Stopping publisher...")
        client.loop_stop()
        client.disconnect()
        print(f"✓ Published {message_count} messages total")
        print("✓ Disconnected")


if __name__ == "__main__":
    main()
