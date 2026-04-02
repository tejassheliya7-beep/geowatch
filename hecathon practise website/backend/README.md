# GeoWatch – AI Powered Satellite Change Detection System (Backend)

This is the FastAPI-based backend for the GeoWatch project, designed to provide high-performance geospatial analysis, satellite data fetching, AI change detection, and compliance reporting.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8+
- [Google Earth Engine (GEE)](https://code.earthengine.google.com/) account (required for satellite fetching)
- CUDA-enabled GPU (optional but recommended for AI detection)

### 2. Setup

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

* **GEE Credentials**: Ensure you have authenticated your local machine by running `earthengine authenticate`.
* **AI Model Weights**: Place your `.pth` ChangeFormer model weights in `models/weights.pth` or configure the path in `services/ai_model.py`.

### 4. Running the Server

```bash
# Run with auto-reload for development
python main.py
```

The API will be available at `http://localhost:8000`.  
Explore the interactive API documentation at:  
- **Swagger UI**: `http://localhost:8000/docs`  
- **Redoc**: `http://localhost:8000/redoc`

## 🛠 Project Structure

- `main.py`: Entry point for the FastAPI application.
- `routes/`: Individual API endpoints for Area, Satellite, Detection, Compliance, and Reports.
- `services/`: Core logic and service integrations (Grid, GEE, AI, Compliance, Report).
- `models/`: Pydantic schemas for data validation and response formatting.
- `requirements.txt`: List of dependencies.

## 🔬 Core Functionality

- **Grid Generation**: Uses UTM projections to accurately divide areas into 1km x 1km tiles.
- **Satellite Data Fetching**: Directly integrates with Sentinel-2 via Google Earth Engine.
- **AI Change Detection**: Uses a ChangeFormer-based architecture for high-accuracy change classification.
- **Compliance Engine**: Rule-based checking against urban zoning regulations (AUDA).
- **Report Generation**: Produces professional PDF summaries for legal and urban planning review.

---
**GeoWatch AI** – Smart Monitoring. Better Governance.
