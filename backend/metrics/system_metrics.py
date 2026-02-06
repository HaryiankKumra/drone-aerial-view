"""
System Metrics Tracker - Phase 4
Tracks operational metrics for 24/7 autonomous system
"""

import time
import json
from datetime import datetime

class SystemMetrics:
    """Track system-wide operational metrics"""
    
    def __init__(self, data_file="data/metrics.json"):
        """Initialize metrics tracker"""
        self.data_file = data_file
        self.start_time = time.time()
        
        # Operational metrics
        self.total_patrol_time = 0  # seconds
        self.total_events_detected = 0
        self.total_violations = 0
        self.total_battery_cycles = 0
        self.total_charges_completed = 0
        self.total_rth_triggers = 0
        self.total_uptime = 0  # seconds
        
        # Session metrics
        self.session_start = time.time()
        self.session_events = 0
        self.session_violations = 0
        
        # Failure tracking
        self.camera_failures = 0
        self.model_failures = 0
        self.connection_failures = 0
        self.last_failure_time = None
        
        # Load existing metrics if available
        self._load_metrics()
        
        print("📊 System metrics initialized")
    
    def _load_metrics(self):
        """Load metrics from disk"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.total_patrol_time = data.get('total_patrol_time', 0)
                self.total_events_detected = data.get('total_events_detected', 0)
                self.total_violations = data.get('total_violations', 0)
                self.total_battery_cycles = data.get('total_battery_cycles', 0)
                self.total_charges_completed = data.get('total_charges_completed', 0)
                self.total_rth_triggers = data.get('total_rth_triggers', 0)
                self.total_uptime = data.get('total_uptime', 0)
                self.camera_failures = data.get('camera_failures', 0)
                self.model_failures = data.get('model_failures', 0)
                self.connection_failures = data.get('connection_failures', 0)
                print("✅ Loaded metrics from disk")
        except FileNotFoundError:
            print("ℹ️  No existing metrics file - starting fresh")
        except Exception as e:
            print(f"⚠️  Error loading metrics: {e}")
    
    def _save_metrics(self):
        """Save metrics to disk"""
        try:
            data = {
                'total_patrol_time': self.total_patrol_time,
                'total_events_detected': self.total_events_detected,
                'total_violations': self.total_violations,
                'total_battery_cycles': self.total_battery_cycles,
                'total_charges_completed': self.total_charges_completed,
                'total_rth_triggers': self.total_rth_triggers,
                'total_uptime': self.total_uptime,
                'camera_failures': self.camera_failures,
                'model_failures': self.model_failures,
                'connection_failures': self.connection_failures,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving metrics: {e}")
    
    def increment_event(self):
        """Record a detection event"""
        self.total_events_detected += 1
        self.session_events += 1
        self._save_metrics()
    
    def increment_violation(self):
        """Record a violation"""
        self.total_violations += 1
        self.session_violations += 1
        self._save_metrics()
    
    def record_battery_cycle(self):
        """Record a completed battery charge cycle"""
        self.total_battery_cycles += 1
        self.total_charges_completed += 1
        print(f"🔋 Battery cycle #{self.total_battery_cycles} completed")
        self._save_metrics()
    
    def record_rth_trigger(self):
        """Record an RTH trigger"""
        self.total_rth_triggers += 1
        self._save_metrics()
    
    def record_patrol_time(self, seconds):
        """Add patrol time (call periodically)"""
        self.total_patrol_time += seconds
        self._save_metrics()
    
    def record_failure(self, failure_type):
        """Record a system failure"""
        if failure_type == 'camera':
            self.camera_failures += 1
        elif failure_type == 'model':
            self.model_failures += 1
        elif failure_type == 'connection':
            self.connection_failures += 1
        
        self.last_failure_time = datetime.now().isoformat()
        print(f"⚠️  Failure recorded: {failure_type}")
        self._save_metrics()
    
    def get_metrics(self):
        """Get current metrics snapshot"""
        current_uptime = time.time() - self.session_start
        total_uptime = self.total_uptime + current_uptime
        
        return {
            'total_patrol_time': self.total_patrol_time,
            'total_patrol_hours': round(self.total_patrol_time / 3600, 2),
            'total_events_detected': self.total_events_detected,
            'total_violations': self.total_violations,
            'total_battery_cycles': self.total_battery_cycles,
            'total_charges_completed': self.total_charges_completed,
            'total_rth_triggers': self.total_rth_triggers,
            'total_uptime': total_uptime,
            'total_uptime_hours': round(total_uptime / 3600, 2),
            'session_events': self.session_events,
            'session_violations': self.session_violations,
            'session_uptime': current_uptime,
            'session_uptime_hours': round(current_uptime / 3600, 2),
            'camera_failures': self.camera_failures,
            'model_failures': self.model_failures,
            'connection_failures': self.connection_failures,
            'last_failure': self.last_failure_time,
            'avg_events_per_hour': round((self.total_events_detected / (total_uptime / 3600)) if total_uptime > 0 else 0, 2)
        }
    
    def reset_session_metrics(self):
        """Reset session-specific metrics"""
        self.session_start = time.time()
        self.session_events = 0
        self.session_violations = 0
        print("🔄 Session metrics reset")
    
    def shutdown(self):
        """Save metrics on shutdown"""
        current_uptime = time.time() - self.session_start
        self.total_uptime += current_uptime
        self._save_metrics()
        print("💾 Metrics saved to disk")
