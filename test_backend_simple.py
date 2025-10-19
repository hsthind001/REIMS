#!/usr/bin/env python3
"""
Ultra-simple backend for testing REIMS upload functionality
"""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uuid
from datetime import datetime
import os

# Create FastAPI app
app = FastAPI(title="REIMS Test Backend", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage for uploaded files
UPLOAD_DIR = "test_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...), property_id: str = Form(...)):
    """Upload a document"""
    try:
        # Generate unique ID
        doc_id = str(uuid.uuid4())
        
        # Save file
        file_content = await file.read()
        filename = f"{doc_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Return success response
        return {
            "document_id": doc_id,
            "filename": file.filename,
            "file_size": len(file_content),
            "property_id": property_id,
            "status": "uploaded",
            "message": "File uploaded successfully"
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }

@app.get("/api/documents")
async def list_documents():
    """List uploaded documents"""
    files = []
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            if "_" in filename:
                doc_id, original_name = filename.split("_", 1)
                files.append({
                    "document_id": doc_id,
                    "filename": original_name,
                    "stored_filename": filename
                })
    
    return {"documents": files, "total": len(files)}

if __name__ == "__main__":
    import uvicorn
    print("Starting REIMS Test Backend on http://localhost:8002")
    print("Upload endpoint: POST /api/documents/upload")
    print("Health check: GET /health")
    uvicorn.run(app, host="0.0.0.0", port=8002)