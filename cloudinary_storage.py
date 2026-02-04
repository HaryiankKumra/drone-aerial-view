"""
Cloudinary Integration for Campus Guardian Drone
Permanent cloud storage for detection images/videos (25GB FREE)
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url
import os
import base64
from io import BytesIO
from datetime import datetime

# Configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', 'dq9v0bo36'),
    api_key=os.getenv('CLOUDINARY_API_KEY', '895472581156914'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),  # Set via environment variable
    secure=True
)

def is_configured():
    """Check if Cloudinary is properly configured"""
    try:
        # Test configuration
        if not os.getenv('CLOUDINARY_API_SECRET'):
            print("⚠️  Cloudinary not configured - set CLOUDINARY_API_SECRET environment variable")
            return False
        
        # Configuration is valid if secret is present
        print("✅ Cloudinary configured successfully!")
        print(f"📦 Cloud: {cloudinary.config().cloud_name}")
        return True
    except Exception as e:
        print(f"❌ Cloudinary error: {e}")
        return False

def upload_detection_image(base64_image, event_id, folder='campus-guardian/detections'):
    """
    Upload detection image to Cloudinary
    
    Args:
        base64_image: Base64 encoded image (with or without data URI prefix)
        event_id: Unique event identifier
        folder: Cloudinary folder path
    
    Returns:
        dict with 'url', 'secure_url', 'public_id' or None if failed
    """
    if not is_configured():
        return None
    
    try:
        # Remove data URI prefix if present
        if base64_image.startswith('data:image'):
            base64_image = base64_image.split(',')[1]
        
        # Upload to Cloudinary
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        public_id = f"event_{event_id}_{timestamp}"
        
        result = cloudinary.uploader.upload(
            f"data:image/jpeg;base64,{base64_image}",
            public_id=public_id,
            folder=folder,
            resource_type='image',
            format='jpg',
            quality='auto:good',  # Auto-optimize quality
            fetch_format='auto',   # Auto-format for best delivery
            transformation=[
                {'width': 1920, 'height': 1080, 'crop': 'limit'},  # Max size limit
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'}
            ]
        )
        
        return {
            'url': result.get('url'),
            'secure_url': result.get('secure_url'),
            'public_id': result.get('public_id'),
            'width': result.get('width'),
            'height': result.get('height'),
            'bytes': result.get('bytes'),
            'format': result.get('format')
        }
    
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        return None

def upload_video(video_file_path, event_id, folder='campus-guardian/videos'):
    """
    Upload video to Cloudinary
    
    Args:
        video_file_path: Path to video file
        event_id: Unique event identifier
        folder: Cloudinary folder path
    
    Returns:
        dict with video details or None if failed
    """
    if not is_configured():
        return None
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        public_id = f"{folder}/video_{event_id}_{timestamp}"
        
        result = cloudinary.uploader.upload(
            video_file_path,
            public_id=public_id,
            folder=folder,
            resource_type='video',
            quality='auto:good',
            transformation=[
                {'width': 1280, 'height': 720, 'crop': 'limit'},
                {'quality': 'auto:good'}
            ]
        )
        
        return {
            'url': result.get('url'),
            'secure_url': result.get('secure_url'),
            'public_id': result.get('public_id'),
            'duration': result.get('duration'),
            'width': result.get('width'),
            'height': result.get('height'),
            'bytes': result.get('bytes'),
            'format': result.get('format')
        }
    
    except Exception as e:
        print(f"Error uploading video to Cloudinary: {e}")
        return None

def upload_csv(csv_file_path, event_id, folder='campus-guardian/logs'):
    """
    Upload CSV/Excel file to Cloudinary
    
    Args:
        csv_file_path: Path to CSV file
        event_id: Unique event identifier
        folder: Cloudinary folder path
    
    Returns:
        dict with file details or None if failed
    """
    if not is_configured():
        return None
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        public_id = f"log_{event_id}_{timestamp}"
        
        result = cloudinary.uploader.upload(
            csv_file_path,
            public_id=public_id,
            folder=folder,
            resource_type='raw',  # For non-image files like CSV
            format='csv'
        )
        
        return {
            'url': result.get('url'),
            'secure_url': result.get('secure_url'),
            'public_id': result.get('public_id'),
            'bytes': result.get('bytes'),
            'format': result.get('format')
        }
    
    except Exception as e:
        print(f"Error uploading CSV to Cloudinary: {e}")
        return None

def get_optimized_url(public_id, width=None, height=None, quality='auto:good'):
    """
    Get optimized delivery URL for an image
    
    Args:
        public_id: Cloudinary public ID
        width: Optional width
        height: Optional height
        quality: Quality setting
    
    Returns:
        Optimized URL
    """
    try:
        transformation = {'quality': quality, 'fetch_format': 'auto'}
        if width:
            transformation['width'] = width
        if height:
            transformation['height'] = height
        
        url, _ = cloudinary_url(public_id, **transformation)
        return url
    except Exception as e:
        print(f"Error generating URL: {e}")
        return None

def delete_image(public_id):
    """Delete image from Cloudinary"""
    if not is_configured():
        return False
    
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type='image')
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"Error deleting from Cloudinary: {e}")
        return False

def get_storage_stats():
    """Get Cloudinary storage usage statistics"""
    if not is_configured():
        return None
    
    try:
        usage = cloudinary.api.usage()
        # Handle both dict and object-style responses
        if isinstance(usage, dict):
            return {
                'total_resources': usage.get('resources', 0),
                'bandwidth_used': usage.get('bandwidth', {}).get('usage', 0) if isinstance(usage.get('bandwidth'), dict) else usage.get('bandwidth', 0),
                'storage_used': usage.get('storage', {}).get('usage', 0) if isinstance(usage.get('storage'), dict) else usage.get('storage', 0),
                'transformations': usage.get('transformations', {}).get('usage', 0) if isinstance(usage.get('transformations'), dict) else usage.get('transformations', 0),
                'plan': usage.get('plan', 'free'),
                'credits_used': usage.get('credits', {}).get('usage', 0) if isinstance(usage.get('credits'), dict) else usage.get('credits', 0),
                'credits_limit': usage.get('credits', {}).get('limit', 25000000000) if isinstance(usage.get('credits'), dict) else 25000000000  # 25GB default
            }
        else:
            return {
                'total_resources': getattr(usage, 'resources', 0),
                'bandwidth_used': getattr(usage, 'bandwidth', 0),
                'storage_used': getattr(usage, 'storage', 0),
                'plan': getattr(usage, 'plan', 'free')
            }
    except Exception as e:
        print(f"Error getting Cloudinary stats: {e}")
        # Return basic info if API call fails
        return {
            'configured': True,
            'cloud_name': cloudinary.config().cloud_name,
            'error': str(e)
        }

# Test configuration on import
if __name__ == '__main__':
    print("Testing Cloudinary configuration...")
    if is_configured():
        print("\n✅ All good! Ready to upload images.")
        stats = get_storage_stats()
        if stats and not stats.get('error'):
            print(f"\n📊 Storage Stats:")
            print(f"  Resources: {stats.get('total_resources', 'N/A')}")
            print(f"  Storage Used: {stats.get('storage_used', 0) / 1024 / 1024:.2f} MB")
            print(f"  Plan: {stats.get('plan', 'free')}")
        elif stats:
            print(f"\n⚠️  Stats available but limited: {stats.get('cloud_name')}")
    else:
        print("\n❌ Configuration failed!")
        print("\nSet environment variable:")
        print("export CLOUDINARY_API_SECRET='CjTNupJulkSZmSv7vaknaogJD1A'")
