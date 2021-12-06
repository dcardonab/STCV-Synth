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
        # Top
        self.x1 = x
        # Left
        self.y1 = y
        # Button Label
        self.label = label
        #Right (or Length)
        self.x2 = x + 50
        # height
        self.y2 = y + 50
        # Text color for label
        self.text_color = text_color
        # Text color for botton
        self.btm_text_color = btm_text_color
        # Back color of text button
        self.back_color = back_color
        # Label offset is sets the space to place the 
        # label away from the button
        self.label_offset_x = label_offset_x
        # Sets control visibility.  If visible is
        # false, the control will not process finger motions
        self.visible = visible
        # The value below which the minus button will not go
        self.min_value = min_value
        # The maximum value which a button click will set
        self.max_value = max_value
        # Sets the default value
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
            
            # Creates the plus button rectangle
            cv2.rectangle(
                img, (self.x1, self.y1), (self.x2, self.y2), self.back_color, cv2.FILLED
            )
            # Places the place above the button rectangle
            # The order of drawing sets the display order
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

            # creates the second button
            cv2.rectangle(
                img,
                ((self.x1 + 100), self.y1),
                ((self.x2 + 100), self.y2),
                self.back_color,
                cv2.FILLED,
            )
            # The following places the minus text on one of the buttons. 
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

            # The following sets the label text of the control
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
            # The following sets the current selected value
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
        # processes the events for the plus botton click
        # A button click is simply looking for a finger 
        # landmark intersection
        if self.visible:
            if self.max_value > self.current_value:
                point = Point(x, y)
                bounding_box = create_rectangle_array(
                    (self.x1, self.y1), (self.x2, self.y2)
                )
                if point_intersects(point, bounding_box):
                    self.current_value += 1

    def minus_btn_click(self, x, y):
        # processes the events for the minus botton click
        # A button click is simply looking for a finger 
        # landmark intersection
        if self.visible:
            if self.min_value < self.current_value:
                point = Point(x, y)
                bounding_box = create_rectangle_array(
                    (self.x1 + 100, self.y1), ((self.x2 + 100), self.y2)
                )
                if point_intersects(point, bounding_box):
                    self.current_value -= 1
