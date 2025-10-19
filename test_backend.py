#!/usr/bin/env python3
"""
Minimal backend test for REIMS - Health check only
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="REIMS API", description="Real Estate Information Management System API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "REIMS Backend is running"}

@app.get("/")
def root():
    return {"message": "REIMS API is running", "docs": "/docs"}

if __name__ == "__main__":
    print("Starting minimal REIMS Backend...")
    uvicorn.run(app, host="0.0.0.0", port=8001)