# 🚀 Quick Start Guide - Deploy in 15 Minutes!

## Campus Guardian Drone - Production Deployment

---

## 📋 What You'll Get

✅ **Full autonomous drone surveillance system**  
✅ **Running on AWS EC2** (t3.medium, ~$32/month)  
✅ **Web dashboard** accessible worldwide  
✅ **Raspberry Pi edge devices** sending real-time data  
✅ **24/7 autonomous operation** with auto-charging  
✅ **Complete API** for integrations  

---

## 🎯 Three Deployment Options

### Option 1: **AWS EC2** (Recommended for Production)
- ⏱️ **Time**: 15-20 minutes
- 💰 **Cost**: ~$32-35/month
- 🌐 **Access**: Public IP + optional domain
- 🔄 **Uptime**: 99.9%

### Option 2: **Local Server** (Demo/Development)
- ⏱️ **Time**: 2 minutes
- 💰 **Cost**: Free
- 🌐 **Access**: localhost only
- 🔄 **Uptime**: While your computer runs

### Option 3: **Docker Desktop** (Testing)
- ⏱️ **Time**: 5 minutes
- 💰 **Cost**: Free
- 🌐 **Access**: localhost only
- 🔄 **Uptime**: While Docker runs

---

## 🚀 FASTEST PATH: AWS EC2 Automated Deployment

### Step 1: Pre-requisites (5 minutes)

```bash
# 1. Install AWS CLI (macOS)
brew install awscli

# 2. Configure AWS credentials
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Format (json)

# 3. Get Cloudinary account (free tier)
# Visit: https://cloudinary.com/users/register_free
# Note your: cloud_name, api_key, api_secret
```

### Step 2: Configure Environment (2 minutes)

```bash
cd "/Users/mohitkumra/Desktop/DL Notebooks/hack"

# Copy environment template
cp .env.example .env

# Edit .env file
nano .env
```

**Required: Add Cloudinary credentials:**
```bash
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here

FLASK_ENV=production
PORT=8080
SECRET_KEY=change-this-to-random-string
```

**Optional: Add Telegram bot (for alerts):**
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Step 3: Deploy to AWS (10 minutes)

```bash
# Run automated deployment script
./deploy_aws.sh
```

**What happens:**
1. ✅ Creates EC2 instance (t3.medium)
2. ✅ Configures security groups (opens ports 22, 80, 8080, 443)
3. ✅ Installs Docker & dependencies
4. ✅ Clones your code
5. ✅ Builds containers
6. ✅ Starts server

**Output:**
```
╔════════════════════════════════════════════════════════════╗
║          🎉 DEPLOYMENT SUCCESSFUL!                         ║
╚════════════════════════════════════════════════════════════╝

Dashboard: http://12.34.56.78:8080
SSH: ssh -i ~/.ssh/drone-guardian-key.pem ubuntu@12.34.56.78
```

### Step 4: Access Your Dashboard

```bash
# Open in browser (replace with your IP)
open http://YOUR_EC2_IP:8080
```

**You should see:**
- 🗺️ Live map with drone position
- 📊 Telemetry panel (battery, altitude, GPS)
- 📈 Operational metrics
- 🎯 System health indicators

---

## 🔧 Alternative: Local Development (2 minutes)

### Quick Start (No Docker)

```bash
cd "/Users/mohitkumra/Desktop/DL Notebooks/hack"

# Activate virtual environment
source .venv/bin/activate

# Start server
python app.py

# Open dashboard
open http://localhost:8080
```

### With Docker

```bash
# Build and run
docker-compose up --build

# Access dashboard
open http://localhost:8080
```

---

## 📡 Raspberry Pi Setup (Add Edge Devices)

### Step 1: Prepare Raspberry Pi

```bash
# SSH into your Raspberry Pi
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y python3-opencv gpsd gpsd-clients

# Enable camera
sudo raspi-config
# → Interface Options → Camera → Enable
```

### Step 2: Install Client

