"""
Configuration file for aerial drone surveillance object detection
"""

# Model settings
MODEL_PATH = 'yolov8s-visdrone.pt'  # Pre-trained on VisDrone dataset for aerial/drone detection
CONF_THRESHOLD = 0.25  # Lower threshold for better detection of people and bikes
# Mac M4 Neural Engine provides good acceleration

# Classes to detect (VisDrone dataset classes)
# VisDrone classes: pedestrian, people, bicycle, car, van, truck, tricycle, awning-tricycle, bus, motor
TARGET_CLASSES = ['pedestrian', 'people', 'bicycle', 'car', 'van', 'truck', 'bus', 'motor']

# Video source
# Options:
# - 0, 1, 2, etc. for webcam index
# - 'rtsp://ip:port/stream' for RTSP drone feed
# - 'path/to/video.mp4' for video file
VIDEO_SOURCE = 'auto'  # 'auto' will find first available camera

# Camera settings
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# API settings (for future deployment)
USE_API = False  # Set to True when deploying with API
API_ENDPOINT = 'http://localhost:5000/detect'  # Your API endpoint
SEND_FRAME_INTERVAL = 1  # Send every Nth frame to API

# Display settings
SHOW_FPS = True
SHOW_CONF = True
BOX_COLOR = (0, 255, 0)  # Green
TEXT_COLOR = (0, 0, 255)  # Red
