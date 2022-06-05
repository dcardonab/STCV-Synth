"""
GUI elements for interaction via CV.
"""

# Python Libraries
from typing import Tuple, Union

# Third-Party Libraries
import cv2
from shapely.geometry import Point

# Local Files
from constants import BPM_SUBDIVISIONS
from geometry_utility import create_rectangle_array, point_intersects, polygon_bounds


class PlusMinusButtons:
    """
    Base Class for Button-based GUI elements.
    """
    def __init__(
        self, x: int, y: int,
        label: str = "Label", label_offset_x: int = 50,
        min_value: int = 1, max_value: int = 100,
        text_color: Tuple[int, int, int] = (255, 255, 255),
        btm_text_color: Tuple[int, int, int] = (4, 201, 126),
        back_color: Tuple[int, int, int] = (255, 255, 255),
    ) -> None:

        # Screen Coordinates.
        self.top_left = (x, y)
        self.bottom_right = (x + 50, y + 50)    # Length and Height

        # Button Design.
        self.label = label                              # Button Label
        self.text_color = text_color                    # Text color for label
        self.btm_text_color = btm_text_color            # Text color for botton
        self.back_color = back_color                    # BG color
        self.label_offset_x = self.top_left[0] + label_offset_x  # Distance from button

        # Create a bounding boxes to detect collisions against the buttons.
        self.minus_bounding_box = create_rectangle_array(
            self.top_left, self.bottom_right)
        self.plus_bounding_box = create_rectangle_array(
            (self.top_left[0] + 100, self.top_left[1]),
            (self.bottom_right[0] + 100, self.bottom_right[1])
        )

        # Set range of GUI element.
        self.min_value = min_value
        self.max_value = max_value

        self.value = None

    def set_value(self, value: int) -> None:
        """ Update current value if does not exceed min and max values. """
        if self.max_value >= value >= self.min_value:
            self.value = int(value)

    def set_max_value(self, value: int) -> None:
        """ Set upper bound of the button selector. """
        self.max_value = value
        if self.value > self.max_value:
            self.value = self.max_value

    def render(self, img):
        """ Render button on top of the camera captured image. """
        x_1, y_1 = self.top_left
        x_2, y_2 = self.bottom_right

        # Create the minus button rectangle.
        cv2.rectangle(
            img, self.top_left, self.bottom_right,
            self.back_color, cv2.FILLED
        )

        # Add the 'minus' sign text.
        # The order of drawing sets the display order.
        cv2.putText(
            img, "-", (x_1 + 12, y_1 + 35),
            cv2.FONT_HERSHEY_SIMPLEX, 1, self.btm_text_color,
            2, cv2.LINE_AA
        )

        # Create the plus button rectangle.
        cv2.rectangle(
            img, (x_1 + 100, y_1), (x_2 + 100, y_2),
            self.back_color, cv2.FILLED,
        )

        # Add the 'plus' sign text.
        cv2.putText(
            img, "+", (x_1 + 112, y_1 + 35),
            cv2.FONT_HERSHEY_SIMPLEX, 1, self.btm_text_color,
            2, cv2.LINE_AA
        )

        # Draw the label of the control.
        cv2.putText(
            img, self.label, (self.label_offset_x, y_2),
            cv2.FONT_HERSHEY_SIMPLEX, 1, self.text_color,
            2, cv2.LINE_AA
        )

        # Draw the currently selected value
        cv2.putText(
            img, str(self.value), (x_2 + 150, y_2),
            cv2.FONT_HERSHEY_SIMPLEX, 1, self.text_color,
            2, cv2.LINE_AA
        )

        # Return drawn controls overlaid on the image.
        return img

    def minus_btn_check_collision(self, x: int, y: int) -> Union[bool, None]:
        """
        Processes events for the minus botton collision (i.e., the
        intersection between a finger landmark and the button).
        """
        # Ensure that decreasing the value would not exceed minumum.
        if self.min_value < self.value:
            point = Point(x, y)
            # Decrease value if there was a collision.
            if point_intersects(point, self.minus_bounding_box):
                self.set_value(self.value - 1)
                return True

        return False

    def plus_btn_check_collision(self, x: int, y: int) -> Union[bool, None]:
        """
        Processes events for the plus botton collision (i.e., the
        intersection between a finger landmark and the button).
        """
        # Ensure that increasing the value would not exceed maximum.
        if self.max_value > self.value:
            # Convert coordinates into a point.
            point = Point(x, y)
            # Increase value if there was a collision.
            if point_intersects(point, self.plus_bounding_box):
                self.set_value(self.value + 1)
                return True

        return False


class SubdivisionsButtons(PlusMinusButtons):
    """
    This class overrides the 'set_value()' method in order to map the
    subdivision values to the value declared in the 'BPM_SUBDIVISIONS' dict.
    The plus and minus buttons will change the selected dictionary value.
    """
    def init_value(self, value: int) -> None:
        """
        Initialize value to prevent an NoneType error when using the setter.
        """
        self.value = value

    def set_value(self, value: int) -> None:
        if value > self.value:
            # The values here increase only by one step. Since the
            # values are pulled from a dictionary, the key
            # is the value of that can be selected
            if self.value in BPM_SUBDIVISIONS:
                keys = list(BPM_SUBDIVISIONS)
                index = keys.index(self.value)
                if index + 1 < len(keys):
                    self.value = keys[index + 1]

        elif value < self.value:
            if self.value in BPM_SUBDIVISIONS:
                keys = list(BPM_SUBDIVISIONS)
                index = keys.index(self.value)
                if index - 1 >= 0:
                    self.value = keys[index - 1]


