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
        self.label = label                      # Button Label
        self.text_color = text_color            # Text color for label
        self.btm_text_color = btm_text_color    # Text color for botton
        self.back_color = back_color            # Back color of text button
        self.label_offset_x = label_offset_x    # Distance from the button

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
                    self.value -= 1

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
                    self.value += 1


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


class GUI_OctaveRange(PlusMinusButtons):
    """
    This class overrides the 'set_value' method of the PlusMinusButtons
    class to utilize the keys of the octave range dictionary.
    """
    def set_value(self, value: int) -> None:
        # if value == self.value:
        #     # No change in the current value
        #     pass
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

        # return super().set_value(value)


class GUI_Subdivions(PlusMinusButtons):
    
    def set_value(self, value):
        """
        This method only allows values the match the tuples list in the dictionary
        """
        # if value == self.value:
        #     # No change in the current value
        #     pass
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

        # return super().set_value(self.value)
    
    def get_value_constant(self):
        # The current value is tied to a dictionary in the constants.py
        # Only values from that dictionary can be set
        value = self.get_value()    
        if str(value) in BPM_SUBDIVISIONS.keys():
            return BPM_SUBDIVISIONS[str(value)]

    def minus_btn_click(self, x, y):
        # Becasue the count factor changed, this method needs to be overriden.
        if self.visible:
            if self.min_value < self.value:
                point = Point(x, y)
                bounding_box = create_rectangle_array(
                    (self.x1, self.y1), (self.x2, self.y2)
                )
                if point_intersects(point, bounding_box):
                    self.set_value(self.value - 1)

    def plus_btn_click(self, x, y):
        # Becasue the count factor changed, this method needs to be overriden.
        if self.visible:
            if self.max_value > self.value:
                point = Point(x, y)
                bounding_box = create_rectangle_array(
                    (self.x1 + 100, self.y1), (self.x2 + 100, self.y2)
                )
                if point_intersects(point, bounding_box):
                    self.set_value(self.value + 1)


class Menu:
    def __init__(
        self, x: int, y: int,
        menu_dictionary: dict,
        alpha: float = 0.7,
        btm_text_color: Tuple[int, int, int] = (0, 255, 0),
        visible: bool = True
    ) -> None:
        self.x = x
        self.y = y
        self.alpha = alpha      # Opacity.
        self.btm_text_color = btm_text_color
        self.column_number = 2
        self.row_number = 8
        self.visible = visible
        self.menu_dictionary = menu_dictionary
        self.menu_grid_dictionary = {}
        self.selected_item = None

    def set_column_number(self, column_number: int) -> None:
        self.column_number = column_number

    def set_row_number(self, row_number: int) -> None:
        # Sets the maximum row count for the menu item
        self.row_number = row_number

    def get_menu_grid_dictionary(self) -> dict:
        # Creates a matrix of the menu grid.
        return self.menu_grid_dictionary

    def get_selected_item(self) -> str:
        return self.selected_item

    def set_visible(self, visible: bool = True) -> bool:
        # Sets the controls to make visible or not
        self.visible = visible

    def get_visible(self) -> bool:
        """
        Returns whether the control will be rendered or not
        """
        return self.visible

    def menu_item_clicked(self, x: int, y: int) -> None:
        # Processes menu click if it occurs
        if self.visible:
            if self.menu_grid_dictionary:
                for item in self.menu_grid_dictionary:
                    rectangle = self.menu_grid_dictionary[item]
                    if point_intersects((x, y), rectangle):
                        self.selected_item = {item: rectangle}
                        break

    def draw_sub_item(self, x: int, y: int, scale_name: str, overlay_img):
        # Creates individual menu items base on dictionary
        if self.selected_item:
            if scale_name in self.selected_item:
                cv2.rectangle(
                    overlay_img,
                    self.selected_item[scale_name][0],
                    self.selected_item[scale_name][2],
                    (255, 255, 255),
                    cv2.FILLED,
                )

        cv2.putText(
            overlay_img,
            scale_name,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            self.btm_text_color,
            2,
            cv2.LINE_AA,
        )

        self.menu_grid_dictionary[scale_name] = create_rectangle_array(
            (x, y + 5), (x + 240, y - 50)
        )
        cv2.rectangle(
            overlay_img, (x, y + 5), (x + 240, y - 50), self.btm_text_color, 1
        )

        return overlay_img

    def draw(self, img):
        if not self.get_visible():
            return img

        # Create an overlay image to place buttons on
        overlay = img.copy()

        current_y = self.y
        current_x = self.x

        current_row = 0
        for scale_name in self.menu_dictionary.keys():
            if self.column_number > 1 and current_row >= self.row_number:
                current_x += 250
                current_row = 0
                current_y = self.y

            overlay = self.draw_sub_item(
                current_x, current_y, scale_name, overlay
            )
            current_y += 70
            current_row += 1

        image_new = cv2.addWeighted(overlay, self.alpha, img, 1 - self.alpha, 0)

        if self.selected_item is None:
            self.menu_item_clicked(self.x + 10, self.y - 5)

        return image_new


class ScaleMenu(Menu):
    # Via inheritance, we are simply supplying the current scale value
    # Scale returns as a dictionary with a single value key (such as ionian)
    # and the scale values (such as [0, 2, 4, 5, 7, 9, 11])
    def __init__(
        self, x: int, y: int,
        menu_dictionary: dict,
        alpha: float = 0.7,
        btm_text_color: Tuple[int, int, int] = (0, 255, 0),
        visible: bool = True
    ) -> None:

        super().__init__(x, y, menu_dictionary, alpha=alpha,
            btm_text_color=btm_text_color, visible=visible
        )
        self.current_scale = None
    
    def get_current_scale(self):
        return self.current_scale

    # Overriding this method to capture and return the scale values
    def menu_item_clicked(self, x, y):
        # Processes menu click if it occurs
        if self.visible:
            if self.menu_grid_dictionary:
                for item in self.menu_grid_dictionary:
                    rectangle = self.menu_grid_dictionary[item]
                    if point_intersects((x, y), rectangle):
                        self.selected_menu_item = {item: rectangle}
                        if item in SCALES.keys():
                            self.current_scale = {item: SCALES[item]}
                        break
            return super().menu_item_clicked(x, y)


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
        '''
        draw_controls drawing to layout the slider control
        :param img: 
        :return: img (opencv image)
        '''
        # Create a containing  retangle
        cv2.rectangle(img, (self.x1, self.y1), (self.x2, self.y2), (192, 84, 80), 3)

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
