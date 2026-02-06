"""
Video Sources Module
Abstraction layer for different video input sources
"""
from .base import VideoSource
from .laptop_cam import LaptopCam
from .drone_cam import DroneCam

__all__ = ['VideoSource', 'LaptopCam', 'DroneCam']
