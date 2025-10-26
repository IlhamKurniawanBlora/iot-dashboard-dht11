# 🚀 Quick Start Guide - IoT Dashboard DHT11

Get your IoT Dashboard running in **less than 5 minutes**!

## Prerequisites
- Python 3.8+ ([Download](https://www.python.org/downloads/))
- Git (optional, for cloning)

## Option 1: Using Python (Recommended)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/iot-dashboard-dht11.git
cd iot-dashboard-dht11
```

Or download and extract the ZIP file.

### Step 2: Create Virtual Environment
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Dashboard
```bash
python app.py
```

**Dashboard is now live at:** http://localhost:8050

### Step 5: Generate Test Data (New Terminal)
```bash
# Activate virtual environment first
python test_publisher.py
```

### Done! 🎉
You should see:
- Dashboard with live charts
- Temperature and humidity readings updating every 3 seconds
- Real-time clock in the header

---

## Option 2: Using Docker

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/iot-dashboard-dht11.git
cd iot-dashboard-dht11
```

### Step 2: Build and Run
```bash
# Build image
docker build -t iot-dashboard .

# Run container
docker run -p 8050:8050 iot-dashboard
```

**Dashboard is now live at:** http://localhost:8050

### Using Docker Compose
```bash
docker-compose up
```

---

## Option 3: Cloud Deployment (Render.com)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-url>
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn app:app`
6. Click "Create Web Service"

**Dashboard will be live at:** `https://<your-service-name>.onrender.com`

---

## Publishing Sensor Data

### Option A: Use Test Publisher
```bash
python test_publisher.py
```

### Option B: Publish Manually
```bash
# Using mqtt-cli (https://hivemq.github.io/mqtt-cli/)
mqtt pub -h broker.emqx.io -t dht11/sensor -m '{"temperature": 25.5, "humidity": 60.0}'
```

### Option C: Python Script
```python
import paho.mqtt.client as mqtt
import json
import time

client = mqtt.Client()
client.connect("broker.emqx.io", 1883, 60)
client.loop_start()

for i in range(10):
    payload = json.dumps({
        "temperature": 20 + i,
        "humidity": 50 + i * 2
    })
    client.publish("dht11/sensor", payload)
    time.sleep(1)

client.loop_stop()
client.disconnect()
```

---

## Troubleshooting

### "Port 8050 already in use"
```bash
# Kill process on port 8050
# Windows:
netstat -ano | findstr :8050
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8050
kill -9 <PID>
```

### "No data displayed"
1. Check if test_publisher.py is running
2. Verify topic is `dht11/sensor`
3. Check message format: `{"temperature": X, "humidity": Y}`

### "Import not found errors"
```bash
# Ensure virtual environment is activated
pip install --upgrade -r requirements.txt
```

### "Connection refused"
- Check internet connectivity
- Verify broker.emqx.io is accessible
- Check firewall settings

---

## Next Steps

After getting started:

1. **Read Documentation**
   - [README.md](README.md) - Full documentation
   - [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide

2. **Customize the Dashboard**
   - Change MQTT topic in `mqtt_client.py`
   - Modify colors in `assets/style.css`
   - Add new metrics to sensor data

3. **Deploy Globally**
   - Use Render.com (see Option 3)
   - Set up custom domain
   - Enable HTTPS

4. **Add Real Hardware**
   - Connect DHT11 sensor to microcontroller
   - Configure device to publish MQTT data
   - Monitor real sensor data in dashboard

---

## Project Structure
```
iot-dashboard-dht11/
├── app.py              # Main Dash application
├── mqtt_client.py      # MQTT communication
├── test_publisher.py   # Test data generator
├── requirements.txt    # Dependencies
├── Procfile           # Render config
└── assets/
    └── style.css      # Custom CSS
```

## Key Features
✅ Real-time temperature and humidity monitoring  
✅ Modern dark theme UI  
✅ MQTT broker integration  
✅ Auto-refresh every 3 seconds  
✅ Responsive design  
✅ Ready for production deployment  

---

## Resources

| Resource | Link |
|----------|------|
| Dash Docs | https://dash.plotly.com |
| Plotly Charts | https://plotly.com/python |
| MQTT Guide | https://www.mqtt.org |
| Python Docs | https://docs.python.org |
| Docker Docs | https://docs.docker.com |

---

## Support

- 📖 See [README.md](README.md) for full documentation
- 🛠️ See [DEVELOPMENT.md](DEVELOPMENT.md) for development guide
- 🐳 See [DOCKER.md](DOCKER.md) for Docker guide
- 📝 Check GitHub Issues for common problems

---

**Made with ❤️ for IoT Enthusiasts**

Version 1.0.0 | October 2025
