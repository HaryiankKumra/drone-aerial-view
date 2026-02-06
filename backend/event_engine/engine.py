"""
Event Engine - Converts detections into security events
Implements 5-second persistence rule and severity classification
"""
import uuid
from datetime import datetime
from .database import EventDatabase

# Severity mapping
SEVERITY_MAP = {
    'person': 'HIGH',
    'people': 'HIGH',
    'bicycle': 'MEDIUM',
    'bike': 'MEDIUM',
    'motorcycle': 'MEDIUM',
    'car': 'MEDIUM',
    'truck': 'MEDIUM',
    'bus': 'MEDIUM',
    'litter': 'LOW',
    'trash': 'LOW',
    'debris': 'LOW'
}

# Default severity
DEFAULT_SEVERITY = 'MEDIUM'

class EventEngine:
    def __init__(self, db_path='data/events.db'):
        self.db = EventDatabase(db_path)
        self.persistence_threshold = 5  # seconds
        
    def process_detection(self, detection_data):
        """
        Process a detection and determine if it should become an event
        
        Args:
            detection_data: {
                'class': str,
                'confidence': float,
                'bbox': [x, y, w, h],
                'snapshot_url': str (optional),
                'snapshot_path': str (optional),
                'drone_lat': float (optional),
                'drone_lon': float (optional),
                'zone': str (optional)
            }
        
        Returns:
            event_id if event created, None otherwise
        """
        object_type = detection_data['class'].lower()
        confidence = detection_data['confidence']
        
        # Update detection buffer
        self.db.update_detection_buffer(object_type, confidence)
        
        # Check if persistence threshold met
        persisted, avg_confidence = self.db.check_persistence(
            object_type, 
            self.persistence_threshold
        )
        
        if persisted:
            # Create event
            event_id = self._create_event(detection_data, avg_confidence)
            
            # Clear buffer for this object type
            self.db.clear_detection_buffer(object_type)
            
            return event_id
        
        return None
    
    def _create_event(self, detection_data, avg_confidence):
        """Create a security event"""
        object_type = detection_data['class'].lower()
        severity = self._get_severity(object_type)
        
        event_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"
        
        event_data = {
            'event_id': event_id,
            'timestamp': datetime.now().isoformat(),
            'object_type': object_type,
            'severity': severity,
            'confidence': avg_confidence,
            'drone_lat': detection_data.get('drone_lat'),
            'drone_lon': detection_data.get('drone_lon'),
            'zone': detection_data.get('zone', 'Campus Area'),
            'snapshot_url': detection_data.get('snapshot_url'),
            'snapshot_path': detection_data.get('snapshot_path'),
            'bbox_data': detection_data.get('bbox', {})
        }
        
        self.db.create_event(event_data)
        
        return event_id
    
    def _get_severity(self, object_type):
        """Get severity level for object type"""
        return SEVERITY_MAP.get(object_type, DEFAULT_SEVERITY)
    
    def get_recent_events(self, limit=50, severity=None):
        """Get recent events"""
        return self.db.get_events(limit, severity)
    
    def get_event_details(self, event_id):
        """Get event by ID"""
        return self.db.get_event_by_id(event_id)
    
    def get_statistics(self):
        """Get event statistics"""
        return self.db.get_stats()
    
    def should_alert(self, event_id):
        """Determine if event should trigger alert"""
        event = self.db.get_event_by_id(event_id)
        if not event:
            return False
        
        # Alert on HIGH and MEDIUM severity
        return event['severity'] in ['HIGH', 'MEDIUM']
    
    def log_alert_sent(self, event_id, alert_type, recipient):
        """Log that alert was sent"""
        return self.db.log_alert(event_id, alert_type, recipient)
