"""
Flask API for Campus Guardian Drone - Aerial Surveillance System
Modular architecture supporting multiple video sources and drone telemetry
"""
import os
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed - using system environment variables only")

from flask import Flask, request, jsonify, render_template, Response, send_file
from ultralytics import YOLO
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import json
from storage import save_detection_event, get_recent_events, get_event_by_id, get_storage_stats, EVENTS_DIR
from csv_logger import event_logger

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from telemetry.drone_state import DroneState
from event_engine import EventEngine, TelegramBot
from geofencing import ZoneManager, ViolationDetector, ViolationLogger, ReturnToHome

app = Flask(__name__)

def calculate_center(bbox):
    """Calculate center point of bounding box"""
    return ((bbox['x1'] + bbox['x2']) / 2, (bbox['y1'] + bbox['y2']) / 2)

def get_distance(point1, point2):
    """Calculate Euclidean distance between two points"""
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5

def is_same_object(bbox1, bbox2, class1, class2):
    """Check if two detections are the same object"""
    if class1 != class2:
        return False
    center1 = calculate_center(bbox1)
    center2 = calculate_center(bbox2)
    return get_distance(center1, center2) < TRACKING_THRESHOLD

# Load model once at startup
print("Loading YOLOv8-VisDrone model...")
model = YOLO('yolov8s-visdrone.pt')
print("Model loaded successfully!")

# Initialize drone state (simulated telemetry)
# TODO: Replace with real coordinates for your campus
drone_state = DroneState(start_location=(30.3560, 76.3649))
print(f"🚁 Drone telemetry initialized")

# Initialize Event Engine (Phase-2)
event_engine = EventEngine(db_path='data/events.db')
telegram_bot = TelegramBot()
print(f"🎯 Event engine initialized")

# Test Telegram connection
if telegram_bot.enabled:
    success, message = telegram_bot.test_connection()
    if success:
        print(f"📱 Telegram: {message}")
    else:
        print(f"⚠️  Telegram: {message}")

# Initialize Geofencing System (Phase-3)
zone_manager = ZoneManager(db_path='data/zones.db')
violation_detector = ViolationDetector(zone_manager)
violation_logger = ViolationLogger(db_path='data/violations.db')
rth_system = ReturnToHome(home_lat=30.3560, home_lon=76.3649)
print(f"🛡️  Geofencing system initialized")


# Configuration
CONF_THRESHOLD = 0.25
TARGET_CLASSES = ['pedestrian', 'people', 'bicycle', 'car', 'van', 'truck', 'bus', 'motor']

# Object tracking to prevent duplicate alerts
tracked_objects = {}
TRACKING_THRESHOLD = 50  # pixels - objects within this distance are considered same
ALERT_COOLDOWN = 30  # seconds - minimum time between alerts for same object
import time

# FPS tracking
last_request_time = None
fps_value = 0.0

# Auto-photo cooldown (3 seconds between photos)
last_photo_time = 0
PHOTO_COOLDOWN = 3  # seconds between auto-photos (changed from 5 to 3)

# Cumulative statistics
cumulative_stats = {
    'total_people': 0,
    'total_vehicles': 0,
    'total_detections': 0
}

@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': 'yolov8s-visdrone',
        'classes': TARGET_CLASSES
    })

@app.route('/telemetry', methods=['GET'])
def get_telemetry():
    """Get current drone telemetry data with zone violation status"""
    telemetry = drone_state.get_telemetry()
    
    # Check for zone violations
    violation_result = violation_detector.check_position(
        telemetry['latitude'],
        telemetry['longitude'],
        telemetry['altitude']
    )
    
    # Add violation info to telemetry
    telemetry['violation'] = violation_result['violation']
    telemetry['violation_severity'] = violation_result['severity']
    telemetry['violation_message'] = violation_result['message']
    
    # Add RTH status
    telemetry['rth_active'] = rth_system.rth_active
    
    return jsonify(telemetry)

@app.route('/hud', methods=['GET'])
def get_hud():
    """Get HUD overlay data for display"""
    return jsonify(drone_state.get_hud_data())

