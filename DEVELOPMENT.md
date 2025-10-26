# IoT Dashboard - DHT11 | Development Guide 🚀

This guide will help you get started with developing and running the IoT Dashboard locally.

## Quick Start (5 minutes)

### 1. Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### 2. Clone and Setup
```bash
git clone <repository-url>
cd iot-dashboard-dht11

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```
Visit http://localhost:8050 in your browser.

### 4. Generate Test Data
In a separate terminal:
```bash
python test_publisher.py
```

## Project Structure

```
iot-dashboard-dht11/
├── app.py                      # Main Dash application
│   ├── Dashboard layout
│   ├── Callbacks for live updates
│   ├── Chart generation
│   └── Server configuration
│
├── mqtt_client.py              # MQTT communication
│   ├── Client initialization
│   ├── Connection handlers
│   ├── Message parsing
│   ├── Thread-safe data storage
│   └── Data retrieval functions
│
├── test_publisher.py           # Test data generator
│   ├── Simulates DHT11 sensor
│   ├── Publishes to MQTT topic
│   └── Realistic data variations
│
├── requirements.txt            # Python dependencies
├── Procfile                    # Render deployment config
├── .gitignore                 # Git ignore patterns
├── README.md                  # User documentation
├── DEVELOPMENT.md             # This file
│
└── assets/
    └── style.css              # Custom CSS styling
```

## Architecture Overview

### MQTT Flow
```
[DHT11 Sensor/Publisher]
         ↓
[MQTT Broker: broker.emqx.io]
         ↓
[mqtt_client.py: Subscriber]
         ↓
[Thread-safe Buffer (deque)]
         ↓
[app.py: Callbacks]
         ↓
[Plotly Charts / Dashboard]
```

### Data Flow
1. **MQTT Subscription**: `mqtt_client.py` subscribes to `dht11/sensor` topic
2. **Message Reception**: JSON payloads received with `temperature` and `humidity`
3. **Data Storage**: Data buffered in thread-safe deques (max 100 points)
4. **Dashboard Polling**: Dash callbacks request data every 3 seconds
5. **Chart Update**: Plotly graphs re-render with latest data

## Key Components

### mqtt_client.py

**Main Functions:**
- `start_mqtt_connection()` - Initialize and connect to broker
- `get_sensor_data()` - Retrieve all buffered sensor data
- `get_latest_reading()` - Get most recent reading

**Data Structure:**
```python
sensor_data = {
    "temperature": deque([...]),  # Last 100 values
    "humidity": deque([...]),     # Last 100 values
    "timestamps": deque([...]),   # Corresponding timestamps
}
```

**Thread Safety:**
- Uses `threading.Lock()` for concurrent access
- Safe for MQTT callback thread + Dash callback threads

### app.py

**Callbacks:**
1. `update_clock()` - Updates live clock display
2. `update_stats()` - Updates current temp/humidity cards
3. `update_temperature_chart()` - Generates temperature line chart
4. `update_humidity_chart()` - Generates humidity line chart

**Update Mechanism:**
- `dcc.Interval` component fires every 3000ms (3 seconds)
- Triggers all callbacks to refresh data
- Charts show last 100 data points with smooth animation

### Custom Styling

**Theme Variables** (in `assets/style.css`):
- Slate 950 (`#0f172a`) - Background
- Slate 800 (`#1e293b`) - Card background
- Orange (`#f97316`) - Temperature chart color
- Cyan (`#06b6d4`) - Humidity chart color

## Development Workflow

### Local Testing

#### Terminal 1: Run Dashboard
```bash
python app.py
```

#### Terminal 2: Generate Test Data
```bash
python test_publisher.py
```

#### Terminal 3: Monitor MQTT (Optional)
```bash
# Install mqtt-cli first
mqtt sub -h broker.emqx.io -t "dht11/sensor"
```

### Publishing Real Data

#### Using MQTT CLI
```bash
mqtt pub -h broker.emqx.io -t dht11/sensor -m '{"temperature": 25.5, "humidity": 60.0}'
```

#### Using Python Script
```python
import paho.mqtt.client as mqtt
import json

client = mqtt.Client()
client.connect("broker.emqx.io", 1883)
payload = json.dumps({"temperature": 25.5, "humidity": 60.0})
client.publish("dht11/sensor", payload)
client.disconnect()
```

#### Using Node-RED
```json
{
  "msg": {
    "payload": {
      "temperature": 25.5,
      "humidity": 60.0
    }
  }
}
```

## Debugging

### Enable Debug Mode
Edit `app.py` last line:
```python
if __name__ == "__main__":
    app.run_server(debug=True, ...)  # Set debug=True
```

