"""
Raspberry Pi Client for Campus Guardian Drone
Captures images, runs YOLO detection, sends data to main server
"""

import cv2
import base64
import requests
import time
import json
from datetime import datetime
import os
from pathlib import Path

# Try to import GPS library (optional)
try:
    import gpsd
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False
    print("⚠️  GPS library not available. Install with: pip install gpsd-py3")

# Try to import YOLO (optional for local detection)
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️  YOLO not available. Install with: pip install ultralytics")


class RPiClient:
    def __init__(self, server_url, device_id="RPi-001", location="Campus Gate"):
        """
        Initialize Raspberry Pi client
        
        Args:
            server_url: Main server URL (e.g., http://your-ec2-ip:8080 or https://yourdomain.com)
            device_id: Unique ID for this RPi
            location: Physical location description
        """
        self.server_url = server_url.rstrip('/')
        self.device_id = device_id
        self.location = location
        self.model = None
        self.camera = None
        self.gps_connected = False
        
        # Configuration
        self.config = {
            'camera_index': 0,  # Default camera
            'capture_interval': 5,  # Capture every 5 seconds
            'image_width': 640,
            'image_height': 480,
            'jpeg_quality': 80,  # Lower quality = smaller upload size
            'local_detection': False,  # Set True to run YOLO on RPi
            'model_path': 'yolov8n.pt',  # Lightweight model for RPi
            'conf_threshold': 0.25,
            'send_only_detections': False,  # Set True to only send when objects detected
        }
        
        print(f"🚁 Raspberry Pi Client Initialized")
        print(f"   Device ID: {self.device_id}")
        print(f"   Location: {self.location}")
        print(f"   Server: {self.server_url}")
        
    def initialize_camera(self):
        """Initialize camera"""
        try:
            self.camera = cv2.VideoCapture(self.config['camera_index'])
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['image_width'])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['image_height'])
            
            # Test capture
            ret, frame = self.camera.read()
            if ret:
                print("✅ Camera initialized successfully")
                return True
            else:
                print("❌ Camera failed to capture frame")
                return False
        except Exception as e:
            print(f"❌ Camera initialization failed: {e}")
            return False
    
    def initialize_gps(self):
        """Initialize GPS connection"""
        if not GPS_AVAILABLE:
            print("⚠️  GPS not available")
            return False
        
        try:
            gpsd.connect()
            packet = gpsd.get_current()
            if packet.mode >= 2:  # 2D fix or better
                print(f"✅ GPS initialized: {packet.lat}, {packet.lon}")
                self.gps_connected = True
                return True
            else:
                print("⚠️  GPS no fix")
                return False
        except Exception as e:
            print(f"❌ GPS initialization failed: {e}")
            return False
    
    def initialize_model(self):
        """Initialize YOLO model for local detection"""
        if not YOLO_AVAILABLE:
            print("⚠️  YOLO not available for local detection")
            return False
        
        if not self.config['local_detection']:
            print("ℹ️  Local detection disabled")
            return False
        
        try:
            print(f"Loading YOLO model: {self.config['model_path']}...")
            self.model = YOLO(self.config['model_path'])
            print("✅ YOLO model loaded")
            return True
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            return False
    
    def get_gps_data(self):
        """Get current GPS coordinates and speed"""
        if not self.gps_connected:
            return None, None, None
        
        try:
            packet = gpsd.get_current()
            if packet.mode >= 2:
                return packet.lat, packet.lon, packet.hspeed
            return None, None, None
        except Exception as e:
            print(f"⚠️  GPS error: {e}")
            return None, None, None
    
    def capture_image(self):
        """Capture image from camera"""
        if not self.camera:
            return None
        
        ret, frame = self.camera.read()
        if ret:
            return frame
        return None
    
    def encode_image(self, frame):
        """Encode image to base64 JPEG"""
        try:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.config['jpeg_quality']]
            result, encoded_img = cv2.imencode('.jpg', frame, encode_param)
            if result:
                img_base64 = base64.b64encode(encoded_img).decode('utf-8')
                return f"data:image/jpeg;base64,{img_base64}"
            return None
        except Exception as e:
            print(f"❌ Image encoding failed: {e}")
            return None
    
    def run_local_detection(self, frame):
        """Run YOLO detection on RPi (optional)"""
        if not self.model:
            return []
        
        try:
            results = self.model(frame, conf=self.config['conf_threshold'])
            detections = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    detections.append({
                        'class': result.names[int(box.cls)],
                        'confidence': float(box.conf),
                        'bbox': box.xyxy[0].tolist()
                    })
            
            return detections
        except Exception as e:
            print(f"❌ Local detection failed: {e}")
            return []
    
    def send_to_server(self, image_data, gps_lat=None, gps_lon=None, speed=None, detections=None):
        """Send data to main server"""
        try:
            payload = {
                'device_id': self.device_id,
                'location': self.location,
                'timestamp': datetime.now().isoformat(),
                'image': image_data,
                'camera_ok': True,
                'model_ok': self.model is not None
            }
            
            # Add GPS data if available
            if gps_lat is not None and gps_lon is not None:
                payload['gps_latitude'] = gps_lat
                payload['gps_longitude'] = gps_lon
            
            if speed is not None:
                payload['speed'] = speed
            
            # Add local detections if available
            if detections:
                payload['local_detections'] = detections
            
            # Send to server
            response = requests.post(
                f"{self.server_url}/rpi/detect",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Data sent successfully | Objects: {data.get('total_objects', 0)}")
                    return True
                else:
                    print(f"⚠️  Server rejected data: {data.get('error', 'Unknown')}")
                    return False
            else:
                print(f"❌ Server error: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ Request timeout")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - is server running?")
            return False
        except Exception as e:
            print(f"❌ Send failed: {e}")
            return False
    
    def run(self):
        """Main loop - capture and send data continuously"""
        print("\n" + "="*60)
        print("🚀 Starting Raspberry Pi Client")
        print("="*60 + "\n")
        
        # Initialize components
        camera_ok = self.initialize_camera()
        if not camera_ok:
            print("❌ Cannot run without camera!")
            return
        
        gps_ok = self.initialize_gps()
        model_ok = self.initialize_model()
        
        print(f"\n{'='*60}")
        print("📊 System Status:")
        print(f"   Camera: {'✅' if camera_ok else '❌'}")
        print(f"   GPS: {'✅' if gps_ok else '❌'}")
        print(f"   Local Detection: {'✅' if model_ok else '❌'}")
        print(f"{'='*60}\n")
        
        # Test server connection
        print("🔍 Testing server connection...")
        try:
            response = requests.get(f"{self.server_url}/system_status", timeout=5)
            if response.status_code == 200:
                print("✅ Server is reachable")
            else:
                print(f"⚠️  Server returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Cannot reach server: {e}")
            print("⚠️  Continuing anyway (will retry each capture)...")
        
        print(f"\n🔄 Starting capture loop (every {self.config['capture_interval']}s)")
        print("Press Ctrl+C to stop\n")
        
        frame_count = 0
        success_count = 0
        fail_count = 0
        
        try:
            while True:
                frame_count += 1
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"\n[{timestamp}] Frame #{frame_count}")
                
                # Capture image
                frame = self.capture_image()
                if frame is None:
                    print("❌ Camera capture failed")
                    fail_count += 1
                    time.sleep(self.config['capture_interval'])
                    continue
                
                # Get GPS data
                gps_lat, gps_lon, speed = self.get_gps_data()
                if gps_lat:
                    print(f"📍 GPS: {gps_lat:.5f}, {gps_lon:.5f} | Speed: {speed:.1f} m/s")
                else:
                    print("📍 GPS: Not available")
                
                # Run local detection (optional)
                detections = None
                if self.config['local_detection'] and self.model:
                    detections = self.run_local_detection(frame)
                    print(f"🔍 Local detections: {len(detections)} objects")
                    
                    # Skip sending if no detections and config says so
                    if self.config['send_only_detections'] and len(detections) == 0:
                        print("⏭️  Skipping (no detections)")
                        time.sleep(self.config['capture_interval'])
                        continue
                
                # Encode image
                image_data = self.encode_image(frame)
                if not image_data:
                    print("❌ Image encoding failed")
                    fail_count += 1
                    time.sleep(self.config['capture_interval'])
                    continue
                
                print(f"📸 Image size: {len(image_data) / 1024:.1f} KB")
                
                # Send to server
                success = self.send_to_server(
                    image_data=image_data,
                    gps_lat=gps_lat,
                    gps_lon=gps_lon,
                    speed=speed,
                    detections=detections
                )
                
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                
                print(f"📊 Stats: {success_count} success | {fail_count} failed")
                
                # Wait before next capture
                time.sleep(self.config['capture_interval'])
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopped by user")
        finally:
            # Cleanup
            if self.camera:
                self.camera.release()
            print(f"\n{'='*60}")
            print(f"📊 Final Stats:")
            print(f"   Total frames: {frame_count}")
            print(f"   Successful: {success_count}")
            print(f"   Failed: {fail_count}")
            print(f"   Success rate: {success_count/max(frame_count,1)*100:.1f}%")
            print(f"{'='*60}\n")
            print("✅ Cleanup complete")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Raspberry Pi Client for Campus Guardian Drone')
    parser.add_argument('--server', type=str, required=True, 
                       help='Server URL (e.g., http://your-ec2-ip:8080)')
    parser.add_argument('--device-id', type=str, default='RPi-001',
                       help='Unique device ID (default: RPi-001)')
    parser.add_argument('--location', type=str, default='Campus Gate',
                       help='Physical location (default: Campus Gate)')
    parser.add_argument('--interval', type=int, default=5,
                       help='Capture interval in seconds (default: 5)')
    parser.add_argument('--local-detection', action='store_true',
                       help='Enable local YOLO detection on RPi')
    parser.add_argument('--send-only-detections', action='store_true',
                       help='Only send frames with detected objects')
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera index (default: 0)')
    
    args = parser.parse_args()
    
    # Create client
    client = RPiClient(
        server_url=args.server,
        device_id=args.device_id,
        location=args.location
    )
    
    # Update configuration
    client.config['capture_interval'] = args.interval
    client.config['local_detection'] = args.local_detection
    client.config['send_only_detections'] = args.send_only_detections
    client.config['camera_index'] = args.camera
    
    # Run
    client.run()


if __name__ == "__main__":
    main()
