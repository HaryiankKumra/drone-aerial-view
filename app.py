"""
Flask API for Aerial Drone Surveillance - FREE Deployment Ready
Receives images from camera, runs YOLOv8 detection, returns results
"""
from flask import Flask, request, jsonify, render_template, Response, send_file
from ultralytics import YOLO
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import json
import os
from storage import save_detection_event, get_recent_events, get_event_by_id, get_storage_stats, EVENTS_DIR

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

# Configuration
CONF_THRESHOLD = 0.25
TARGET_CLASSES = ['pedestrian', 'people', 'bicycle', 'car', 'van', 'truck', 'bus', 'motor']

# Object tracking to prevent duplicate alerts
tracked_objects = {}
TRACKING_THRESHOLD = 50  # pixels - objects within this distance are considered same
ALERT_COOLDOWN = 30  # seconds - minimum time between alerts for same object
import time

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
        
        # Convert annotated image to base64
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
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
        
        # Auto-save only for NEW detections
        should_save = len(new_detections) > 0
        alert_level = 'info'
        
        if should_save:
            # Save if new people detected
            people_count = sum(1 for d in new_detections if d['class'] in ['pedestrian', 'people'])
            if people_count > 5:
                alert_level = 'warning'
            elif people_count > 10:
                alert_level = 'critical'
        
        # Save event to storage
        event = None
        if should_save:
            event = save_detection_event(
                f'data:image/jpeg;base64,{img_base64}',
                new_detections,  # Only save new detections
                alert_level
            )
        
        return jsonify({
            'success': True,
            'annotated_image': f'data:image/jpeg;base64,{img_base64}',
            'detections': detections,
            'total_objects': len(detections),
            'counts': counts,
            'saved': should_save,
            'event_id': event['id'] if event else None
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

if __name__ == '__main__':
    # For local testing
    app.run(host='0.0.0.0', port=8080, debug=False)
