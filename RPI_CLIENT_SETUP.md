# Raspberry Pi Client Setup Guide
## Campus Guardian Drone - Edge Device Configuration

---

## 📋 Hardware Requirements

### Minimum Configuration
- **Raspberry Pi 4B** (4GB RAM recommended, 2GB minimum)
- **Raspberry Pi Camera Module** (V2 or HQ Camera)
- **GPS Module** (optional but recommended)
  - USB GPS (e.g., VK-172, BU-353S4)
  - OR GPIO GPS module with serial connection
- **MicroSD Card** (32GB+, Class 10)
- **Power Supply** (5V 3A USB-C for Pi 4)
- **Internet Connection** (WiFi or Ethernet)

### Optional
- **Cooling** (heatsinks or fan for continuous operation)
- **Case** (weatherproof if outdoor deployment)
- **Battery Pack** (for mobile drone mounting)

---

## 🔧 Raspberry Pi OS Installation

### 1. Install Raspberry Pi OS (64-bit Lite recommended)

```bash
# Use Raspberry Pi Imager or download from:
# https://www.raspberrypi.com/software/

# Recommended: Raspberry Pi OS (64-bit) Lite
# Enables SSH, configure WiFi during setup
```

### 2. First Boot Configuration

```bash
# SSH into your Pi
ssh pi@raspberrypi.local
# Default password: raspberry (CHANGE THIS!)

# Change default password
passwd

# Update system
sudo apt update && sudo apt upgrade -y

# Enable camera
sudo raspi-config
# → Interface Options → Camera → Enable

# Enable I2C/Serial for GPS (if using GPIO GPS)
sudo raspi-config
# → Interface Options → I2C → Enable
# → Interface Options → Serial → No (login shell) → Yes (serial port)

# Reboot
sudo reboot
```

---

## 📦 Software Installation

### 1. Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv

# Install OpenCV dependencies
sudo apt install -y \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    libjasper-dev \
    libqt4-test \
    libhdf5-dev \
    libhdf5-serial-dev

# Install GPS dependencies (if using GPS)
sudo apt install -y gpsd gpsd-clients python3-gps

# Install build tools
sudo apt install -y build-essential cmake pkg-config
```

### 2. Create Project Directory

```bash
# Create project folder
mkdir ~/drone_client
cd ~/drone_client

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
# Activate venv first
source ~/drone_client/venv/bin/activate

# Install core dependencies
pip install --upgrade pip

# Install OpenCV (pre-built wheel for Pi)
pip install opencv-python-headless

# Install other dependencies
pip install requests gpsd-py3

# OPTIONAL: Install YOLO for local detection (WARNING: Large download + slow on Pi)
# Only install if you want detection on RPi itself
# pip install ultralytics

# For lightweight detection on Pi, use TFLite instead:
# pip install tflite-runtime
```

### 4. Download Client Script

```bash
# Option 1: Clone from GitHub (if you pushed rpi_client.py)
git clone https://github.com/YourUsername/drone-aerial-view.git
cp drone-aerial-view/rpi_client.py ~/drone_client/

# Option 2: Download directly
cd ~/drone_client
wget https://raw.githubusercontent.com/YourUsername/drone-aerial-view/main/rpi_client.py

# Option 3: Copy manually via SCP from your computer
# On your computer:
# scp rpi_client.py pi@raspberrypi.local:~/drone_client/
```

### 5. Make Script Executable

```bash
chmod +x ~/drone_client/rpi_client.py
```

---

## 🌐 Configure GPS (If Using)

### USB GPS Module (Easiest)

```bash
# Plug in USB GPS module

# Check if detected
lsusb
# Should see GPS device

# Start gpsd
sudo systemctl enable gpsd
sudo systemctl start gpsd

# Test GPS
gpsmon
# Wait for satellite fix (may take 1-5 minutes outdoors)
# Press Ctrl+C to exit

# Configure gpsd
sudo nano /etc/default/gpsd

