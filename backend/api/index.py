import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Import the FastAPI app
from server import app

# Vercel serverless function handler
def handler(request, context):
    return app(request, context)

# Also export app directly for Vercel
app = app
