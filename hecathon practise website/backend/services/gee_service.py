import ee
import os
from typing import Dict, Any, List
import datetime

class GEEService:
    """
    Service for interacting with Google Earth Engine (GEE).
    Fetches and processes Sentinel-2 satellite imagery.
    """
    _cache = {}  # Class-level cache for efficiency

    def __init__(self, service_account_json: str = None):
        """
        Initialize the GEE connection.
        If GEE_SERVICE_ACCOUNT and GEE_JSON_PATH are in .env, use them.
        """
        try:
            # Try to get credentials from .env first
            sa_email = os.getenv("GEE_SERVICE_ACCOUNT")
            sa_key_path = os.getenv("GEE_JSON_PATH")

            if sa_email and sa_key_path and os.path.exists(sa_key_path):
                print(f"GEE: Authenticating with Service Account: {sa_email}")
                credentials = ee.ServiceAccountCredentials(sa_email, sa_key_path)
                ee.Initialize(credentials)
            elif service_account_json and os.path.exists(service_account_json):
                # Fallback to direct parameter if provided
                credentials = ee.ServiceAccountCredentials("gee-access@geowatch-ai.iam.gserviceaccount.com", service_account_json)
                ee.Initialize(credentials)
            else:
                # Fallback to default auth
                print("GEE: Using default authentication...")
                ee.Initialize()
                
            print("✅ GEE: Backend Connected Successfully.")
        except Exception as e:
            print(f"❌ GEE: Authentication failed: {e}")
            if "not registered" in str(e).lower():
                print("\n⚠️ ACTION REQUIRED: Your project is not registered for Earth Engine.")
                print("1. Visit: https://console.cloud.google.com/earth-engine/configuration?project=geowatch-ai")
                print("2. Ensure 'Earth Engine API' is enabled and you have a valid cloud project selected.")
            else:
                print("Tip: Ensure your service_account.json is in the 'backend/' folder.")

    def fetch_sentinel_data(self, tile_coords: List[float], date_start: str, date_end: str, cloud_threshold: float = 10.0) -> Dict[str, Any]:
        """
        Fetch Sentinel-2 imagery for a specific bounding box and date range.
        Input: [xmin, ymin, xmax, ymax]
        """
        # 🧪 Efficiency Caching
        cache_key = f"{tile_coords}_{date_start}_{date_end}"
        if cache_key in self._cache:
            print(f"GEE: Returning Cached Result for {date_start}")
            return self._cache[cache_key]

        try:
            # Create a geometry from bounding box
            region = ee.Geometry.Rectangle(tile_coords)
            
            # Load Sentinel-2 Collection 2, Level-1C
            collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                            .filterBounds(region) \
                            .filterDate(date_start, date_end) \
                            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_threshold)) \
                            .sort('CLOUDY_PIXEL_PERCENTAGE')
            
            # Select the median composite (calculated from all clear images in the search window)
            # This is much more accurate for 10-year analysis as it removes temporary seasonal noise.
            image = collection.median().clip(region)
            
            # Generate a visualizing URL (RGB)
            vis_params = {
                'min': 0.0,
                'max': 3000,
                'bands': ['B4', 'B3', 'B2'],
            }
            
            url = image.getThumbURL({
                'params': vis_params, 
                'region': region, 
                'format': 'png',
                'crs': 'EPSG:3857', # Web Mercator for consistent projections
                'dimensions': 512    # Fixed size for better performance
            })
            
            # Metadata fetch
            # Note: Median composites have limited metadata properties compared to single images
            info = image.getInfo() or {}
            props = info.get('properties', {})
            
            return {
                "tile_id": "tile_batch",
                "image_url": url,
                "metadata": {
                    "id": info.get('id', 'composite-median'),
                    "date": props.get('DATATAKE_IDENTIFIER', '10-Year Composite'),
                    "cloud_cover": props.get('CLOUDY_PIXEL_PERCENTAGE', 0.5), # Median reduces clouds significantly
                    "bands": info.get('bands', [{'id': 'B4'}, {'id': 'B3'}, {'id': 'B2'}])
                }
            }
        except Exception as e:
            print(f"Error fetching GEE data: {str(e)}")
            return {"error": str(e), "message": "Failed to fetch satellite imagery"}

# Example (uncomment only for testing):
# if __name__ == "__main__":
#     svc = GEEService()
#     res = svc.fetch_sentinel_data([72.5, 23.0, 72.6, 23.1], "2023-01-01", "2023-12-31")
#     print(res.get("image_url"))