@app.route('/system_status', methods=['GET'])
def system_status():
    """Get overall system health status"""
    return jsonify({
        'camera': 'OK',  # Will be 'ERROR' if video source fails
        'model': 'RUNNING',
        'server': 'ONLINE',
        'gps': 'LOCK' if drone_state.gps_lock else 'NO LOCK',
        'battery': drone_state.battery,
        'status': drone_state.status
    })

@app.route('/update_location', methods=['POST'])
def update_location():
    """Update drone base location from browser geolocation with violation checking"""
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if latitude is not None and longitude is not None:
        drone_state.update_location(latitude, longitude)
        
        # Check for zone violations
        telemetry = drone_state.get_telemetry()
        violation_result = violation_detector.check_position(
            latitude, 
            longitude, 
            telemetry['altitude']
        )
        
        # If violation detected, log it and trigger RTH if critical
        if violation_result['violation']:
            # Log the violation
            violation_id = violation_logger.log_violation(
                zone=violation_result['zone'],
                violation_type=violation_result['violation_type'],
                severity=violation_result['severity'],
                drone_lat=latitude,
                drone_lon=longitude,
                drone_altitude=telemetry['altitude'],
                action_taken='RTH_TRIGGERED' if violation_result['severity'] == 'CRITICAL' else 'ALERT_SENT'
            )
            
            # Trigger RTH on critical violations (no-fly zones)
            if violation_detector.should_trigger_rth(violation_result) and not rth_system.rth_active:
                rth_info = rth_system.trigger_rth(
                    current_lat=latitude,
                    current_lon=longitude,
                    reason=ReturnToHome.REASON_NO_FLY_VIOLATION,
                    emergency=True
                )
                drone_state.status = 'RETURNING_HOME'
                print(f"🚨 CRITICAL VIOLATION - RTH TRIGGERED: {violation_result['message']}")
                
                # Send Telegram alert for critical violations
                if telegram_bot.enabled:
                    alert_message = f"🚨 <b>CRITICAL VIOLATION</b>\n\n{violation_result['message']}\n\nRTH ACTIVATED"
                    telegram_bot.send_alert(alert_message, severity='CRITICAL')
        
        return jsonify({
            'success': True, 
            'latitude': latitude, 
            'longitude': longitude,
            'violation': violation_result
        })
    return jsonify({'success': False, 'error': 'Missing latitude or longitude'}), 400

@app.route('/update_temperature', methods=['POST'])
def update_temperature():
    """Update temperature from browser/weather API"""
    data = request.get_json()
    temperature = data.get('temperature')
    
    if temperature is not None:
        drone_state.update_temperature(temperature)
        return jsonify({'success': True, 'temperature': temperature})
    return jsonify({'success': False, 'error': 'Missing temperature'}), 400

@app.route('/set_patrol_pattern', methods=['POST'])
def set_patrol_pattern():
    """Set patrol pattern (diamond or circle)"""
    data = request.get_json()
    pattern = data.get('pattern', 'diamond')
    
    drone_state.set_patrol_pattern(pattern)
    return jsonify({'success': True, 'pattern': pattern})

# ============================================================================
# RASPBERRY PI EDGE DEVICE ENDPOINTS
# ============================================================================

@app.route('/rpi/detect', methods=['POST'])
def rpi_detect():
    """
    Raspberry Pi edge device detection endpoint
    Accepts frames from remote Pi cameras for centralized detection
    """
    try:
        data = request.get_json()
        
        # Extract device info
        device_id = data.get('device_id', 'UNKNOWN')
        location = data.get('location', 'Unknown Location')
        timestamp = data.get('timestamp')
        
        # Handle base64 image
        image_data = base64.b64decode(data['image'].split(',')[1] if ',' in data['image'] else data['image'])
        image = Image.open(BytesIO(image_data))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Run detection
        results = model(frame, conf=CONF_THRESHOLD, verbose=False)[0]
        
        # Process detections
        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]
            
            if class_name in TARGET_CLASSES:
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                detections.append({
                    'class': class_name,
                    'confidence': round(conf, 2),
                    'bbox': {
                        'x1': int(x1),
                        'y1': int(y1),
                        'x2': int(x2),
                        'y2': int(y2)
                    }
                })
        
        print(f"📡 RPi {device_id} @ {location}: {len(detections)} detections")
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'location': location,
            'detections': detections,
            'total_objects': len(detections)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/rpi/register', methods=['POST'])
