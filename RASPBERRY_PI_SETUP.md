# 🔌 Raspberry Pi Integration Guide
## Campus Guardian Drone - Edge Device Setup

**Purpose:** Configure Raspberry Pi as edge camera device for remote drone surveillance

---

## 📋 REQUIREMENTS

### Hardware
- Raspberry Pi 4 (2GB+ RAM recommended)
- Raspberry Pi Camera Module v2 or USB webcam
- MicroSD card (16GB+)
- Power supply (5V 3A)
- Network connection (WiFi or Ethernet)

### Software
- Raspberry Pi OS (64-bit recommended)
- Python 3.9+
- picamera2 (for Pi Camera) or opencv-python (for USB)

---

## 🚀 QUICK SETUP

### 1. Install Raspberry Pi OS
```bash
# Download Raspberry Pi Imager
# Flash SD card with Raspberry Pi OS (64-bit)
# Enable SSH and WiFi during imaging
```

### 2. Initial Configuration
```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
sudo apt install python3-pip python3-venv -y
```

### 3. Install Camera Support
```bash
# For Pi Camera Module
sudo apt install python3-picamera2 -y

# For USB Webcam
pip3 install opencv-python

# Test camera
libcamera-hello  # Should show camera preview
```

### 4. Clone & Configure Client Script
```bash
# Create project directory
mkdir ~/campus-guardian-client
cd ~/campus-guardian-client

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install requests opencv-python python-dotenv Pillow
```

---

## 📁 CLIENT SCRIPT

Create `rpi_client.py`:

```python
"""
Raspberry Pi Client for Campus Guardian Drone
Captures images/video and sends to main server
"""
import os
import time
import requests
from io import BytesIO
from PIL import Image
import base64
from datetime import datetime

# Try Pi Camera first, fall back to OpenCV
try:
    from picamera2 import Picamera2
    USE_PI_CAMERA = True
    print("✅ Using Raspberry Pi Camera Module")
except ImportError:
    import cv2
    USE_PI_CAMERA = False
    print("⚠️  Using USB/OpenCV camera")

# Configuration (or use .env file)
SERVER_URL = os.getenv('SERVER_URL', 'http://your-server-ip:8080')
DEVICE_ID = os.getenv('DEVICE_ID', 'RPI-CAM-001')
DEVICE_LOCATION = os.getenv('DEVICE_LOCATION', 'Campus-North')
UPLOAD_INTERVAL = float(os.getenv('UPLOAD_INTERVAL', '3.0'))  # seconds

class RPiCamera:
    def __init__(self):
        if USE_PI_CAMERA:
            self.camera = Picamera2()
            config = self.camera.create_still_configuration()
            self.camera.configure(config)
            self.camera.start()
            time.sleep(2)  # Warm up
        else:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise Exception("❌ Could not open camera")
        
        print(f"📷 Camera initialized - Device: {DEVICE_ID}")
    
    def capture_frame(self):
        """Capture single frame"""
        if USE_PI_CAMERA:
            frame = self.camera.capture_array()
            # Convert to RGB
            from PIL import Image
            return Image.fromarray(frame)
        else:
            ret, frame = self.camera.read()
            if not ret:
                return None
            # Convert BGR to RGB
            import cv2
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return Image.fromarray(frame)
    
    def frame_to_base64(self, frame):
        """Convert PIL Image to base64"""
        buffered = BytesIO()
        frame.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def close(self):
        if USE_PI_CAMERA:
            self.camera.stop()
        else:
            self.camera.release()

def send_frame_to_server(frame_base64):
    """Send frame to main server for detection"""
    try:
        response = requests.post(
            f"{SERVER_URL}/rpi/detect",
            json={
                'device_id': DEVICE_ID,
                'location': DEVICE_LOCATION,
                'timestamp': datetime.now().isoformat(),
                'image': f'data:image/jpeg;base64,{frame_base64}'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                detections = data.get('detections', [])
                print(f"✅ Detected: {len(detections)} objects")
                return True
        else:
            print(f"⚠️  Server error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    print(f"🚁 Campus Guardian RPi Client")
    print(f"📍 Device: {DEVICE_ID} @ {DEVICE_LOCATION}")
    print(f"🌐 Server: {SERVER_URL}")
    print(f"⏱️  Upload interval: {UPLOAD_INTERVAL}s")
    print("-" * 50)
    
    camera = RPiCamera()
    
    try:
        frame_count = 0
        while True:
            # Capture frame
            frame = camera.capture_frame()
            if frame is None:
                print("⚠️  Failed to capture frame")
                time.sleep(1)
                continue
            
            # Convert to base64
            frame_base64 = camera.frame_to_base64(frame)
            
            # Send to server
            frame_count += 1
            print(f"📤 Sending frame #{frame_count}...", end=" ")
            send_frame_to_server(frame_base64)
            
            # Wait for next upload
            time.sleep(UPLOAD_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    finally:
        camera.close()

if __name__ == "__main__":
    main()
```