```bash
# On Raspberry Pi
mkdir ~/drone_client
cd ~/drone_client

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install opencv-python-headless requests gpsd-py3

# Download client script
wget https://raw.githubusercontent.com/HaryiankKumra/drone-aerial-view/main/rpi_client.py
# Or copy manually: scp rpi_client.py pi@raspberrypi.local:~/drone_client/
```

### Step 3: Run Client

```bash
# On Raspberry Pi
cd ~/drone_client
source venv/bin/activate

# Connect to your AWS EC2 server (replace IP)
python3 rpi_client.py \
  --server http://YOUR_EC2_IP:8080 \
  --device-id RPi-Gate-01 \
  --location "Main Campus Gate" \
  --interval 5
```

**Expected output:**
```
🚁 Raspberry Pi Client Initialized
   Device ID: RPi-Gate-01
   Location: Main Campus Gate
   Server: http://YOUR_EC2_IP:8080

✅ Camera initialized successfully
✅ GPS initialized
✅ Server is reachable

🔄 Starting capture loop (every 5s)

[12:34:56] Frame #1
📍 GPS: 30.35600, 76.36490 | Speed: 2.5 m/s
📸 Image size: 45.2 KB
✅ Data sent successfully | Objects: 3
```

### Step 4: Auto-Start on Boot (Optional)

```bash
# Create systemd service
sudo nano /etc/systemd/system/drone-client.service
```

**Add this content** (replace YOUR_EC2_IP):
```ini
[Unit]
Description=Campus Guardian Drone Client
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/drone_client
Environment="PATH=/home/pi/drone_client/venv/bin"
ExecStart=/home/pi/drone_client/venv/bin/python3 /home/pi/drone_client/rpi_client.py \
  --server http://YOUR_EC2_IP:8080 \
  --device-id RPi-Gate-01 \
  --location "Main Campus Gate" \
  --interval 5
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable drone-client
sudo systemctl start drone-client

# Check status
sudo systemctl status drone-client
```

---

## ✅ Verification Checklist

### Server (AWS EC2)
- [ ] EC2 instance running (check AWS console)
- [ ] Security group allows port 8080
- [ ] Dashboard accessible at `http://YOUR_IP:8080`
- [ ] System status shows all green
- [ ] Telemetry updating every second
- [ ] Docker containers running (`docker-compose ps`)

### Raspberry Pi (Edge Device)
- [ ] Camera working (test with `raspistill -o test.jpg`)
- [ ] GPS getting fix (test with `gpsmon`)
- [ ] Client script running without errors
- [ ] Dashboard shows RPi status: **CONNECTED** (changes from DISCONNECTED)
- [ ] GPS coordinates updating on map
- [ ] Speed showing actual values (not 0.0)

---

## 🎯 Test Your Deployment

### 1. Simulate Everything (No Hardware)

```bash
# Run simulation script (local computer)
cd "/Users/mohitkumra/Desktop/DL Notebooks/hack"
source .venv/bin/activate
python simulate_system.py

# Watch dashboard while simulation runs
# You'll see:
# - RPi status change to CONNECTED
# - Position updates on map
# - Metrics incrementing
# - System health updates
```

### 2. Test API Endpoints

```bash
# Replace YOUR_EC2_IP with your actual IP

# Get telemetry
curl http://YOUR_EC2_IP:8080/telemetry

# Get system status
curl http://YOUR_EC2_IP:8080/system_status

# Simulate RPi detection
curl -X POST http://YOUR_EC2_IP:8080/rpi/detect \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "Test-RPi",
    "gps_latitude": 30.3560,
    "gps_longitude": 76.3649,
    "speed": 2.5,
    "camera_ok": true,
    "model_ok": true
  }'
```

### 3. Monitor Logs

```bash
# SSH into EC2
ssh -i ~/.ssh/drone-guardian-key.pem ubuntu@YOUR_EC2_IP

# View application logs
cd drone-aerial-view
docker-compose logs -f

# View just errors
docker-compose logs -f | grep -i error
```

---

## 🛠️ Common Issues & Fixes

### Issue: "Cannot connect to AWS"

```bash
# Check AWS credentials
aws sts get-caller-identity

# If not configured:
aws configure
```

### Issue: "Dashboard not loading"

