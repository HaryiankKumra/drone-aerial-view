"""
Event Recording and Storage Module
Saves images when motion/objects detected
"""
import os
import json
from datetime import datetime
import cv2
import base64
import numpy as np

# Storage directories
RECORDINGS_DIR = 'recordings'
EVENTS_DIR = os.path.join(RECORDINGS_DIR, 'events')
METADATA_FILE = os.path.join(RECORDINGS_DIR, 'events.json')

# Create directories
os.makedirs(EVENTS_DIR, exist_ok=True)

def save_detection_event(image_base64, detections, alert_level='info'):
    """
    Save detected frame with metadata
    
    Args:
        image_base64: Base64 encoded image
        detections: Detection results from YOLOv8
        alert_level: 'critical', 'warning', or 'info'
    
    Returns:
        dict: Event metadata
    """
    timestamp = datetime.now()
    event_id = timestamp.strftime('%Y%m%d_%H%M%S_%f')
    
    # Decode and save image
    if ',' in image_base64:
        image_base64 = image_base64.split(',')[1]
    
    img_data = base64.b64decode(image_base64)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Save image
    image_filename = f'{event_id}.jpg'
    image_path = os.path.join(EVENTS_DIR, image_filename)
    cv2.imwrite(image_path, img)
    
    # Create event metadata
    event = {
        'id': event_id,
        'timestamp': timestamp.isoformat(),
        'image': image_filename,
        'detections': detections,
        'alert_level': alert_level,
        'objects_count': len(detections),
        'object_summary': {}
    }
    
    # Count objects by class
    for det in detections:
        cls = det['class']
        event['object_summary'][cls] = event['object_summary'].get(cls, 0) + 1
    
    # Load existing events
    events = load_events()
    events.append(event)
    
    # Keep only last 1000 events (storage limit)
    if len(events) > 1000:
        # Delete oldest images
        old_event = events.pop(0)
        old_image_path = os.path.join(EVENTS_DIR, old_event['image'])
        if os.path.exists(old_image_path):
            os.remove(old_image_path)
    
    # Save events metadata
    save_events(events)
    
    return event

def load_events():
    """Load events from metadata file"""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_events(events):
    """Save events to metadata file"""
    with open(METADATA_FILE, 'w') as f:
        json.dump(events, f, indent=2)

def get_recent_events(limit=50):
    """Get recent events"""
    events = load_events()
    return events[-limit:][::-1]  # Last N events, reversed

def get_event_by_id(event_id):
    """Get specific event by ID"""
    events = load_events()
    for event in events:
        if event['id'] == event_id:
            return event
    return None

def delete_old_events(days=7):
    """Delete events older than specified days"""
    from datetime import timedelta
    
    events = load_events()
    cutoff = datetime.now() - timedelta(days=days)
    
    new_events = []
    for event in events:
        event_time = datetime.fromisoformat(event['timestamp'])
        if event_time > cutoff:
            new_events.append(event)
        else:
            # Delete image
            image_path = os.path.join(EVENTS_DIR, event['image'])
            if os.path.exists(image_path):
                os.remove(image_path)
    
    save_events(new_events)
    return len(events) - len(new_events)

def get_storage_stats():
    """Get storage statistics"""
    events = load_events()
    
    total_size = 0
    for event in events:
        image_path = os.path.join(EVENTS_DIR, event['image'])
        if os.path.exists(image_path):
            total_size += os.path.getsize(image_path)
    
    return {
        'total_events': len(events),
        'storage_mb': total_size / (1024 * 1024),
        'oldest_event': events[0]['timestamp'] if events else None,
        'newest_event': events[-1]['timestamp'] if events else None
    }
