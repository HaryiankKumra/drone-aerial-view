"""
Vercel Serverless API - Uses HuggingFace Inference API for YOLO detection
This version offloads ML inference to HuggingFace, keeping Vercel lightweight
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the main Flask app
from app import app

# Vercel expects the app to be available at this module level
# No need to run app.run() - Vercel handles that
