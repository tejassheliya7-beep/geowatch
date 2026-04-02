import sys
import os

print("\n" + "="*40)
print("   GeoWatch AI Backend Diagnostic")
print("="*40)
print(f"Python Version: {sys.version}")
print(f"Current Directory: {os.getcwd()}")
print("-"*40)

modules = [
    "fastapi", "uvicorn", "geopandas", "shapely", 
    "ee", "torch", "rasterio", "reportlab", "pydantic"
]

missing = []
for mod in modules:
    try:
        __import__(mod)
        print(f" [OK]    {mod}")
    except ImportError:
        print(f" [ERROR] {mod} is MISSING")
        missing.append(mod)

if missing:
    print("\n" + "!"*40)
    print("❌ CRITICAL: Missing Dependencies!")
    print(f"Run this command to fix: \npip install -r requirements.txt")
    print("!"*40)
else:
    print("\n✅ All dependencies are installed.")
    print("Checking if port 8000 is available and starting server...")
    print("-"*40)
    try:
        import uvicorn
        # Import the app to check for errors in routes/models
        from main import app
        print("✅ Backend logic is valid. Initializing server...")
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except Exception as e:
        print(f"\n❌ FATAL ERROR DURING STARTUP:")
        print(str(e))
        import traceback
        traceback.print_exc()
    print("="*40)