### View Logs
- Browser console: Press F12, check Console tab
- Terminal output: Shows MQTT connection status and errors

### Common Issues

**Issue: "Connection refused"**
- Broker might be down
- Check internet connectivity
- Verify firewall settings

**Issue: "No data displayed"**
- Ensure test_publisher.py is running
- Verify MQTT topic is correct: `dht11/sensor`
- Check message format: `{"temperature": X, "humidity": Y}`

**Issue: "Port 8050 already in use"**
```bash
# Find process using port 8050
netstat -ano | findstr :8050
# Kill process (replace PID with actual ID)
taskkill /PID <PID> /F
```

**Issue: "Import not found" errors**
```bash
# Ensure virtual environment is activated
# Then reinstall dependencies
pip install --upgrade -r requirements.txt
```

## Customization Guide

### Change Update Interval
**File:** `app.py`
```python
dcc.Interval(
    id="interval-component",
    interval=5000,  # Change to 5 seconds
    n_intervals=0,
)
```

### Change MQTT Topic
**File:** `mqtt_client.py`
```python
MQTT_TOPIC = "my/custom/topic"  # Change this
```

### Change MQTT Broker
**File:** `mqtt_client.py`
```python
MQTT_BROKER = "your-broker.example.com"
MQTT_PORT = 1883
```

### Change Chart Colors
**File:** `app.py`
```python
line=dict(color="#FF5733", width=3)  # Change hex color
```

### Adjust Buffer Size
**File:** `mqtt_client.py`
```python
MAX_DATA_POINTS = 200  # Keep last 200 readings instead of 100
```

### Add New Metrics
Edit `mqtt_client.py`:
```python
sensor_data = {
    "temperature": deque(maxlen=MAX_DATA_POINTS),
    "humidity": deque(maxlen=MAX_DATA_POINTS),
    "pressure": deque(maxlen=MAX_DATA_POINTS),  # New!
    "timestamps": deque(maxlen=MAX_DATA_POINTS),
}
```

Edit `app.py` to add new chart callbacks.

## Deployment

### Local Testing (Production-like)
```bash
gunicorn app:app --bind 0.0.0.0:8050
```

### Docker Deployment
Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8050
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8050"]
```

Build and run:
```bash
docker build -t iot-dashboard .
docker run -p 8050:8050 iot-dashboard
```

### Render.com Deployment
See README.md "Deployment on Render.com" section.

## Performance Tips

1. **Reduce Update Frequency**
   - Increase interval in `dcc.Interval` for slower updates
   - Reduces server load and network usage

2. **Limit Buffer Size**
   - Decrease `MAX_DATA_POINTS` to store fewer readings
   - Reduces memory usage

3. **Optimize Charts**
   - Set `displayModeBar: False` to reduce chart toolbar
   - Use `responsive: True` for better mobile performance

4. **Enable Caching**
   - Add caching headers in production
   - Use CDN for static assets

## Testing

### Unit Testing
Create `test_mqtt_client.py`:
```python
import pytest
from mqtt_client import get_sensor_data, get_latest_reading

def test_sensor_data_structure():
    data = get_sensor_data()
    assert "temperature" in data
    assert "humidity" in data
    assert "timestamps" in data
```

Run tests:
```bash
pytest test_mqtt_client.py -v
```

## Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes and test locally
3. Commit: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Create Pull Request

## Troubleshooting Checklist

- [ ] Virtual environment activated?
- [ ] Dependencies installed? (`pip install -r requirements.txt`)
- [ ] Internet connection working?
- [ ] Broker accessible? (Test with `mqtt sub -h broker.emqx.io -t test`)
- [ ] Test publisher running? (`python test_publisher.py`)
- [ ] Correct MQTT topic?
- [ ] Message format correct? (`{"temperature": X, "humidity": Y}`)
- [ ] Port 8050 not in use? (`netstat -ano | findstr :8050`)

## Resources

- **Dash Documentation:** https://dash.plotly.com
- **Plotly Charts:** https://plotly.com/python
- **Paho MQTT:** https://www.eclipse.org/paho/index.php?page=clients/python/index.php
- **EMQX Broker:** https://www.emqx.io
- **Python Threading:** https://docs.python.org/3/library/threading.html

## Version History

**v1.0.0** (October 2025)
- Initial release
- Real-time temperature and humidity monitoring
- MQTT integration with broker.emqx.io
- Dark theme dashboard
- Responsive design
- Render deployment ready

---

**Last Updated:** October 2025
**Maintained by:** Your Name
