#!/usr/bin/env python3
"""
REIMS Backend Starter - PostgreSQL Mode
This script sets environment variables BEFORE importing any modules
"""

import os
import sys

# CRITICAL: Set environment variables BEFORE any imports
# This ensures they're available before load_dotenv() is called
os.environ['DATABASE_URL'] = 'postgresql://postgres:dev123@localhost:5432/reims'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
os.environ['MINIO_ENDPOINT'] = 'localhost:9000'
os.environ['MINIO_ACCESS_KEY'] = 'minioadmin'
os.environ['MINIO_SECRET_KEY'] = 'minioadmin'
os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'

print("\n" + "="*70)
print("🚀 REIMS BACKEND - POSTGRESQL MODE")
print("="*70)
print("\n✅ Environment variables set:")
print(f"   DATABASE_URL: {os.environ['DATABASE_URL']}")
print(f"   REDIS_URL: {os.environ['REDIS_URL']}")
print(f"   MINIO_ENDPOINT: {os.environ['MINIO_ENDPOINT']}")
print("\n⏳ Starting uvicorn server...")
print("   Look for: 'Connected to PostgreSQL'")
print("="*70 + "\n")

# Now start uvicorn
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )














