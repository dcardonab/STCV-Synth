# Python Libraries
from typing import Tuple

# Third-Party Libraries
import cv2
from shapely.geometry import Point

# Local Files
from constants import BASE_MULT_OPTIONS, BPM_SUBDIVISIONS, SCALES
from geometry_utility import create_rectangle_array, point_intersects, polygon_bounds


class PlusMinusButtons:
    """
    Base Class for Button-based GUI elements.
    """
    def __init__(
        self, x: int, y: int,
        label: str = "Label", label_offset_x: int = 50,
        min_value: int = 1, max_value: int = 100, value: int = 1,
        visible: bool = True,
        text_color: Tuple[int, int, int] = (255, 255, 255),
        btm_text_color: Tuple[int, int, int] = (4, 201, 126),
        back_color: Tuple[int, int, int] = (255, 255, 255),
    ) -> None:

        # Screen Coordinates.
        self.x1 = x         # Left
        self.y1 = y         # Top
        self.x2 = x + 50    # Right (Length)
        self.y2 = y + 50    # Bottom (Height)

        # Button Design.
        self.label = label                              # Button Label
        self.text_color = text_color                    # Text color for label
        self.btm_text_color = btm_text_color            # Text color for botton
        self.back_color = back_color                    # Back color of text button
        self.label_offset_x = self.x1 + label_offset_x  # Distance from the button

        # Initialize range and value of GUI element.
        self.set_range(min_value, max_value)
        self.set_init_value(value)

        self.set_visible(visible)

    def set_visible(self, isVisible: bool) -> None:
        """
        Set visibility to toggle detection of finger motions.
        If visible is false, the control will not process finger motions.
        """
        self.visible = isVisible

    def set_init_value(self, value: int) -> None:
        """
        Initialize GUI element value.
        """
        self.value = value

    def set_range(self, min_value: int, max_value: int) -> None:
        """
        Set the range of values accessible by the button.
        """
        self.min_value = min_value
        self.max_value = max_value

    def set_value(self, value: int) -> None:
        """
        Update current value if does not exceed min and max values.
        """
        if value >= self.min_value and value <= self.max_value:
            self.value = int(value)

    def get_value(self) -> int:
        return self.value

    def draw(self, img):
        # Only draw controls and process inputs when the GUI element is visible
        if self.visible:
            # Create the minus button rectangle.
            cv2.rectangle(
                img, (self.x1, self.y1), (self.x2, self.y2),
                self.back_color, cv2.FILLED
            )

            # Add the 'minus' sign text.
            # The order of drawing sets the display order.
            cv2.putText(
                img, "-", ( (self.x1 + 12), (self.y1 + 35) ),
                cv2.FONT_HERSHEY_SIMPLEX, 1, self.btm_text_color,
                2, cv2.LINE_AA
            )

            # Create the plus button rectangle.
            cv2.rectangle(
                img, (self.x1 + 100, self.y1), (self.x2 + 100, self.y2),
                self.back_color, cv2.FILLED,
            )

            # Add the 'plus' sign text.
            cv2.putText(
                img, "+", ( (self.x1 + 112), (self.y1 + 35) ),
                cv2.FONT_HERSHEY_SIMPLEX, 1, self.btm_text_color,
                2, cv2.LINE_AA
            )

            # Draw the label of the control.
            cv2.putText(
                img, self.label, (self.label_offset_x, self.y2),
                cv2.FONT_HERSHEY_SIMPLEX, 1, self.text_color,
                2, cv2.LINE_AA
            )

            # Draw the currently selected value
            cv2.putText(
                img, str(self.value), (self.x2 + 150, self.y2),
                cv2.FONT_HERSHEY_SIMPLEX, 1, self.text_color,
                2, cv2.LINE_AA
            )

        # Return drawn controls overlaid on the image.
        return img

    def minus_btn_click(self, x: int, y: int) -> None:
        """
        Processes events for the minus botton collision (i.e., the
        intersection between a finger landmark and the button).
        """
        # Only process collisions when the button is visible.
        if self.visible:
            # Ensure that decreasing the value would not exceed minumum.
            if self.min_value < self.value:
                point = Point(x, y)
                # Create bounding box around button for collision detection.
                bounding_box = create_rectangle_array(
                    (self.x1, self.y1), (self.x2, self.y2)
                )
                # Decrease value if there was a collision.
                if point_intersects(point, bounding_box):
                    self.set_value(self.value - 1)

    def plus_btn_click(self, x, y):
        """
        Processes events for the plus botton collision (i.e., the
        intersection between a finger landmark and the button).
        """
        # Only process collisions when the button is visible.
        if self.visible:
            # Ensure that increasing the value would not exceed maximum.
            if self.max_value > self.value:
                # Convert coordinates into a point.
                point = Point(x, y)
                # Create bounding box around button for collision detection.
                bounding_box = create_rectangle_array(
                    (self.x1 + 100, self.y1), (self.x2 + 100, self.y2)
                )
                # Increase value if there was a collision.
                if point_intersects(point, bounding_box):
                    self.set_value(self.value + 1)


class GUI_OctaveBase(PlusMinusButtons):
    """
    In addition to what is declared in the PlusMinusButtons class,
    the PlusMinusOctaveBase returns the tuple contained in constants.py
    that corresponds to the current value of the GUI element.
    The tuple contains the multiplier that will be assigned to the tonal
    center (i.e., determines the lowest frequency of the synth), and the
    second value contains the maximum octave range for that multiplier.
    """
    def get_value_constant(self):
        value = self.get_value()
        # Ensure that value exists as a dictionary option.
        if str(value) in BASE_MULT_OPTIONS.keys():
            return BASE_MULT_OPTIONS[str(value)]


