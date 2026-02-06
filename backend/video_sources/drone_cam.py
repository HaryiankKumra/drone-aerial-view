"""
Drone Camera Video Source (Future Implementation)
For actual drone deployment with DJI Tello or similar
"""
from .base import VideoSource

class DroneCam(VideoSource):
    """
    Drone camera video source (placeholder for future drone integration)
    Will be implemented when deploying on actual drone hardware
    """
    
    def __init__(self, drone_ip='192.168.10.1', port=11111):
        """
        Initialize drone camera connection
        Args:
            drone_ip: Drone's IP address
            port: Video stream port
        """
        self.drone_ip = drone_ip
        self.port = port
        self.connected = False
        print(f"⚠️ DroneCam not yet implemented - use LaptopCam for development")
    
    def get_frame(self):
        """Get frame from drone camera (to be implemented)"""
        raise NotImplementedError("DroneCam integration pending - coming in Phase 2")
    
    def release(self):
        """Release drone camera connection"""
        pass
    
    def is_available(self):
        """Check if drone camera is connected"""
        return False
    
    def get_resolution(self):
        """Get drone camera resolution"""
        return (1280, 720)  # DJI Tello default