```bash
# Check if server is running
ssh -i ~/.ssh/drone-guardian-key.pem ubuntu@YOUR_EC2_IP
docker-compose ps

# If not running, start it:
cd drone-aerial-view
docker-compose up -d

# Check logs for errors
docker-compose logs
```

### Issue: "RPi not connecting"

```bash
# On RPi, test server connection
curl http://YOUR_EC2_IP:8080/system_status

# If timeout:
# 1. Check EC2 security group allows port 8080
# 2. Check RPi has internet connection: ping google.com
# 3. Check firewall on EC2: sudo ufw status
```

### Issue: "GPS not working on RPi"

```bash
# On Raspberry Pi
# Check GPS module connected
lsusb  # Should see GPS device

# Test GPS
gpsmon
# Wait 2-5 minutes for satellite fix (needs outdoor/window view)

# If still not working:
sudo systemctl restart gpsd
```

---

## 📚 Next Steps

### 1. Configure Geofencing

```bash
# On dashboard:
1. Click "Draw Zone" button
2. Draw polygon on map
3. Set type: patrol / no_fly / restricted
4. Save zone
```

### 2. Set Up Multiple RPi Devices

```bash
# RPi 1 (Main Gate)
python3 rpi_client.py \
  --server http://YOUR_EC2_IP:8080 \
  --device-id RPi-Gate-01 \
  --location "Main Gate"

# RPi 2 (Parking Lot)
python3 rpi_client.py \
  --server http://YOUR_EC2_IP:8080 \
  --device-id RPi-Parking-01 \
  --location "Parking Lot"
```

### 3. Enable HTTPS (Optional)

```bash
# Follow detailed guide in AWS_DEPLOYMENT.md
# Requires domain name
```

### 4. Set Up Telegram Alerts

```bash
# 1. Message @BotFather on Telegram
# 2. Create new bot, copy token
# 3. Message your bot
# 4. Visit: https://api.telegram.org/bot<TOKEN>/getUpdates
# 5. Copy chat_id
# 6. Add to .env file
# 7. Restart server
```

---

## 💰 Cost Breakdown

### AWS EC2 Deployment
- **EC2 Instance** (t3.medium): $30.42/month
- **EBS Storage** (30GB gp3): $2.40/month
- **Data Transfer**: First 100GB free
- **Elastic IP**: Free (while attached)
- **Total**: ~$32-35/month

### Raspberry Pi (One-time)
- **Raspberry Pi 4B (4GB)**: $55
- **Camera Module**: $25
- **GPS Module** (optional): $15-30
- **Power Supply**: $10
- **MicroSD Card (32GB)**: $10
- **Total**: ~$115-130 per device

---

## 🎉 You're Live!

Your Campus Guardian Drone system is now:
- ✅ **Running 24/7** on AWS EC2
- ✅ **Accepting data** from Raspberry Pi devices
- ✅ **Tracking positions** in real-time
- ✅ **Detecting violations** automatically
- ✅ **Sending alerts** (if Telegram configured)
- ✅ **Recording metrics** for analysis
- ✅ **Auto-recovering** from failures

**Dashboard**: `http://YOUR_EC2_IP:8080`  
**API Docs**: See [API_REFERENCE.md](API_REFERENCE.md)  
**Full AWS Guide**: See [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)  
**RPi Setup**: See [RPI_CLIENT_SETUP.md](RPI_CLIENT_SETUP.md)

---

## 📞 Support & Documentation

- **Test Report**: [TEST_REPORT.md](TEST_REPORT.md) - Verification results
- **Deployment Guide**: [DEPLOYMENT_README.md](DEPLOYMENT_README.md) - Docker details
- **API Reference**: [API_REFERENCE.md](API_REFERENCE.md) - All 26 endpoints
- **AWS Deployment**: [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) - EC2 setup
- **RPi Setup**: [RPI_CLIENT_SETUP.md](RPI_CLIENT_SETUP.md) - Edge devices

---

**Deployment Time**: 15-20 minutes  
**Difficulty**: Easy (automated script)  
**Hackathon Ready**: ✅ YES!  

🏆 **GO WIN THAT HACKATHON!** 🏆
