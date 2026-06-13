from shapely.geometry import Point, Polygon
from typing import Any
import json


def is_point_inside_boundary(
    lat: float,
    lng: float,
    boundary_coordinates: list[list[float]],
) -> bool:
    """
    Check if a GPS point is inside a farm polygon boundary.
    boundary_coordinates: list of [lat, lng] pairs
    Returns True if inside or within 50m buffer.
    """
    try:
        if len(boundary_coordinates) < 3:
            return False

        # Build polygon from [lat, lng] → shapely uses (x=lng, y=lat)
        polygon_points = [(c[1], c[0]) for c in boundary_coordinates]
        polygon = Polygon(polygon_points)

        # Add ~50 metre buffer (roughly 0.00045 degrees)
        buffered = polygon.buffer(0.00045)

        point = Point(lng, lat)
        return buffered.contains(point)

    except Exception:
        # If geometry fails, don't block the upload
        return False


def compute_polygon_center(
    coordinates: list[list[float]],
) -> tuple[float, float]:
    """Returns (center_lat, center_lng)."""
    lats = [c[0] for c in coordinates]
    lngs = [c[1] for c in coordinates]
    return sum(lats) / len(lats), sum(lngs) / len(lngs)