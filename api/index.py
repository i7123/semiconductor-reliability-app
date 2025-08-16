"""
Vercel serverless function entry point for the FastAPI backend
"""
import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

from backend.app.main import app

# This is required for Vercel to recognize the FastAPI app
handler = app