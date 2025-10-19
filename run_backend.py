#!/usr/bin/env python3
"""
Simple backend runner script for REIMS
SQLite-only configuration
"""

import uvicorn
import sys
from pathlib import Path

# Add the backend path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    try:
        # Import and run the FastAPI app
        from backend.api.main import app
        
        print("Starting REIMS Backend Server on http://localhost:8001")
        print("Press Ctrl+C to stop the server")
        print("Note: Backend uses FIXED port 8001 - will fail if port is in use")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)