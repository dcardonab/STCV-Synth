"""Geometry functions."""

# Python Libraries
from typing import Tuple

# Third-Party Libraries
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


def create_rectangle_array(
        pt1: Tuple[int, int],
        pt2: Tuple[int, int]) -> list:
    """
    This method takes two points and extracts a polygon boundary from it.
    """
    return [
        (pt1[0], pt1[1]),
        (pt1[0], pt2[1]),
        (pt2[0], pt2[1]),
        (pt2[0], pt1[1])
    ]


def polygon_bounds(polygon_array):
    """
    Build a polygon from an array, and return the bounds.
    """
    polygon = Polygon(polygon_array)
    return polygon.bounds


def point_intersects(point, polygon_array):
    """
    point_intersects is function that returns true if the point
    passed in falls in the boundary of the polygon
    """
    polygon = Polygon(polygon_array)
    return polygon.contains(Point(point))
