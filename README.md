# IoT Dashboard - DHT11 Sensor Monitor 🌡️

A modern, real-time IoT dashboard for monitoring DHT11 sensor data using Python Dash, Plotly, and MQTT. Built with a clean dark theme inspired by Tailwind CSS slate colors.

## Features

✨ **Real-time Data Visualization**
- Live temperature monitoring with animated line charts
- Live humidity monitoring with animated line charts
- Auto-refresh every 3 seconds

🌍 **MQTT Integration**
- Connects to public MQTT broker (broker.emqx.io)
- Subscribes to `dht11/sensor` topic
- Thread-safe data handling with automatic buffering (last 100 readings)

🎨 **Modern UI Design**
- Dark theme with Tailwind slate colors
- Responsive layout for desktop and mobile
- Live clock display
- Real-time stats cards
- Clean footer with last update timestamp

🚀 **Deployment Ready**
- Configured for Render.com deployment
- Uses Gunicorn as production WSGI server
- Environment-based port configuration

## Project Structure

```
iot-dashboard-dht11/
├── app.py                    # Main Dash application
├── mqtt_client.py           # MQTT client and data management
├── requirements.txt         # Python dependencies
├── Procfile                 # Render deployment config
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── assets/
    └── style.css           # Custom CSS styling
```

## Requirements

- Python 3.8+
- pip or conda

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/iot-dashboard-dht11.git
cd iot-dashboard-dht11
```

### 2. Create a virtual environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Running Locally

### Development Mode
```bash
python app.py
```
The dashboard will be available at `http://localhost:8050`

### Production Mode (with Gunicorn)
```bash
gunicorn app:app --bind 0.0.0.0:8050
```

## MQTT Configuration

### Subscribing to Sensor Data

To publish test data to the dashboard, you can use any MQTT client to publish to the topic `dht11/sensor`:

**Example payload (JSON):**
```json
{
    "temperature": 28.5,
    "humidity": 65.3
}
```

**Using MQTT CLI:**
```bash
# Install mqtt-cli from https://hivemq.github.io/mqtt-cli/
mqtt pub -h broker.emqx.io -t dht11/sensor -m '{"temperature": 28.5, "humidity": 65.3}'
```

**Using Python:**
```python
import paho.mqtt.client as mqtt
import json
import time

client = mqtt.Client()
client.connect("broker.emqx.io", 1883, 60)
client.loop_start()

while True:
    payload = {
        "temperature": 25.0 + (time.time() % 10),
        "humidity": 50.0 + (time.time() % 30)
    }
    client.publish("dht11/sensor", json.dumps(payload))
    time.sleep(2)
```

## Environment Variables

- `PORT`: Server port (default: 8050)

Set environment variables before running:
```bash
# Windows PowerShell
$env:PORT=8080
python app.py

# Windows Command Prompt
set PORT=8080
python app.py

# macOS/Linux
export PORT=8080
python app.py
```

## Deployment on Render.com

### Prerequisites
- GitHub account with repository pushed
- Render.com account

### Steps

1. **Create New Web Service**
   - Go to https://render.com/dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - **Name:** iot-dashboard-dht11
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Free (or Starter)

3. **Add Environment**
   - No specific environment variables needed (uses defaults)
   - Optional: `PORT` will be auto-assigned

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Your dashboard will be live at `https://<your-service-name>.onrender.com`

## File Descriptions

### `app.py`
Main Dash application with:
- Dashboard layout and styling
- Live clock callback
- Real-time stats updates
- Temperature and humidity charts
- Auto-refresh mechanism (3-second interval)

### `mqtt_client.py`
MQTT client logic with:
- Connection/disconnection handlers
- Message parsing and storage
- Thread-safe data access
- Auto-buffering of last 100 readings
- Callback functions for MQTT events

### `requirements.txt`
Python package dependencies:
- `dash` - Web framework
- `plotly` - Chart library
- `pandas` - Data handling
- `paho-mqtt` - MQTT client
- `gunicorn` - Production WSGI server

### `Procfile`
Render.com deployment configuration for Gunicorn

### `assets/style.css`
Custom CSS styling:
- Dark theme with Tailwind slate colors
- Scrollbar styling
- Input/button styling
- Responsive design

## Customization

### Change MQTT Topic
Edit `mqtt_client.py`:
```python
MQTT_TOPIC = "your/custom/topic"
```

### Change MQTT Broker
Edit `mqtt_client.py`:
```python
MQTT_BROKER = "your-broker-address"
MQTT_PORT = 1883
```

### Change Auto-Refresh Interval
Edit `app.py`:
```python
dcc.Interval(
    id="interval-component",
    interval=5000,  # milliseconds (5 seconds)
    n_intervals=0,
)
```

### Adjust Chart History
Edit `mqtt_client.py`:
```python
MAX_DATA_POINTS = 200  # Store last 200 readings
```

### Customize Colors
Edit `assets/style.css` or `app.py` inline styles to change the color scheme.

## Troubleshooting

### MQTT Connection Issues
- Verify internet connection
- Check if broker.emqx.io is accessible
- Ensure your firewall allows port 1883 outbound
- Check console logs for connection errors

### Charts Not Updating
- Ensure MQTT messages are being published to the correct topic
- Verify message format is valid JSON with `temperature` and `humidity` fields
- Check browser console for JavaScript errors

### Port Already in Use
```bash
# Windows - Find process on port 8050
netstat -ano | findstr :8050

# macOS/Linux - Find process on port 8050
lsof -i :8050

# Kill the process (on Windows, replace PID with the process ID)
taskkill /PID <PID> /F
```

## Contributing

Feel free to fork this project and submit pull requests for any improvements.

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Project Issues]
- Email: your-email@example.com

## Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your-email@example.com

---

**Last Updated:** October 2025
**Version:** 1.0.0
