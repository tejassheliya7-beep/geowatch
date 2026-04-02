from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

# Load Environment Variables (.env)
load_dotenv()

# Import Routers
from routes import area, satellite, detection, compliance, report

app = FastAPI(
    title="GeoWatch AI Backend",
    description="AI Powered Satellite Change Detection System - FastAPI Backend.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
# Adjust origins for production (e.g., http://localhost:5173 for Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root Endpoint
@app.get("/")
async def root():
    return {
        "project": "GeoWatch AI",
        "status": "Online",
        "message": "Welcome to the GeoWatch Satellite Intelligence API."
    }

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "Healthy", "env": os.getenv("ENV", "development")}

# Include Routers
app.include_router(area.router)
app.include_router(satellite.router)
app.include_router(detection.router)
app.include_router(compliance.router)
app.include_router(report.router)

# Static Files Serving for Reports
if not os.path.exists("reports"):
    try:
        os.makedirs("reports")
    except:
        pass
app.mount("/static", StaticFiles(directory="reports"), name="static")

if __name__ == "__main__":
    # In production, run with gunicorn or uvicorn main:app
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
