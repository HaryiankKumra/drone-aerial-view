"""
CSV Event Logger for Campus Guardian Drone
Maintains real-time event log with timestamps
Uploads to Cloudinary for permanent storage
"""

import csv
import os
from datetime import datetime
from pathlib import Path
import time

# Storage directory
LOGS_DIR = Path('recordings/logs')
LOGS_DIR.mkdir(parents=True, exist_ok=True)

class EventLogger:
    def __init__(self):
        self.current_session_file = None
        self.csv_writer = None
        self.csv_file = None
        self.start_new_session()
    
    def start_new_session(self):
        """Start a new CSV log file for this session"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.current_session_file = LOGS_DIR / f'events_{timestamp}.csv'
        
        # Create CSV with headers
        self.csv_file = open(self.current_session_file, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([
            'Timestamp',
            'Date',
            'Time',
            'Event_Type',
            'Object_Class',
            'Count',
            'Confidence',
            'Alert_Level',
            'Location_X',
            'Location_Y',
            'Notes'
        ])
        self.csv_file.flush()
        
        print(f"📊 Started new event log: {self.current_session_file}")
        return str(self.current_session_file)
    
    def log_detection(self, detections, alert_level='info'):
        """
        Log a detection event to CSV
        
        Args:
            detections: List of detection objects
            alert_level: 'info', 'warning', or 'critical'
        """
        if not detections:
            return
        
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Include milliseconds
        date = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        # Count by class
        class_counts = {}
        class_confidences = {}
        class_locations = {}
        
        for det in detections:
            cls = det['class']
            class_counts[cls] = class_counts.get(cls, 0) + 1
            
            if cls not in class_confidences:
                class_confidences[cls] = []
                class_locations[cls] = []
            
            class_confidences[cls].append(det['confidence'])
            
            # Calculate center of bounding box
            bbox = det['bbox']
            center_x = (bbox['x1'] + bbox['x2']) / 2
            center_y = (bbox['y1'] + bbox['y2']) / 2
            class_locations[cls].append((center_x, center_y))
        
        # Write one row per object class detected
        for cls, count in class_counts.items():
            avg_conf = sum(class_confidences[cls]) / len(class_confidences[cls])
            
            # Get first location for this class
            loc_x, loc_y = class_locations[cls][0]
            
            # Determine event type
            if cls in ['pedestrian', 'people']:
                event_type = 'PERSON_DETECTED'
            elif cls in ['car', 'van', 'truck', 'bus']:
                event_type = 'VEHICLE_DETECTED'
            elif cls in ['bicycle', 'motor']:
                event_type = 'BIKE_DETECTED'
            else:
                event_type = 'OBJECT_DETECTED'
            
            # Notes
            if count > 1:
                notes = f'{count} {cls}s detected'
            else:
                notes = f'1 {cls} detected'
            
            self.csv_writer.writerow([
                timestamp,
                date,
                time_str,
                event_type,
                cls,
                count,
                f'{avg_conf:.2f}',
                alert_level.upper(),
                f'{int(loc_x)}',
                f'{int(loc_y)}',
                notes
            ])
        
        # Flush to disk immediately
        self.csv_file.flush()
    
    def log_custom_event(self, event_type, message, alert_level='info'):
        """Log a custom event (like recording start/stop)"""
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        date = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        self.csv_writer.writerow([
            timestamp,
            date,
            time_str,
            event_type,
            '-',
            '0',
            '-',
            alert_level.upper(),
            '-',
            '-',
            message
        ])
        self.csv_file.flush()
    
    def get_current_log_file(self):
        """Get path to current CSV log file"""
        return str(self.current_session_file)
    
    def upload_to_cloudinary(self):
        """Upload current CSV to Cloudinary"""
        try:
            from cloudinary_storage import upload_csv
            
            if self.current_session_file and self.current_session_file.exists():
                result = upload_csv(
                    str(self.current_session_file),
                    f'log_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
                )
                
                if result:
                    print(f"☁️  CSV uploaded to Cloudinary: {result['secure_url']}")
                    return result['secure_url']
        except Exception as e:
            print(f"⚠️  Could not upload CSV to Cloudinary: {e}")
        
        return None
    
    def close(self):
        """Close current log file and upload to Cloudinary"""
        if self.csv_file:
            self.csv_file.close()
            return self.upload_to_cloudinary()

# Global logger instance
event_logger = EventLogger()

# Test
if __name__ == '__main__':
    print("🧪 Testing Event Logger\n")
    
    # Simulate some detections
    test_detections = [
        {
            'class': 'car',
            'confidence': 0.91,
            'bbox': {'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200}
        },
        {
            'class': 'pedestrian',
            'confidence': 0.87,
            'bbox': {'x1': 300, 'y1': 150, 'x2': 350, 'y2': 250}
        }
    ]
    
    event_logger.log_detection(test_detections, 'warning')
    event_logger.log_custom_event('SYSTEM_START', 'Detection system started')
    
    time.sleep(0.5)
    
    event_logger.log_detection([test_detections[0]], 'info')
    event_logger.log_custom_event('RECORDING_START', 'Video recording started')
    
    print(f"\n✅ Log file created: {event_logger.get_current_log_file()}")
    print(f"\nCheck the file to see the CSV format!")
    
    # Upload to Cloudinary
    url = event_logger.close()
    if url:
        print(f"☁️  Uploaded to: {url}")
