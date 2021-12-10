from lib.constants import scales
from lib.geometry_utility import create_rectangle_array, point_intersects
import cv2


class Menu:
    def __init__(
        self, x, y, menu_dictionary, alpha=0.7, btm_text_color=(0, 255, 0), visible=True
    ):
        self.x = x
        self.y = y
        self.alpha = alpha  # Transparency factor.
        self.btm_text_color = btm_text_color
        self.column_number = 2
        self.row_number = 8
        self.visible = visible
        self.menu_dictionary = menu_dictionary
        self.menu_grid_dictionary = {}
        self.selected_menu_item = None

    def set_column_number(self, column_number=2):
        self.column_number = column_number

    def set_row_number(self, row_number):
        # Sets the maximum row count for the menu item
        self.row_number = row_number

    def get_menu_grid_dictionary(self):
        #Creates a matrix of the menu grid
        return self.menu_grid_dictionary

    def get_selected_menu_item(self):
        return self.selected_menu_item

    def set_visible(self, visible: bool = True) -> bool:
        # Sets the controls to make visible or not
        self.visible = visible

    def get_visible(self) -> bool:
        """
        Returns whether the control will be rendered or not
        """
        return self.visible

    def menu_item_clicked(self, x, y):
        # Processes menu click if it occurs
        if self.visible:
            if self.menu_grid_dictionary:
                for item in self.menu_grid_dictionary:
                    rectangle = self.menu_grid_dictionary[item]
                    if point_intersects((x, y), rectangle):
                        self.selected_menu_item = {item: rectangle}
                        break

    def draw_sub_item(self, scale_name, overlay_img, x, y):
        # Creates individual menu items base on dictionary
        if self.selected_menu_item:
            if scale_name in self.selected_menu_item:
                cv2.rectangle(
                    overlay_img,
                    self.selected_menu_item[scale_name][0],
                    self.selected_menu_item[scale_name][2],
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
        """

        :param img:
        :return:
        """

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

            overlay = self.draw_sub_item(scale_name, overlay, current_x, current_y)
            current_y += 70
            current_row += 1

        image_new = cv2.addWeighted(overlay, self.alpha, img, 1 - self.alpha, 0)

        if self.selected_menu_item is None:
            self.menu_item_clicked(self.x + 10, self.y - 5)


        return image_new