def rpi_register():
    """Register a new Raspberry Pi device"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        location = data.get('location')
        
        # TODO: Store device info in database
        
        print(f"📱 New RPi registered: {device_id} @ {location}")
        
        return jsonify({
            'success': True,
            'message': 'Device registered successfully',
            'device_id': device_id,
            'server_time': time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/detect', methods=['POST'])
def detect():
    """
    Main detection endpoint
    Accepts: JSON with base64 encoded image or multipart/form-data with image file
    Returns: JSON with detections
    """
    try:
        # Handle base64 image from JSON
        if request.is_json:
            data = request.get_json()
            image_data = base64.b64decode(data['image'].split(',')[1] if ',' in data['image'] else data['image'])
            image = Image.open(BytesIO(image_data))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Handle file upload
        elif 'image' in request.files:
            file = request.files['image']
            image = Image.open(file.stream)
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        else:
            return jsonify({'error': 'No image provided'}), 400

        # Run detection
        results = model(frame, conf=CONF_THRESHOLD, verbose=False)[0]
        
        # Process detections
        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]
            
            # Filter by target classes
            if class_name in TARGET_CLASSES:
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                detections.append({
                    'class': class_name,
                    'confidence': round(conf, 2),
                    'bbox': {
                        'x1': int(x1),
                        'y1': int(y1),
                        'x2': int(x2),
                        'y2': int(y2)
                    }
                })
        
        # Count objects by class
        counts = {}
        for det in detections:
            counts[det['class']] = counts.get(det['class'], 0) + 1
        
        return jsonify({
            'success': True,
            'detections': detections,
            'total_objects': len(detections),
            'counts': counts,
            'image_size': {
                'width': frame.shape[1],
                'height': frame.shape[0]
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/detect_annotated', methods=['POST'])
def detect_annotated():
    """
    Detection endpoint that returns annotated image
    Returns: JSON with base64 encoded annotated image and detections
    """
    global last_request_time, fps_value, last_photo_time, cumulative_stats, video_recording
    
    # Calculate FPS
    current_time = time.time()
    if last_request_time is not None:
        time_diff = current_time - last_request_time
        if time_diff > 0:
            fps_value = 1.0 / time_diff
    last_request_time = current_time
    
    try:
        # Handle base64 image
        if request.is_json:
            data = request.get_json()
            image_data = base64.b64decode(data['image'].split(',')[1] if ',' in data['image'] else data['image'])
            image = Image.open(BytesIO(image_data))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Handle file upload
        elif 'image' in request.files:
            file = request.files['image']
            image = Image.open(file.stream)
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        else:
            return jsonify({'error': 'No image provided'}), 400

        # Run detection
        results = model(frame, conf=CONF_THRESHOLD, verbose=False)[0]
        
        # Draw annotations
        annotated_frame = frame.copy()
        detections = []
        
        for box in results.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]
            
            if class_name in TARGET_CLASSES:
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                
                # Draw bounding box
                color = (0, 255, 0)  # Green
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label = f'{class_name}: {conf:.2f}'
                cv2.putText(annotated_frame, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                detections.append({
                    'class': class_name,
                    'confidence': round(conf, 2),
                    'bbox': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
                })
        
        # Convert annotated image to base64 (for dashboard display)
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # If recording, add RAW frame (WITHOUT annotations) to video
        global video_recording, video_frames
        if video_recording:
            video_frames.append(frame.copy())  # Save original frame without green boxes
        
        # Count objects
        counts = {}
        for det in detections:
            counts[det['class']] = counts.get(det['class'], 0) + 1
        
        # Track objects and prevent duplicate alerts for stationary objects
        current_time = time.time()
        new_detections = []
        
        for detection in detections:
            is_new = True
            detection_key = f"{detection['class']}_{detection['bbox']['x1']}_{detection['bbox']['y1']}"
            
            # Check if this is same as any tracked object
            for tracked_key, tracked_data in list(tracked_objects.items()):
                if is_same_object(detection['bbox'], tracked_data['bbox'], 
                                detection['class'], tracked_data['class']):
                    # Same object - check cooldown
                    if current_time - tracked_data['last_alert'] < ALERT_COOLDOWN:
                        is_new = False
                    else:
                        # Update alert time
                        tracked_objects[tracked_key]['last_alert'] = current_time
                        is_new = True
                    break
            
            if is_new:
                new_detections.append(detection)
                # Add to tracked objects
                tracked_objects[detection_key] = {
                    'bbox': detection['bbox'],
                    'class': detection['class'],
                    'last_alert': current_time,
                    'first_seen': current_time
                }
        
        # Clean up old tracked objects (not seen for 60 seconds)
        for key in list(tracked_objects.keys()):
            if current_time - tracked_objects[key]['last_alert'] > 60:
                del tracked_objects[key]
        
        # Update cumulative statistics
        global cumulative_stats
        current_people = sum(1 for d in detections if d['class'] in ['pedestrian', 'people'])
        current_vehicles = sum(1 for d in detections if d['class'] in ['car', 'van', 'truck', 'bus', 'motor', 'bicycle'])
        
        # Add new detections to cumulative totals
        if len(new_detections) > 0:
            new_people = sum(1 for d in new_detections if d['class'] in ['pedestrian', 'people'])
            new_vehicles = sum(1 for d in new_detections if d['class'] in ['car', 'van', 'truck', 'bus', 'motor', 'bicycle'])
            cumulative_stats['total_people'] += new_people
            cumulative_stats['total_vehicles'] += new_vehicles
            cumulative_stats['total_detections'] += len(new_detections)
        
        # Auto-photo: Save only if NOT recording AND 3+ seconds since last photo AND has new detections
        should_save_photo = False
        event = None
        alert_level = 'info'
        event_ids = []  # Track created events
        
        if not video_recording and len(new_detections) > 0:
            if (current_time - last_photo_time) >= PHOTO_COOLDOWN:
                should_save_photo = True
                last_photo_time = current_time
                
                # Determine alert level
                people_count = sum(1 for d in new_detections if d['class'] in ['pedestrian', 'people'])
                if people_count > 10:
                    alert_level = 'critical'
                elif people_count > 5:
                    alert_level = 'warning'
                
                # Save photo to Cloudinary
                event = save_detection_event(
                    f'data:image/jpeg;base64,{img_base64}',
                    new_detections,
                    alert_level
                )
                
                # Log to CSV
                event_logger.log_detection(detections, alert_level)
                
                # PHASE-2: Process through Event Engine
                telemetry = drone_state.get_telemetry()
                for detection in new_detections:
                    detection_data = {
                        'class': detection['class'],
                        'confidence': detection['confidence'],
                        'bbox': detection['bbox'],
                        'snapshot_url': event.get('url') if event else None,
                        'snapshot_path': event.get('id') if event else None,
                        'drone_lat': telemetry['latitude'],
                        'drone_lon': telemetry['longitude'],
                        'zone': 'Campus Area'  # TODO: Add geofencing in Phase-3
                    }
                    
                    # Process detection (creates event if 5-second rule met)
                    event_id = event_engine.process_detection(detection_data)
                    
                    if event_id:
                        event_ids.append(event_id)
                        print(f"🎯 Event created: {event_id}")
                        
                        # Check if alert should be sent
                        if event_engine.should_alert(event_id):
                            event_details = event_engine.get_event_details(event_id)
                            
                            # Send Telegram alert
                            if telegram_bot.send_alert(event_details):
                                event_engine.log_alert_sent(
                                    event_id, 
                                    'telegram', 
                                    'security_team'
                                )

        
        return jsonify({
            'success': True,
            'annotated_image': f'data:image/jpeg;base64,{img_base64}',
            'detections': detections,
            'total_objects': len(detections),
            'counts': counts,
            'current_people': current_people,
            'current_vehicles': current_vehicles,
            'cumulative_people': cumulative_stats['total_people'],
            'cumulative_vehicles': cumulative_stats['total_vehicles'],
            'cumulative_total': cumulative_stats['total_detections'],
            'photo_saved': should_save_photo,
            'recording': video_recording,
            'event_id': event['id'] if event else None,
            'security_events': event_ids,  # New: Event engine event IDs
            'fps': round(fps_value, 1)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/events', methods=['GET'])
def get_events():
    """Get recent saved events"""
    limit = request.args.get('limit', 50, type=int)
    events = get_recent_events(limit)
    return jsonify({
        'success': True,
        'events': events,
        'total': len(events)
    })

@app.route('/event/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get specific event details"""
    event = get_event_by_id(event_id)
    if event:
        return jsonify({
            'success': True,
            'event': event
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Event not found'
        }), 404

