from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

point = Point(0.5, 0.5)

def create_rectangle_array(pt1, pt2):
    points = []
    points.append((pt1[0], pt1[1]))
    points.append((pt1[0], pt2[1]))
    points.append((pt2[0], pt2[1]))
    points.append((pt2[0], pt1[1]))
    return points

def point_intersects(point, polygon_array):
    polygon = Polygon(polygon_array)
    return polygon.contains(Point(point))