class Menu:
    """ Menus are lists of items and it is mainly used for the scales. """
    def __init__(
        self, x: int, y: int,
        menu_dictionary: dict,
        alpha: float = 0.7,
        btm_text_color: Tuple[int, int, int] = (0, 255, 0),
        columns: int = 1, rows: int = 2
    ) -> None:
        self.start_coords = (x, y)
        self.alpha = alpha      # Opacity.
        self.btm_text_color = btm_text_color
        self.columns = columns
        self.rows = rows
        self.menu_items = menu_dictionary
        self.menu_items_coordinates = {}

        self.value = None

        self._init_menu_items_coordinates()

    def get_value(self) -> str:
        """
        Return the scale name to update the synth if it changed.
        The name of the scale is contained in the first value of the tuple.
        """
        return self.value[0]

    def init_value(self, value: str) -> None:
        """ Store the name of the scale and the coordinates as a tuple. """
        self.value = (value, self.menu_items_coordinates[value])

    def _set_value(self, value: Tuple) -> None:
        """ Update the chosen scale and coordinates tuple. """
        self.value = value

    def check_collision(self, x: int, y: int) -> Union[bool, None]:
        """ Check for collision against menu boxes. """
        # Process collisions with menu items.
        for k, v in self.menu_items_coordinates.items():
            if point_intersects((x, y), v):
                self._set_value((k, v))
                return True

        return False

    def render(self, img):
        """ Render function for the whole menu. """
        for item in self.menu_items.keys():
            overlay = self.render_item(
                self.menu_items_coordinates[item][0],
                self.menu_items_coordinates[item][2],
                item, img
            )

        image_new = cv2.addWeighted(
            overlay, self.alpha, img, 1 - self.alpha, 0
        )

        return image_new

    def render_item(
        self,
        btm_left: Tuple[int, int], top_right: Tuple[int, int],
        item: str, overlay_img
    ):
        """ Render function for the individual boxes. """
        if item in self.value:
            cv2.rectangle(
                overlay_img,
                self.value[item][0],
                self.value[item][2],
                (255, 255, 255),
                cv2.FILLED,
            )

        cv2.putText(
            overlay_img,
            item,
            (btm_left[0], btm_left[1] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            self.btm_text_color,
            2,
            cv2.LINE_AA,
        )

        cv2.rectangle(
            overlay_img, btm_left, top_right, self.btm_text_color, 1
        )

        return overlay_img

    def _init_menu_items_coordinates(self):
        """
        Add screen coordinates for each element in the menu.
        """
        # Init X and Y for creating menu items
        x, y = self.start_coords

        row = 0
        column = 0
        for item in self.menu_items.keys():
            if column < self.columns and row >= self.rows:
                row = 0
                x += 250
                y = self.start_coords[1]

            self.menu_items_coordinates[item] = create_rectangle_array(
                (x, y + 5), (x + 240, y - 50)
            )

            y += 70
            row += 1

            if row == self.rows - 1:
                column += 1


class Slider:
    """
    This class creates a slider control where the data value falls inside
    the bounding rectangle.
    """
    def __init__(
        self, bpm: int = 100, textlabel: str = "BPM",
        x: int = 1000, y: int = 140, min_value: int = 40, max_value: int = 220
    ) -> None:
        # Setting the text to be displayed before the control, to the left
        # of the slider
        self.bpm = bpm
        self.textlabel = textlabel
        # Intializing control layout coordinates
        self.top_left = (x, y)
        self.bottom_right = (x + 225, y + 50)

        self.min_value = min_value
        self.max_value = max_value

        self.bounding_box = create_rectangle_array(
            self.top_left, self.bottom_right
        )

    def set_bpm(self, bpm):
        """ Set the BPM slider based on the provided range. """
        if int(bpm) < self.min_value:
            bpm = self.min_value
        if int(bpm) > self.max_value:
            bpm = self.max_value
        self.bpm = bpm

    def render(self, img):
        """ Draw the slider control. """

        x_1, y_1 = self.top_left

        # Create a containing  retangle
        cv2.rectangle(
            img, self.top_left, self.bottom_right, (192, 84, 80), 3
        )

        # Create a rectangle that displays the current setting
        cv2.rectangle(
            img, self.top_left, (int(self.bpm + x_1), self.bottom_right[1]),
            (255, 255, 255), cv2.FILLED)

        # Place label text the left of the containing rectangle
        cv2.putText(
            img, self.textlabel, (x_1 - 70, y_1 + 50),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255),
            2, cv2.LINE_AA
        )

        # Placing label text inside slider bar
        cv2.putText(
            img, str(int(self.bpm)), (x_1 + 10, y_1 + 40),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (4, 201, 126),
            2, cv2.LINE_AA
        )

        return img

    def set_sliders(self, img, x_coord, y_coord):
        """
        The method exists to checks to see if the user is
        trying to adjust the slider by intersection of the
        containing control

        This method takes the opencv image, but currently adds
        nothing to it.
        """
        # Pickup BPM Control
        point = Point(x_coord, y_coord)

        if point_intersects(point, self.bounding_box):
            bounds = polygon_bounds(self.bounding_box)
            # The countrol needs to read the X1 boundary
            # to avoid hardcoding of values
            self.set_bpm(int(x_coord - bounds[0]))

        return img