@app.route('/event/<event_id>/image', methods=['GET'])
def get_event_image(event_id):
    """Get event image file"""
    event = get_event_by_id(event_id)
    if event:
        image_path = os.path.join(EVENTS_DIR, event['image'])
        if os.path.exists(image_path):
            return send_file(image_path, mimetype='image/jpeg')
    return jsonify({'error': 'Image not found'}), 404

@app.route('/storage/stats', methods=['GET'])
def storage_stats():
    """Get storage statistics"""
    stats = get_storage_stats()
    return jsonify({
        'success': True,
        'stats': stats
    })

@app.route('/record_snapshot', methods=['POST'])
def record_snapshot():
    """Manually save current frame"""
    try:
        # Handle base64 image
        if request.is_json:
            data = request.get_json()
            image_data = base64.b64decode(data['image'].split(',')[1] if ',' in data['image'] else data['image'])
            image = Image.open(BytesIO(image_data))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            return jsonify({'error': 'No image provided'}), 400

        # Run detection
        results = model(frame, conf=CONF_THRESHOLD, verbose=False)[0]
        
        # Draw annotations
        annotated_frame = frame.copy()
        detections = []
        
        for box in results.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]
            
            if class_name in TARGET_CLASSES:
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                
                color = (0, 255, 0)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                label = f'{class_name}: {conf:.2f}'
                cv2.putText(annotated_frame, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                detections.append({
                    'class': class_name,
                    'confidence': round(conf, 2),
                    'bbox': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
                })
        
        # Convert to base64
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Force save (manual recording)
        event = save_detection_event(
            f'data:image/jpeg;base64,{img_base64}',
            detections,
            'manual'
        )
        
        return jsonify({
            'success': True,
            'message': 'Snapshot saved',
            'event_id': event['id'] if event else None
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Video recording state
video_writer = None
video_recording = False
video_filename = None
video_frames = []  # For RAW frames (without annotations)
video_frames_annotated = []  # For dashboard display (with green boxes)

@app.route('/start_recording', methods=['POST'])
def start_recording():
    """Start recording live video"""
    global video_recording, video_filename, video_frames
    
    try:
        # Auto-reset if recording flag is set but no frames exist (error recovery)
        if video_recording and len(video_frames) == 0:
            print("⚠️  Resetting stale recording state")
            video_recording = False
        
        if video_recording:
            return jsonify({
                'success': False,
                'error': 'Recording already in progress'
            }), 400
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        video_filename = os.path.join(EVENTS_DIR, f'recording_{timestamp}.mp4')
        video_recording = True
        video_frames = []
        
        # Log to CSV
        event_logger.log_custom_event('RECORDING_START', f'Video recording started: {video_filename}')
        
        return jsonify({
            'success': True,
            'message': 'Recording started',
            'filename': video_filename
        })
    
    except Exception as e:
        video_recording = False  # Reset on error
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    """Stop recording and save video (RAW - no annotations)"""
    global video_recording, video_filename, video_frames, video_writer
    
    try:
        if not video_recording:
            return jsonify({
                'success': False,
                'error': 'No recording in progress'
            }), 400
        
        video_recording = False
        
        if len(video_frames) == 0:
            return jsonify({
                'success': False,
                'error': 'No frames captured'
            }), 400
        
        # Save RAW video file (without green boxes)
        height, width = video_frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_filename, fourcc, 10.0, (width, height))
        
        for frame in video_frames:
            out.write(frame)
        
        out.release()
        frames_count = len(video_frames)
        video_frames = []
        
        # Upload to Cloudinary
        from cloudinary_storage import upload_video
        cloud_url = None
        
        try:
            cloud_result = upload_video(video_filename, f'recording_{time.strftime("%Y%m%d_%H%M%S")}')
            if cloud_result:
                cloud_url = cloud_result['secure_url']
                print(f"✅ Video uploaded to Cloudinary: {cloud_url}")
        except Exception as e:
            print(f"⚠️  Could not upload video to Cloudinary: {e}")
        
        file_size = os.path.getsize(video_filename)
        
        # Log to CSV
        event_logger.log_custom_event(
            'RECORDING_STOP',
            f'Video saved: {frames_count} frames, {file_size} bytes, Cloud: {cloud_url}'
        )
        
        # Upload CSV log to Cloudinary
        csv_url = event_logger.upload_to_cloudinary()
        
        return jsonify({
            'success': True,
            'message': 'Recording saved',
            'filename': video_filename,
            'frames': frames_count,
            'size': file_size,
            'cloudinary_url': cloud_url,
            'csv_url': csv_url
        })
    
    except Exception as e:
        video_recording = False
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/recording_status', methods=['GET'])
def recording_status():
    """Get current recording status"""
    return jsonify({
        'recording': video_recording,
        'frames': len(video_frames),
        'filename': video_filename if video_recording else None
    })

@app.route('/reset_recording', methods=['POST'])
def reset_recording():
    """Reset recording state (emergency recovery)"""
    global video_recording, video_filename, video_frames
    
    video_recording = False
    video_filename = None
    video_frames = []
    
    return jsonify({
        'success': True,
        'message': 'Recording state reset'
    })

@app.route('/download_csv', methods=['GET'])
def download_csv():
    """Download current CSV event log"""
    try:
        csv_file = event_logger.get_current_log_file()
        if os.path.exists(csv_file):
            return send_file(
                csv_file,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'events_{time.strftime("%Y%m%d_%H%M%S")}.csv'
            )
        else:
            return jsonify({'error': 'No log file found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/csv_status', methods=['GET'])
def csv_status():
    """Get CSV log status"""
    try:
        csv_file = event_logger.get_current_log_file()
        if os.path.exists(csv_file):
            file_size = os.path.getsize(csv_file)
            # Count lines
            with open(csv_file, 'r') as f:
                line_count = sum(1 for _ in f) - 1  # Subtract header
            
            return jsonify({
                'success': True,
                'file': csv_file,
                'size': file_size,
                'events': line_count
            })
        else:
            return jsonify({'error': 'No log file'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PHASE-2: EVENT ENGINE ENDPOINTS
# ============================================================================

@app.route('/security/events', methods=['GET'])
def get_security_events():
    """Get recent security events from event engine"""
    try:
        limit = request.args.get('limit', 50, type=int)
        severity = request.args.get('severity', None, type=str)
        
        events = event_engine.get_recent_events(limit, severity)
        
        return jsonify({
            'success': True,
            'events': events,
            'total': len(events)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/security/event/<event_id>', methods=['GET'])
def get_security_event_details(event_id):
    """Get specific security event details"""
    try:
        event = event_engine.get_event_details(event_id)
        
        if event:
            return jsonify({
                'success': True,
                'event': event
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/security/stats', methods=['GET'])
def get_security_stats():
    """Get security event statistics"""
    try:
        stats = event_engine.get_statistics()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/security/telegram/test', methods=['GET'])
def test_telegram():
    """Test Telegram bot connection"""
    try:
        success, message = telegram_bot.test_connection()
        
        return jsonify({
            'success': success,
            'message': message,
            'enabled': telegram_bot.enabled
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== GEOFENCING ENDPOINTS (Phase-3) ====================

@app.route('/zones/create', methods=['POST'])
def create_zone():
    """Create a new geofencing zone"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['name', 'zone_type', 'polygon_coords']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        zone_id = zone_manager.create_zone(
            name=data['name'],
            zone_type=data['zone_type'],
            polygon_coords=data['polygon_coords'],
            description=data.get('description', ''),
            max_altitude=data.get('max_altitude', 100.0),
            alert_on_entry=data.get('alert_on_entry', True)
        )
        
        return jsonify({
            'success': True,
            'zone_id': zone_id,
            'message': f'Zone "{data["name"]}" created successfully'
        })
    
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/zones', methods=['GET'])
def get_zones():
    """Get all zones"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        zones = zone_manager.get_all_zones(active_only=active_only)
        
        return jsonify({
            'success': True,
            'zones': zones,
            'count': len(zones)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/zones/<int:zone_id>', methods=['GET'])
def get_zone(zone_id):
    """Get a specific zone by ID"""
    try:
        zone = zone_manager.get_zone_by_id(zone_id)
        
        if not zone:
            return jsonify({'success': False, 'error': 'Zone not found'}), 404
        
        return jsonify({
            'success': True,
            'zone': zone
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/zones/<int:zone_id>', methods=['DELETE'])
def delete_zone(zone_id):
    """Delete a zone (soft delete)"""
    try:
        permanent = request.args.get('permanent', 'false').lower() == 'true'
        
        if permanent:
            success = zone_manager.permanently_delete_zone(zone_id)
        else:
            success = zone_manager.delete_zone(zone_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Zone {zone_id} deleted'
            })
        else:
            return jsonify({'success': False, 'error': 'Zone not found'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/zones/stats', methods=['GET'])
def get_zone_stats():
    """Get zone statistics"""
    try:
        stats = zone_manager.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/zones/check', methods=['POST'])
def check_zone_violation():
    """Check if a position violates any zones"""
    try:
        data = request.get_json()
        lat = data.get('latitude')
        lon = data.get('longitude')
        altitude = data.get('altitude', 2.0)
        
        if lat is None or lon is None:
            return jsonify({'success': False, 'error': 'Missing latitude/longitude'}), 400
        
        # Check for violations
        violation_result = violation_detector.check_position(lat, lon, altitude)
        
        # Get zones containing point
        containing_zones = zone_manager.get_zones_containing_point(lat, lon)
        
        return jsonify({
            'success': True,
            'violation': violation_result['violation'],
            'violation_info': violation_result,
            'containing_zones': containing_zones
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/violations', methods=['GET'])
def get_violations():
    """Get recent violations"""
    try:
        limit = int(request.args.get('limit', 50))
        severity = request.args.get('severity')
        
        if severity:
            violations = violation_logger.get_violations_by_severity(severity)
        else:
            violations = violation_logger.get_recent_violations(limit)
        
        return jsonify({
            'success': True,
            'violations': violations,
            'count': len(violations)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/violations/stats', methods=['GET'])
def get_violation_stats():
    """Get violation statistics"""
    try:
        stats = violation_logger.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/rth/trigger', methods=['POST'])
def trigger_rth():
    """Trigger return-to-home"""
    try:
        data = request.get_json()
        reason = data.get('reason', 'manual')
        emergency = data.get('emergency', False)
        
        # Get current drone position
        telemetry = drone_state.get_telemetry()
        
        rth_info = rth_system.trigger_rth(
            current_lat=telemetry['latitude'],
            current_lon=telemetry['longitude'],
            reason=reason,
            emergency=emergency
        )
        
        # Update drone state to RETURNING_HOME
        drone_state.status = 'RETURNING_HOME'
        
        return jsonify({
            'success': True,
            'message': f'RTH triggered: {reason}',
            'rth_info': rth_info
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/rth/cancel', methods=['POST'])
def cancel_rth():
    """Cancel return-to-home"""
    try:
        rth_system.cancel_rth()
        
        # Resume normal patrol
        drone_state.status = 'PATROLLING'
        
        return jsonify({
            'success': True,
            'message': 'RTH cancelled'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/rth/status', methods=['GET'])
def get_rth_status():
    """Get RTH status"""
    try:
        # Get current position
        telemetry = drone_state.get_telemetry()
        
        status = rth_system.get_status(
            current_lat=telemetry['latitude'],
            current_lon=telemetry['longitude']
        )
        
        return jsonify({
            'success': True,
            'rth_status': status
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Log system start
    event_logger.log_custom_event('SYSTEM_START', 'Campus Guardian Drone system started')
    
    # For local testing
    app.run(host='0.0.0.0', port=8080, debug=False)
