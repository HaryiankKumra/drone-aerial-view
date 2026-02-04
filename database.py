"""
MongoDB Atlas Integration for Campus Guardian Drone
Free cloud storage for events, detections, and recordings
"""

from pymongo import MongoClient
from datetime import datetime
import os
from typing import List, Dict, Optional

class DroneDatabase:
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize MongoDB connection
        
        Setup Instructions:
        1. Go to https://www.mongodb.com/cloud/atlas/register (NO CREDIT CARD NEEDED)
        2. Create free account
        3. Create cluster (M0 Free tier - 512MB storage)
        4. Create database user
        5. Get connection string
        6. Set MONGODB_URI environment variable
        """
        self.connection_string = connection_string or os.getenv('MONGODB_URI')
        
        if not self.connection_string:
            print("⚠️  MongoDB not configured - using local storage fallback")
            print("📝 To enable cloud storage:")
            print("   1. Sign up at https://www.mongodb.com/cloud/atlas/register")
            print("   2. Create M0 Free cluster (512MB free)")
            print("   3. Set MONGODB_URI environment variable")
            self.client = None
            self.db = None
            return
        
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client['campus_guardian']
            
            # Collections
            self.events = self.db['events']
            self.detections = self.db['detections']
            self.sessions = self.db['sessions']
            self.statistics = self.db['statistics']
            
            # Create indexes for faster queries
            self.events.create_index([('timestamp', -1)])
            self.events.create_index([('severity', 1)])
            self.detections.create_index([('timestamp', -1)])
            
            print("✅ MongoDB Atlas connected successfully!")
            print(f"📊 Database: {self.db.name}")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("📂 Falling back to local storage")
            self.client = None
            self.db = None
    
    def is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        return self.client is not None and self.db is not None
    
    def save_detection(self, detection_data: Dict) -> Optional[str]:
        """
        Save detection event to cloud
        
        Schema:
        {
            'timestamp': datetime,
            'frame_id': str,
            'objects': [{'class': str, 'confidence': float, 'bbox': [x,y,w,h]}],
            'total_people': int,
            'total_vehicles': int,
            'alert_level': str,
            'session_id': str
        }
        """
        if not self.is_connected():
            return None
        
        try:
            detection_data['timestamp'] = datetime.utcnow()
            result = self.detections.insert_one(detection_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error saving detection: {e}")
            return None
    
    def save_event(self, event_data: Dict) -> Optional[str]:
        """
        Save alert/event to cloud
        
        Schema:
        {
            'timestamp': datetime,
            'event_type': str,  # 'person_detected', 'crowd_warning', 'vehicle_detected'
            'severity': str,    # 'info', 'warning', 'critical'
            'zone': str,
            'description': str,
            'image_base64': str,  # Optional - only for critical events
            'detection_id': str,
            'metadata': {...}
        }
        """
        if not self.is_connected():
            return None
        
        try:
            event_data['timestamp'] = datetime.utcnow()
            event_data['is_active'] = True
            result = self.events.insert_one(event_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error saving event: {e}")
            return None
    
    def get_recent_events(self, limit: int = 50, severity: Optional[str] = None) -> List[Dict]:
        """Get recent events from cloud"""
        if not self.is_connected():
            return []
        
        try:
            query = {}
            if severity:
                query['severity'] = severity
            
            events = self.events.find(query).sort('timestamp', -1).limit(limit)
            return [{**event, '_id': str(event['_id'])} for event in events]
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    def get_recent_detections(self, limit: int = 100) -> List[Dict]:
        """Get recent detections from cloud"""
        if not self.is_connected():
            return []
        
        try:
            detections = self.detections.find().sort('timestamp', -1).limit(limit)
            return [{**det, '_id': str(det['_id'])} for det in detections]
        except Exception as e:
            print(f"Error fetching detections: {e}")
            return []
    
    def get_statistics(self, hours: int = 24) -> Dict:
        """Get aggregated statistics from cloud"""
        if not self.is_connected():
            return {
                'total_detections': 0,
                'total_people': 0,
                'total_vehicles': 0,
                'total_alerts': 0,
                'critical_alerts': 0
            }
        
        try:
            from datetime import timedelta
            since = datetime.utcnow() - timedelta(hours=hours)
            
            total_detections = self.detections.count_documents({'timestamp': {'$gte': since}})
            total_alerts = self.events.count_documents({'timestamp': {'$gte': since}})
            critical_alerts = self.events.count_documents({
                'timestamp': {'$gte': since},
                'severity': 'critical'
            })
            
            # Aggregate people and vehicles
            pipeline = [
                {'$match': {'timestamp': {'$gte': since}}},
                {'$group': {
                    '_id': None,
                    'total_people': {'$sum': '$total_people'},
                    'total_vehicles': {'$sum': '$total_vehicles'}
                }}
            ]
            
            agg_result = list(self.detections.aggregate(pipeline))
            
            stats = {
                'total_detections': total_detections,
                'total_people': agg_result[0]['total_people'] if agg_result else 0,
                'total_vehicles': agg_result[0]['total_vehicles'] if agg_result else 0,
                'total_alerts': total_alerts,
                'critical_alerts': critical_alerts,
                'period_hours': hours
            }
            
            return stats
        except Exception as e:
            print(f"Error fetching statistics: {e}")
            return {}
    
    def dismiss_event(self, event_id: str) -> bool:
        """Mark event as dismissed"""
        if not self.is_connected():
            return False
        
        try:
            from bson import ObjectId
            result = self.events.update_one(
                {'_id': ObjectId(event_id)},
                {'$set': {'is_active': False, 'dismissed_at': datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error dismissing event: {e}")
            return False
    
    def start_session(self, metadata: Optional[Dict] = None) -> Optional[str]:
        """Start a new surveillance session"""
        if not self.is_connected():
            return None
        
        try:
            session = {
                'start_time': datetime.utcnow(),
                'end_time': None,
                'is_active': True,
                'metadata': metadata or {}
            }
            result = self.sessions.insert_one(session)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error starting session: {e}")
            return None
    
    def end_session(self, session_id: str, stats: Optional[Dict] = None) -> bool:
        """End a surveillance session"""
        if not self.is_connected():
            return False
        
        try:
            from bson import ObjectId
            update = {
                'end_time': datetime.utcnow(),
                'is_active': False
            }
            if stats:
                update['stats'] = stats
            
            result = self.sessions.update_one(
                {'_id': ObjectId(session_id)},
                {'$set': update}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error ending session: {e}")
            return False


# Global database instance
db = DroneDatabase()