---

## 🔐 CONFIGURATION

Create `.env` file:
```env
# Server Configuration
SERVER_URL=http://192.168.1.100:8080
DEVICE_ID=RPI-CAM-001
DEVICE_LOCATION=Campus-North-Gate

# Upload Settings
UPLOAD_INTERVAL=3.0  # seconds between frames
```

---

## 🏃 RUNNING THE CLIENT

### Manual Start
```bash
cd ~/campus-guardian-client
source venv/bin/activate
python rpi_client.py
```

### Auto-Start on Boot (Systemd Service)

Create `/etc/systemd/system/campus-guardian.service`:
```ini
[Unit]
Description=Campus Guardian RPi Camera Client
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/campus-guardian-client
ExecStart=/home/pi/campus-guardian-client/venv/bin/python rpi_client.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable campus-guardian.service
sudo systemctl start campus-guardian.service

# Check status
sudo systemctl status campus-guardian.service

# View logs
journalctl -u campus-guardian.service -f
```

---

## 📊 TESTING

### 1. Test Camera
```bash
python3 -c "from picamera2 import Picamera2; cam = Picamera2(); cam.start(); print('Camera OK')"
```

### 2. Test Server Connection
```bash
curl http://your-server-ip:8080/health
```

### 3. Test Frame Upload
```bash
python rpi_client.py
# Should see: ✅ Detected: X objects
```

---

## 🔧 TROUBLESHOOTING

### Camera Not Detected
```bash
# Check if camera is enabled
sudo raspi-config
# Interface Options → Camera → Enable

# List camera devices
v4l2-ctl --list-devices

# Check USB camera
ls /dev/video*
```

### Connection Refused
```bash
# Check server is running
curl http://server-ip:8080/health

# Check firewall
sudo ufw allow 8080
```

### Permission Denied
```bash
# Add user to video group  
sudo usermod -a -G video pi

# Reboot
sudo reboot
```

---

## 🎯 SERVER-SIDE ENDPOINTS

### Required Endpoint: `/rpi/detect`
```python
@app.route('/rpi/detect', methods=['POST'])
def rpi_detect():
    data = request.get_json()
    device_id = data['device_id']
    location = data['location']
    image = data['image']  # base64
    
    # Process with YOLO
    # Return detections
```

See `app.py` for full implementation.

---

## 📈 PERFORMANCE TIPS

1. **Lower Resolution**: 640x480 for faster uploads
2. **JPEG Quality**: 70-85 for balance
3. **Batch Uploads**: Send every 5s instead of 3s
4. **Edge Detection**: Run lightweight detection on Pi, send only alerts
5. **Network**: Use Ethernet for stable connection

---

## 🚀 ADVANCED FEATURES

### Multiple Cameras
```python
# Modify rpi_client.py to support multiple camera IDs
CAMERA_ID = 0  # or 1, 2, etc.
```

### Video Streaming
```python
# Use RTSP stream instead of frame uploads
# Install: pip install ffmpeg-python
```

### Edge AI
```python
# Run YOLO on Pi for pre-filtering
# pip install ultralytics
# Only send frames with detections
```

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Raspberry Pi OS installed
- [ ] Camera module connected & tested
- [ ] Python dependencies installed
- [ ] `.env` configured with server URL
- [ ] Client script tested manually
- [ ] Systemd service enabled
- [ ] Auto-start on boot verified
- [ ] Network connectivity stable
- [ ] Server endpoints working

---

## 📞 SUPPORT

**Error logs:**
```bash
journalctl -u campus-guardian.service --since today
```

**Manual testing:**
```bash
# Run with verbose output
python rpi_client.py --verbose
```

**Network debugging:**
```bash
ping server-ip
curl http://server-ip:8080/health
```

---

**You now have a distributed edge surveillance system!** 🎯