class GUI_Subdivions(PlusMinusButtons):
    """
    This class overrides the 'set_value()' method in order to map the
    subdivision values to the value declared in the 'BPM_SUBDIVISIONS' dict.
    The plus and minus buttons will change the selected dictionary value.
    """
    def set_value(self, value: int) -> None:
        if value > self.value:
            # The values here increase only by one step. Since the 
            # values are pulled from a dictionary, the key
            # is the value of that can be selected
            if str(self.value) in BPM_SUBDIVISIONS.keys():
                keys = list(BPM_SUBDIVISIONS)
                index = keys.index(str(self.value))
                if index + 1 < len(keys):
                    key = int(keys[index + 1])
                    self.value = key

        elif value < self.value:
            if str(self.value) in BPM_SUBDIVISIONS.keys():
                keys = list(BPM_SUBDIVISIONS)
                index = keys.index(str(self.value))
                if index - 1 >= 0:
                    key = int(keys[index - 1])
                    self.value = key


class Menu:
    def __init__(
        self, x: int, y: int,
        menu_dictionary: dict,
        alpha: float = 0.7,
        btm_text_color: Tuple[int, int, int] = (0, 255, 0),
        columns: int = 1, rows: int = 2,
        visible: bool = True
    ) -> None:
        self.x = x
        self.y = y
        self.alpha = alpha      # Opacity.
        self.btm_text_color = btm_text_color
        self.columns = columns
        self.rows = rows
        self.visible = visible
        self.menu_items = menu_dictionary
        self.menu_items_coordinates = {}
        self.value = None

        self.init_menu_items_coordinates()

    def get_value(self) -> str:
        return list(self.value.keys())[0]

    def init_value(self, value: str) -> None:
        self.value = { value: self.menu_items_coordinates[value] }

    def set_visible(self, visible: bool = True) -> bool:
        # Sets the controls to make visible or not
        self.visible = visible

    def set_value(self, x: int, y: int) -> None:
        # Processes menu click if it occurs
        if self.visible:
            for item in self.menu_items_coordinates:
                rectangle = self.menu_items_coordinates[item]
                if point_intersects((x, y), rectangle):
                    self.value = { item: rectangle }
                    break

    def draw(self, img):
        if not self.visible:
            return img

        # Create an overlay image to place buttons on
        overlay = img.copy()

        for item in self.menu_items.keys():
            overlay = self.draw_item(
                self.menu_items_coordinates[item][0],
                self.menu_items_coordinates[item][2],
                item, overlay
            )

        image_new = cv2.addWeighted(
            overlay, self.alpha, img, 1 - self.alpha, 0
        )

        return image_new

    def draw_item(
        self,
        top_left: Tuple[int, int], btm_right: Tuple[int, int],
        item: str, overlay_img
    ):
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
            top_left,
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            self.btm_text_color,
            2,
            cv2.LINE_AA,
        )

        cv2.rectangle(
            overlay_img, top_left, btm_right, self.btm_text_color, 1
        )

        return overlay_img

    def init_menu_items_coordinates(self):
        """
        Add screen coordinates for each element in the menu.
        """
        # Init X and Y for creating menu items
        x = self.x
        y = self.y

        row = 0
        column = 0
        for item in self.menu_items.keys():
            if column < self.columns and row >= self.rows:
                row = 0
                x += 250
                y = self.y

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
        self, BPM=100, visible=True, textlabel="BPM",
        x1=1000, y1=250, x2=1225, y2=300, min_value=40, max_value=220
    ):
        # Setting the text to be displayed before the control, to the left of the
        # slider
        self.BPM = BPM
        self.textlabel = textlabel
        self.visible = visible
        # Intializing control layout coordinates
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.min_value = min_value
        self.max_value = max_value

    def set_bpm(self, bpm):
        if bpm is None:
            return bpm
        if int(bpm) < self.min_value:
            bpm = self.min_value
        if int(bpm) > self.max_value:
            bpm = self.max_value
        self.BPM = bpm

    def draw_controls(self, img):
        """
        draw_controls drawing to layout the slider control
        :param img: 
        :return: img (opencv image)
        """
        # Create a containing  retangle
        cv2.rectangle(
            img,
            (self.x1, self.y1),
            (self.x2, self.y2),
            (192, 84, 80),
            3
        )

        # Create a rectangle that displays the current setting
        cv2.rectangle(
            img,
            (self.x1, self.y1),
            (int(self.BPM + self.x1), self.y2),
            (255, 255, 255),
            cv2.FILLED,
        )

        # Place label text the left of the containing rectangle
        cv2.putText(
            img,
            self.textlabel,
            (self.x1 - 70, self.y1 + 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        # Placing label text inside slider bar
        cv2.putText(
            img,
            str(int(self.BPM)),
            (self.x1 + 10, self.y1 + 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (4, 201, 126),
            2,
            cv2.LINE_AA,
        )
        return img

    def set_sliders(self, img, x1, y1):
        """
        The method exists to checks to see if the user is
        trying to adjust the slider by intersection of the
        containing control
        
        This method takes the opencv image, but currently adds 
        nothing to it. 
        """
        # Pickup BPM Control
        point = Point(x1, y1)
        bpm_rectangle = create_rectangle_array((self.x1, self.y1), (self.x2, self.y2))
        if point_intersects(point, bpm_rectangle):
            bounds = polygon_bounds(bpm_rectangle)
            # The countrol needs to read the X1 boundary 
            # to avoid hardcoding of values
            self.set_bpm(int(x1 - bounds[0]))
            
            # self.BPM = 


        return img
