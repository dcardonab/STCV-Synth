from lib.menu import Menu
from lib.geometry_utility import create_rectangle_array, point_intersects
from lib.constants import scales

class ScaleMenu(Menu):
    # Via inheritance, we are simply supplying the current scale value
    # Scale is returned as a dictionary with a single value key (such as ionian)
    # and the scale values (such as [0, 2, 4, 5, 7, 9, 11])
    def __init__(self, x, y, menu_dictionary, alpha=0.7, btm_text_color=(0, 255, 0), visible=True):
        super().__init__(x, y, menu_dictionary, alpha=alpha, btm_text_color=btm_text_color, visible=visible)
        self.current_scale = None
    
    # Scale is returned as a dictionary with a single value key (such as ionian)
    # and the scale values (such as [0, 2, 4, 5, 7, 9, 11])
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
                        if item in scales.keys():
                            self.current_scale = {item: scales[item]}
                        break
            return super().menu_item_clicked(x, y)