import geopandas as gpd
from shapely.geometry import Polygon, mapping
import numpy as np
from typing import List, Dict, Any

class GridService:
    @staticmethod
    def generate_grid(geojson_polygon: Dict[str, Any], tile_size_km: float = 1.0) -> List[Dict[str, Any]]:
        """
        Optimized vectorized grid generation for high-performance tiling.
        """
        try:
            # Load and Project
            gdf = gpd.GeoDataFrame.from_features([{"geometry": geojson_polygon, "properties": {}}], crs="EPSG:4326")
            # Calculate UTM zone without calling .centroid on geographic CRS
            bounds = gdf.total_bounds
            lon, lat = (bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2
            utm_zone = int((lon + 180) / 6) + 1
            utm_crs = f"+proj=utm +zone={utm_zone} +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
            gdf_utm = gdf.to_crs(utm_crs)
            
            # Grid Bounds
            xmin, ymin, xmax, ymax = gdf_utm.total_bounds
            tile_size_m = tile_size_km * 1000
            
            # Vectorized Grid Generation
            cols = np.arange(xmin, xmax, tile_size_m)
            rows = np.arange(ymin, ymax, tile_size_m)
            
            # Create all grid polygons at once
            polygons = []
            for x in cols:
                for y in rows:
                    polygons.append(Polygon([(x, y), (x + tile_size_m, y), (x + tile_size_m, y + tile_size_m), (x, y + tile_size_m)]))
            
            # Filter polygons that intersect the area in one vectorized operation
            grid_gdf_utm = gpd.GeoDataFrame({"geometry": polygons}, crs=utm_crs)
            intersecting_grid = grid_gdf_utm[grid_gdf_utm.intersects(gdf_utm.geometry[0])]
            
            # Batch Project entire grid back to WGS84
            res_gdf = intersecting_grid.to_crs("EPSG:4326")
            
            # Format results
            tiles = []
            for idx, row in enumerate(res_gdf.itertuples()):
                b = row.geometry.bounds
                tiles.append({
                    "id": f"tile_{idx+1}",
                    "xmin": b[0], "ymin": b[1], "xmax": b[2], "ymax": b[3],
                    "center": [row.geometry.centroid.x, row.geometry.centroid.y],
                    "geometry": mapping(row.geometry)
                })
            
            return tiles
        except Exception as e:
            return [{"error": str(e)}]

# Example usage (uncomment only for testing):
# if __name__ == "__main__":
#     sample_polygon = {
#         "type": "Polygon",
#         "coordinates": [[
#             [72.5, 23.0], [72.6, 23.0], [72.6, 23.1], [72.5, 23.1], [72.5, 23.0]
#         ]]
#     }
#     svc = GridService()
#     res = svc.generate_grid(sample_polygon)
#     print(f"Generated {len(res)} tiles")
