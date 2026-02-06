"""
Imgur Integration - Simple, Free, Anonymous Uploads
No API key needed for anonymous uploads!
"""

import requests
import base64
from datetime import datetime

IMGUR_CLIENT_ID = "546c25a59c58ad7"  # Public anonymous client ID

def upload_to_imgur(base64_image, title="Campus Guardian Detection"):
    """
    Upload image to Imgur (no account needed!)
    
    Args:
        base64_image: Base64 encoded image
        title: Image title
    
    Returns:
        dict with 'url', 'delete_hash' or None
    """
    try:
        # Remove data URI prefix if present
        if base64_image.startswith('data:image'):
            base64_image = base64_image.split(',')[1]
        
        # Upload to Imgur
        headers = {'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
        data = {
            'image': base64_image,
            'type': 'base64',
            'title': title,
            'description': f'Aerial detection - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        }
        
        response = requests.post(
            'https://api.imgur.com/3/image',
            headers=headers,
            data=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()['data']
            return {
                'url': result['link'],
                'delete_hash': result.get('deletehash'),
                'id': result.get('id'),
                'size': result.get('size', 0)
            }
        else:
            print(f"Imgur error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error uploading to Imgur: {e}")
        return None

def delete_from_imgur(delete_hash):
    """Delete image from Imgur"""
    try:
        headers = {'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
        response = requests.delete(
            f'https://api.imgur.com/3/image/{delete_hash}',
            headers=headers
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error deleting from Imgur: {e}")
        return False

# Test
if __name__ == '__main__':
    import cv2
    import numpy as np
    
    print("🧪 Testing Imgur Upload\n")
    
    # Create test image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img[:] = (30, 30, 30)
    cv2.rectangle(img, (100, 100), (300, 250), (0, 255, 0), 3)
    cv2.putText(img, 'IMGUR TEST', (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    _, buffer = cv2.imencode('.jpg', img)
    base64_img = base64.b64encode(buffer).decode('utf-8')
    
    print("📤 Uploading to Imgur...")
    result = upload_to_imgur(base64_img, "Campus Guardian Test")
    
    if result:
        print(f"\n✅ Upload successful!")
        print(f"🔗 URL: {result['url']}")
        print(f"📏 Size: {result['size']} bytes")
        print(f"🗑️  Delete hash: {result['delete_hash']}")
        print(f"\n🎉 Open this URL: {result['url']}")
    else:
        print("\n❌ Upload failed!")
