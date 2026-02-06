"""
PHASE-4: Failure Handler
Automatic recovery mechanisms for camera, model, and connection failures
"""

import time
import logging
from datetime import datetime
from typing import Dict, Optional, Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FailureHandler:
    """Manages failure detection and recovery for critical system components"""
    
    # Retry configurations
    CAMERA_RETRY_INTERVAL = 5  # seconds
    MODEL_RETRY_INTERVAL = 10  # seconds
    CONNECTION_RETRY_INTERVAL = 3  # seconds
    
    MAX_RETRIES = 3  # Maximum retry attempts before manual intervention
    
    def __init__(self, metrics_tracker=None):
        """
        Initialize failure handler
        
        Args:
            metrics_tracker: SystemMetrics instance for logging failures
        """
        self.metrics_tracker = metrics_tracker
        
        # Failure states
        self.camera_healthy = True
        self.model_healthy = True
        self.connection_healthy = True
        
        # Retry tracking
        self.camera_retry_count = 0
        self.model_retry_count = 0
        self.connection_retry_count = 0
        
        # Last failure timestamps
        self.last_camera_failure = None
        self.last_model_failure = None
        self.last_connection_failure = None
        
        # Last retry timestamps
        self.last_camera_retry = 0
        self.last_model_retry = 0
        self.last_connection_retry = 0
        
        # Recovery callbacks (set by application)
        self.camera_recovery_callback: Optional[Callable] = None
        self.model_recovery_callback: Optional[Callable] = None
        self.connection_recovery_callback: Optional[Callable] = None
        
        logger.info("🛡️ Failure handler initialized")
    
    def report_camera_failure(self, error_message: str) -> Dict:
        """
        Report camera failure and attempt recovery
        
        Args:
            error_message: Description of the failure
            
        Returns:
            dict: Recovery status
        """
        self.camera_healthy = False
        self.last_camera_failure = datetime.now()
        
        # Log to metrics
        if self.metrics_tracker:
            self.metrics_tracker.record_failure('camera')
        
        logger.error(f"📹 CAMERA FAILURE: {error_message}")
        
        # Attempt recovery after cooldown
        current_time = time.time()
        if current_time - self.last_camera_retry >= self.CAMERA_RETRY_INTERVAL:
            self.last_camera_retry = current_time
            self.camera_retry_count += 1
            
            if self.camera_retry_count <= self.MAX_RETRIES:
                logger.info(f"🔄 Attempting camera recovery (try {self.camera_retry_count}/{self.MAX_RETRIES})...")
                
                if self.camera_recovery_callback:
                    try:
                        self.camera_recovery_callback()
                        self.camera_healthy = True
                        self.camera_retry_count = 0
                        logger.info("✅ Camera recovered successfully")
                        return {
                            'recovered': True,
                            'message': 'Camera reconnected',
                            'retries': self.camera_retry_count
                        }
                    except Exception as e:
                        logger.error(f"❌ Camera recovery failed: {e}")
                        return {
                            'recovered': False,
                            'message': f'Recovery attempt {self.camera_retry_count} failed',
                            'retries': self.camera_retry_count
                        }
            else:
                logger.error(f"🚨 Camera recovery failed after {self.MAX_RETRIES} attempts - manual intervention required")
                return {
                    'recovered': False,
                    'message': 'Max retries exceeded - manual intervention required',
                    'retries': self.camera_retry_count
                }
        
        return {
            'recovered': False,
            'message': f'Waiting for retry cooldown ({self.CAMERA_RETRY_INTERVAL}s)',
            'retries': self.camera_retry_count
        }
    
    def report_model_failure(self, error_message: str) -> Dict:
        """
        Report model failure and attempt recovery
        
        Args:
            error_message: Description of the failure
            
        Returns:
            dict: Recovery status
        """
        self.model_healthy = False
        self.last_model_failure = datetime.now()
        
        # Log to metrics
        if self.metrics_tracker:
            self.metrics_tracker.record_failure('model')
        
        logger.error(f"🤖 MODEL FAILURE: {error_message}")
        
        # Attempt recovery after cooldown
        current_time = time.time()
        if current_time - self.last_model_retry >= self.MODEL_RETRY_INTERVAL:
            self.last_model_retry = current_time
            self.model_retry_count += 1
            
            if self.model_retry_count <= self.MAX_RETRIES:
                logger.info(f"🔄 Attempting model reload (try {self.model_retry_count}/{self.MAX_RETRIES})...")
                
                if self.model_recovery_callback:
                    try:
                        self.model_recovery_callback()
                        self.model_healthy = True
                        self.model_retry_count = 0
                        logger.info("✅ Model reloaded successfully")
                        return {
                            'recovered': True,
                            'message': 'Model reloaded',
                            'retries': self.model_retry_count
                        }
                    except Exception as e:
                        logger.error(f"❌ Model reload failed: {e}")
                        return {
                            'recovered': False,
                            'message': f'Recovery attempt {self.model_retry_count} failed',
                            'retries': self.model_retry_count
                        }
            else:
                logger.error(f"🚨 Model recovery failed after {self.MAX_RETRIES} attempts - manual intervention required")
                return {
                    'recovered': False,
                    'message': 'Max retries exceeded - manual intervention required',
                    'retries': self.model_retry_count
                }
        
        return {
            'recovered': False,
            'message': f'Waiting for retry cooldown ({self.MODEL_RETRY_INTERVAL}s)',
            'retries': self.model_retry_count
        }
    
    def report_connection_failure(self, error_message: str) -> Dict:
        """
        Report connection failure (RPi disconnect, network issues, etc.)
        
        Args:
            error_message: Description of the failure
            
        Returns:
            dict: Recovery status
        """
        self.connection_healthy = False
        self.last_connection_failure = datetime.now()
        
        # Log to metrics
        if self.metrics_tracker:
            self.metrics_tracker.record_failure('connection')
        
        logger.warning(f"📡 CONNECTION FAILURE: {error_message}")
        
        # Attempt recovery after cooldown
        current_time = time.time()
        if current_time - self.last_connection_retry >= self.CONNECTION_RETRY_INTERVAL:
            self.last_connection_retry = current_time
            self.connection_retry_count += 1
            
            if self.connection_retry_count <= self.MAX_RETRIES:
                logger.info(f"🔄 Attempting connection recovery (try {self.connection_retry_count}/{self.MAX_RETRIES})...")
                
                if self.connection_recovery_callback:
                    try:
                        self.connection_recovery_callback()
                        self.connection_healthy = True
                        self.connection_retry_count = 0
                        logger.info("✅ Connection restored")
                        return {
                            'recovered': True,
                            'message': 'Connection restored',
                            'retries': self.connection_retry_count
                        }
                    except Exception as e:
                        logger.warning(f"⚠️ Connection recovery attempt failed: {e}")
                        return {
                            'recovered': False,
                            'message': f'Recovery attempt {self.connection_retry_count} failed',
                            'retries': self.connection_retry_count
                        }
            else:
                logger.warning(f"⚠️ Connection recovery failed after {self.MAX_RETRIES} attempts - operating in degraded mode")
                return {
                    'recovered': False,
                    'message': 'Max retries exceeded - operating in degraded mode',
                    'retries': self.connection_retry_count
                }
        
        return {
            'recovered': False,
            'message': f'Waiting for retry cooldown ({self.CONNECTION_RETRY_INTERVAL}s)',
            'retries': self.connection_retry_count
        }
    
    def mark_camera_healthy(self):
        """Mark camera as healthy and reset retry count"""
        self.camera_healthy = True
        self.camera_retry_count = 0
        logger.info("✅ Camera marked as healthy")
    
    def mark_model_healthy(self):
        """Mark model as healthy and reset retry count"""
        self.model_healthy = True
        self.model_retry_count = 0
        logger.info("✅ Model marked as healthy")
    
    def mark_connection_healthy(self):
        """Mark connection as healthy and reset retry count"""
        self.connection_healthy = True
        self.connection_retry_count = 0
        logger.info("✅ Connection marked as healthy")
    
    def get_status(self) -> Dict:
        """
        Get current failure handler status
        
        Returns:
            dict: Status information
        """
        return {
            'camera': {
                'healthy': self.camera_healthy,
                'retry_count': self.camera_retry_count,
                'last_failure': self.last_camera_failure.isoformat() if self.last_camera_failure else None
            },
            'model': {
                'healthy': self.model_healthy,
                'retry_count': self.model_retry_count,
                'last_failure': self.last_model_failure.isoformat() if self.last_model_failure else None
            },
            'connection': {
                'healthy': self.connection_healthy,
                'retry_count': self.connection_retry_count,
                'last_failure': self.last_connection_failure.isoformat() if self.last_connection_failure else None
            },
            'overall_health': self.camera_healthy and self.model_healthy and self.connection_healthy
        }
    
    def reset_all(self):
        """Reset all failure states (for testing or manual recovery)"""
        self.camera_healthy = True
        self.model_healthy = True
        self.connection_healthy = True
        
        self.camera_retry_count = 0
        self.model_retry_count = 0
        self.connection_retry_count = 0
        
        logger.info("🔄 All failure states reset")