# Set:
DEVICES="/dev/ttyUSB0"  # or /dev/ttyACM0, check with ls /dev/tty*
GPSD_OPTIONS="-n"
```

### GPIO GPS Module

```bash
# Connect GPS to GPIO pins:
# GPS VCC → Pi Pin 1 (3.3V)
# GPS GND → Pi Pin 6 (Ground)
# GPS TX → Pi Pin 10 (GPIO 15, RXD)
# GPS RX → Pi Pin 8 (GPIO 14, TXD)

# Disable serial console
sudo raspi-config
# → Interface Options → Serial → No (console) → Yes (hardware)

# Configure gpsd
sudo nano /etc/default/gpsd
# Set:
DEVICES="/dev/serial0"
GPSD_OPTIONS="-n"

# Restart gpsd
sudo systemctl restart gpsd

# Test
gpsmon
```

---

## 📷 Test Camera

```bash
# Test camera capture
raspistill -o test.jpg

# If using Python:
python3 << EOF
import cv2
cam = cv2.VideoCapture(0)
ret, frame = cam.read()
if ret:
    cv2.imwrite('test_opencv.jpg', frame)
    print("✅ Camera working!")
else:
    print("❌ Camera failed")
cam.release()
EOF
```

---

## 🚀 Running the Client

### Basic Usage (Camera Only, No GPS)

```bash
cd ~/drone_client
source venv/bin/activate

# Replace with your actual server URL
python3 rpi_client.py \
  --server http://YOUR_SERVER_IP:8080 \
  --device-id RPi-Gate-01 \
  --location "Main Campus Gate" \
  --interval 5
```

### Full Usage (Camera + GPS)

```bash
python3 rpi_client.py \
  --server http://YOUR_EC2_IP:8080 \
  --device-id RPi-Gate-01 \
  --location "Main Campus Gate" \
  --interval 5
```

### With Local Detection (If YOLO Installed on Pi)

```bash
# WARNING: Very slow on Raspberry Pi without coral/neural accelerator
python3 rpi_client.py \
  --server http://YOUR_SERVER_IP:8080 \
  --device-id RPi-Gate-01 \
  --location "Main Campus Gate" \
  --interval 10 \
  --local-detection \
  --send-only-detections
```

### Command Line Arguments

```
--server URL          Server URL (required)
--device-id ID        Unique device ID (default: RPi-001)
--location NAME       Physical location (default: Campus Gate)
--interval SECONDS    Capture interval (default: 5)
--camera INDEX        Camera index (default: 0)
--local-detection     Enable YOLO on RPi (requires ultralytics)
--send-only-detections  Only send frames with objects
```

---

## 🔄 Auto-Start on Boot

### Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/drone-client.service
```

**Add this content** (replace YOUR_SERVER_IP):

```ini
[Unit]
Description=Campus Guardian Drone - Raspberry Pi Client
After=network.target gpsd.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/drone_client
Environment="PATH=/home/pi/drone_client/venv/bin"
ExecStart=/home/pi/drone_client/venv/bin/python3 /home/pi/drone_client/rpi_client.py \
  --server http://YOUR_SERVER_IP:8080 \
  --device-id RPi-Gate-01 \
  --location "Main Campus Gate" \
  --interval 5
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable drone-client

# Start service now
sudo systemctl start drone-client

# Check status
sudo systemctl status drone-client

# View logs
sudo journalctl -u drone-client -f
```

---

## 🛠️ Troubleshooting

### Camera Not Working

```bash
# Check camera connection
vcgencmd get_camera
# Should show: supported=1 detected=1

# Check permissions
sudo usermod -a -G video pi

# Reboot
sudo reboot
```

### GPS Not Getting Fix

```bash
# GPS needs clear sky view
# Move outdoors, away from buildings
# Wait 2-5 minutes for initial fix

# Check GPS status
gpsmon

# Check satellites
cgps -s
```

### Connection Errors

```bash
# Test server reachability
ping YOUR_SERVER_IP

# Test server endpoint
curl http://YOUR_SERVER_IP:8080/system_status

# Check firewall (server side)
# Ensure port 8080 is open on server
```

### High CPU Usage

