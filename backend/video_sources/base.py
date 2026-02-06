"""
Base Video Source Interface for Campus Guardian Drone
Supports multiple video input types: webcam, Pi camera, drone feed, etc.
"""
from abc import ABC, abstractmethod
import numpy as np

class VideoSource(ABC):
    """Abstract base class for all video sources"""
    
    @abstractmethod
    def get_frame(self):
        """
        Get the next frame from video source
        Returns: numpy array (BGR format) or None if error
        """
        pass
    
    @abstractmethod
    def release(self):
        """Release video source resources"""
        pass
    
    @abstractmethod
    def is_available(self):
        """Check if video source is available and readable"""
        pass
    
    @abstractmethod
    def get_resolution(self):
        """Get current video resolution as (width, height)"""
        pass
