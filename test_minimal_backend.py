from fastapi import FastAPI

# Create a minimal FastAPI app for testing
app = FastAPI(title="REIMS API Test", description="Minimal test version")

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}

@app.get("/")
def root():
    return {"message": "REIMS Backend API", "version": "1.0.0"}