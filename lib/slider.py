import cv2
from shapely.geometry import Point
from geometry_utility import create_rectangle_array, point_intersects


class Slider:

    def __init__(self, BPM=100, visible=True):
        self.BPM = BPM
        self.visible = visible

    def draw_controls(self, img):
        cv2.rectangle(img, (1000, 250), (1225, 300), (192, 84, 80), 3)
        cv2.rectangle(
            img, (1000, 250), (int(self.BPM + 1000), 300), (255, 255, 255), cv2.FILLED
        )
        cv2.putText(
            img,
            "BPM",
            (930, 300),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            img,
            str(int(self.BPM)),
            (1010, 290),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (4, 201, 126),
            2,
            cv2.LINE_AA,
        )
        return img

    def set_sliders(self, img, x1, y1):
        # Pickup BPM Control
        point = Point(x1, y1)
        bpm_rectangle = create_rectangle_array((1000, 250), (1220, 300))
        if point_intersects(point, bpm_rectangle):
            self.BPM = int(x1 - 1000)

        return img
