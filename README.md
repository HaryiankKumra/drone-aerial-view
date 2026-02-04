# Campus Guardian Drone - Aerial Surveillance System

**Professional drone surveillance system with real-time object detection, cloud storage, and web dashboard.**

🎯 Built for **Campus Guardian Drone Hackathon** - Complete aerial monitoring solution under ₹25,000

---

## Live Demo
🌐 **Dashboard**: https://drone-aerial-view.onrender.com/

---

## Features

### 🚁 Aerial Detection
- ✓ **YOLOv8-VisDrone** model optimized for top-down views
- ✓ Detects: pedestrian, bicycle, car, van, truck, bus, motor
- ✓ Real-time detection with live FPS counter
- ✓ Object tracking to prevent duplicate alerts
- ✓ 30-second cooldown for stationary objects

### 📊 Professional Dashboard
- ✓ Glassmorphism dark theme with cyan accents
- ✓ Live video feed with detection overlays
- ✓ Real-time alerts panel with animations
- ✓ Scan-line radar effects
- ✓ Manual recording button
- ✓ Object count statistics

### ☁️ Cloud Storage
- ✓ **Cloudinary integration** (25GB FREE permanent storage)
- ✓ Auto-upload detection images to cloud
- ✓ CDN-optimized delivery
- ✓ Automatic image optimization
- ✓ Fallback to local storage

### 🎯 Smart Detection
- ✓ Object tracking with 50px movement threshold
- ✓ 30-second alert cooldown for same object
- ✓ Auto-cleanup of old tracking data
- ✓ Manual snapshot recording
- ✓ Event metadata with timestamps

---

## Why Aerial-Trained Weights Are Critical

### The Problem with Standard YOLO Models
Standard YOLO models (trained on COCO dataset) are optimized for:
- **Side views** and **front views** of objects
- Ground-level camera angles (human perspective)
- Objects photographed from typical angles

### Why They Fail for Drone Surveillance
When viewing from a drone (top-down/bird's eye view):
- Cars look like rectangles from above, not the familiar side profile
- People appear as small circles/ovals, not full body shapes
- Motorcycles and bikes are hard to distinguish from above
- Standard models have **low accuracy** or **fail completely** at these angles

### The Solution: VisDrone Dataset
**VisDrone** is a specialized dataset with:
- 10,000+ images captured from drones
- Top-down and oblique aerial views
- Annotated for: pedestrian, people, bicycle, car, van, truck, tricycle, etc.
- Real-world drone surveillance scenarios

**YOLOv8 trained on VisDrone** learns to recognize objects from aerial perspectives, making it ideal for drone surveillance applications.

---

## Features
- ✓ Detects: **person, car, motorcycle, bus, truck** from TOP view
- ✓ Uses **YOLOv8 trained on VisDrone** dataset
- ✓ Draws bounding boxes with class name and confidence
- ✓ Shows live FPS and object count
- ✓ Supports **webcam, RTSP stream, or video file**
- ✓ Runs locally (no cloud calls)
- ✓ API-ready architecture (commented for future deployment)
- ✓ Press 'q' to quit safely

---

## Project Structure
```
hack/
├── config.py              # Centralized configuration
├── yolov8_webcam.py       # Main detection script
├── download_model.py      # Download VisDrone-trained weights
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── yolov8n-visdrone.pt   # Model weights (auto-downloaded)
```

---

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Aerial Detection Model

**⚠️ CRITICAL: You MUST use aerial-trained weights for top-down detection!**

Choose ONE of these options:

#### Option A: Find Pre-trained Weights (Fastest - 30 min)
```bash
python find_weights.py
```
This helps you find community-trained VisDrone weights online.

#### Option B: Train Your Own (Best - 2-4 hours)
```bash
# 1. Download VisDrone dataset from http://aiskyeye.com/
# 2. Extract to visdrone_data/ folder
# 3. Run automated training
python auto_train.py
```

#### Option C: Quick Test Only (NOT for production)
```bash
# Uses standard YOLO - poor accuracy for aerial views
# Already set up, just run the detection script
python yolov8_webcam.py
```

**For production drone surveillance, use Option A or B.**

---

## Usage

### Basic Usage (Webcam)
```bash
python yolov8_webcam.py
```

### Using RTSP Stream (Drone Feed)
Edit [config.py](config.py):
```python
VIDEO_SOURCE = 'rtsp://192.168.1.100:8554/live'
```

### Using Video File
Edit [config.py](config.py):
```python
VIDEO_SOURCE = 'path/to/drone_footage.mp4'
```

### Adjusting Detection Sensitivity
Edit [config.py](config.py):
```python
CONF_THRESHOLD = 0.45  # Lower = more detections, Higher = fewer false positives
```

---

## Configuration Options

All settings are in [config.py](config.py):

| Setting | Description | Default |
|---------|-------------|---------|
| `MODEL_PATH` | Path to VisDrone-trained weights | `yolov8n-visdrone.pt` |
| `CONF_THRESHOLD` | Confidence threshold (0.0-1.0) | `0.45` |
| `TARGET_CLASSES` | Classes to detect | `['person', 'car', 'motorcycle', 'truck', 'bus']` |
| `VIDEO_SOURCE` | Camera/stream/file source | `'auto'` |
| `FRAME_WIDTH` | Video frame width | `640` |
| `FRAME_HEIGHT` | Video frame height | `480` |
| `USE_API` | Enable API integration | `False` |

---

## Future Deployment Architecture

The code is structured for future API integration:

```
Drone → Camera Feed → [PC Running Detection] → API Endpoint → Your Server
```

**Current Setup (Testing):**
- Laptop camera simulates drone feed
- Local detection on PC
- API code commented out

**Production Setup:**
1. Drone sends live RTSP stream to your PC
2. PC runs detection locally
3. Detections sent to API endpoint
4. Server logs/processes surveillance data

To enable API:
1. Set `USE_API = True` in [config.py](config.py)
2. Set `API_ENDPOINT` to your server URL
3. Uncomment API code in [yolov8_webcam.py](yolov8_webcam.py)

---

## How to Stop the Program

- **Press 'q'** in the video window to quit safely
- **Ctrl+C** in terminal to force stop

---

## Requirements
- Python 3.9+
- Webcam or RTSP stream access
- ~2GB disk space for model weights

---

## Performance Notes
- **GPU**: If you have CUDA-capable GPU, detection will be faster
- **CPU**: Works fine on modern CPUs, expect 10-20 FPS
- **Resolution**: Lower resolution = faster inference

---

## Troubleshooting

### "Model file not found"
Run: `python download_model.py`

### "Could not open webcam"
- Check camera permissions in System Settings → Privacy → Camera
- Try changing `VIDEO_SOURCE` to `0`, `1`, or `2` in [config.py](config.py)

### Low accuracy / False detections
- Increase `CONF_THRESHOLD` in [config.py](config.py)
- Ensure camera angle is top-down (drone perspective)
- Check lighting conditions

### Low FPS
- Reduce `FRAME_WIDTH` and `FRAME_HEIGHT` in [config.py](config.py)
- Use GPU if available
- Use `yolov8n-visdrone.pt` (nano) instead of larger models

---

## References
- [VisDrone Dataset](http://aiskyeye.com/)
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [YOLOv8 on VisDrone](https://github.com/ultralytics/ultralytics/discussions/)

---

## License
This project uses pretrained models and is for educational/research purposes.
