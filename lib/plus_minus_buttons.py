import cv2
from geometry_utility import create_rectangle_array, point_intersects
from shapely.geometry import Point


class PlusMinusButtons:
    def __init__(
        self,
        x,
        y,
        label="Label",
        label_offset_x=50,
        min_value=1,
        max_value=100,
        visible=True,
        text_color=(255, 255, 255),
        btm_text_color=(4, 201, 126),
        back_color=(255, 255, 255),
    ):
        self.x1 = x
        self.y1 = y
        self.label = label
        self.x2 = x + 50
        self.y2 = y + 50
        self.text_color = text_color
        self.btm_text_color = btm_text_color
        self.back_color = back_color
        self.label_offset_x = label_offset_x
        self.visible = visible
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = 1

    def set_visible(self, isVisible):
        self.visible = isVisible

    def set_current_value(self, current_value):
        if current_value > self.min_value and current_value < self.max_value:
            self.current_value = int(current_value)

    def get_current_value(self):
        return self.current_value

    def draw(self, img):
        if self.visible:
            cv2.rectangle(
                img, (self.x1, self.y1), (self.x2, self.y2), self.back_color, cv2.FILLED
            )
            cv2.putText(
                img,
                "+",
                ((self.x1 + 12), (self.y1 + 35)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                self.btm_text_color,
                2,
                cv2.LINE_AA,
            )
            cv2.rectangle(
                img,
                ((self.x1 + 100), self.y1),
                ((self.x2 + 100), self.y2),
                self.back_color,
                cv2.FILLED,
            )
            cv2.putText(
                img,
                "-",
                ((self.x1 + 112), (self.y1 + 35)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                self.btm_text_color,
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                img,
                self.label,
                (self.label_offset_x, self.y2),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                self.text_color,
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                img,
                str(self.current_value),
                (self.x2 + 150, self.y2),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                self.text_color,
                2,
                cv2.LINE_AA,
            )
        return img

    def plus_btn_click(self, x, y):
        if self.visible:
            if self.max_value > self.current_value:
                point = Point(x, y)
                bounding_box = create_rectangle_array(
                    (self.x1, self.y1), (self.x2, self.y2)
                )
                if point_intersects(point, bounding_box):
                    self.current_value += 1

    def minus_btn_click(self, x, y):
        if self.visible:
            if self.min_value < self.current_value:
                point = Point(x, y)
                bounding_box = create_rectangle_array(
                    (self.x1 + 100, self.y1), ((self.x2 + 100), self.y2)
                )
                if point_intersects(point, bounding_box):
                    self.current_value -= 1