```bash
# Don't run YOLO on RPi without accelerator
# Disable local detection
# Increase capture interval to 10-30 seconds
# Lower image quality in script (jpeg_quality)
```

### Service Crashes

```bash
# Check logs
sudo journalctl -u drone-client -n 50

# Test manually first
cd ~/drone_client
source venv/bin/activate
python3 rpi_client.py --server http://YOUR_SERVER_IP:8080

# If errors, fix dependencies:
pip install --upgrade opencv-python-headless requests
```

---

## ⚙️ Configuration Options

Edit `rpi_client.py` to customize:

```python
self.config = {
    'camera_index': 0,           # Camera device ID
    'capture_interval': 5,       # Seconds between captures
    'image_width': 640,          # Lower = faster upload
    'image_height': 480,         # Lower = faster upload
    'jpeg_quality': 80,          # 60-90 recommended (lower = smaller)
    'local_detection': False,    # True = run YOLO on Pi
    'model_path': 'yolov8n.pt',  # Lightweight model
    'conf_threshold': 0.25,      # Detection confidence
    'send_only_detections': False,  # True = skip empty frames
}
```

---

## 🔋 Power Optimization

### For Battery-Powered Deployment

```bash
# Disable HDMI
sudo /usr/bin/tvservice -o

# Reduce GPU memory (edit /boot/config.txt)
sudo nano /boot/config.txt
# Add: gpu_mem=16

# Disable WiFi (if using Ethernet)
sudo rfkill block wifi

# Disable Bluetooth
sudo systemctl disable bluetooth
sudo systemctl disable hciuart

# Lower CPU frequency (edit /boot/config.txt)
# Add: arm_freq=600
```

---

## 📊 Monitoring RPi Client

### On Raspberry Pi

```bash
# View service logs (real-time)
sudo journalctl -u drone-client -f

# Check service status
sudo systemctl status drone-client

# View resource usage
htop  # Install: sudo apt install htop

# Check temperature
vcgencmd measure_temp
```

### On Main Server Dashboard

- Open **http://YOUR_SERVER_IP:8080**
- Check **System Health Panel** → RPi status should show **CONNECTED**
- Monitor real-time position updates on map
- View detection events in event log

---

## 🚁 Multiple Raspberry Pi Setup

Deploy multiple edge devices:

```bash
# RPi 1 (Main Gate)
python3 rpi_client.py \
  --server http://SERVER:8080 \
  --device-id RPi-Gate-01 \
  --location "Main Gate"

# RPi 2 (Parking Lot)
python3 rpi_client.py \
  --server http://SERVER:8080 \
  --device-id RPi-Parking-01 \
  --location "Parking Lot"

# RPi 3 (Library)
python3 rpi_client.py \
  --server http://SERVER:8080 \
  --device-id RPi-Library-01 \
  --location "Library Entrance"
```

All devices will report to same dashboard!

---

## 🎯 Verification Checklist

- [ ] Raspberry Pi OS installed and updated
- [ ] Camera working (tested with raspistill)
- [ ] GPS getting fix (if installed)
- [ ] Python environment created
- [ ] Dependencies installed
- [ ] rpi_client.py downloaded
- [ ] Server URL configured correctly
- [ ] Client connects to server successfully
- [ ] Images appearing on dashboard
- [ ] RPi status shows CONNECTED on dashboard
- [ ] GPS coordinates updating (if GPS installed)
- [ ] Systemd service configured for auto-start
- [ ] Client restarts on crashes

---

## 📚 Next Steps

1. **Test locally**: Run client, verify dashboard updates
2. **Deploy to field**: Mount RPi at strategic location
3. **Configure geofencing**: Set zones on dashboard
4. **Monitor 24/7**: Let system run autonomously
5. **Scale up**: Add more RPi devices as needed

---

**Support**: If issues persist, check server logs and ensure firewall rules allow connections on port 8080.

**Performance**: On Raspberry Pi 4 (4GB), expect ~0.5-1s per detection with local YOLO. For production, offload detection to main server (default behavior).
