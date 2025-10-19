from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from client import queue_client

app = FastAPI(title="REIMS Queue Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DocumentProcessingRequest(BaseModel):
    document_id: str
    metadata: Dict[str, Any]

@app.post("/process")
async def enqueue_document(request: DocumentProcessingRequest):
    """
    Add a document to the processing queue
    """
    try:
        job_id = queue_client.enqueue_document(request.document_id, request.metadata)
        return {
            "status": "queued",
            "job_id": job_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status of a processing job
    """
    try:
        status = queue_client.get_job_status(job_id)
        if status["status"] == "not_found":
            raise HTTPException(status_code=404, detail="Job not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/queue/info")
async def get_queue_info():
    """
    Get information about the current state of the queues
    """
    try:
        return queue_client.get_queue_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8002, reload=True)