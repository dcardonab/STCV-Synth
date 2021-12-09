from lib.plus_minus_buttons import PlusMinusButtons
from lib.constants import bpm_sub_divisions
from lib.geometry_utility import point_intersects, polygon_bounds, create_rectangle_array
from shapely.geometry import Point

class PlusMinusSubdivions(PlusMinusButtons):
    def set_current_value(self, new_value):
        if new_value == self.current_value:
            # No change in the current value
            pass
        elif new_value > self.current_value:
            
            if str(self.current_value) in bpm_sub_divisions.keys():
                t = list(bpm_sub_divisions)
                i = t.index(str(self.current_value))
                if (i+1) < len(t):
                    key = int(t[i+1])
                    self.current_value = key
        elif new_value <= self.current_value:
            if str(self.current_value) in bpm_sub_divisions.keys():
                t = list(bpm_sub_divisions)
                i = t.index(str(self.current_value))
                if (i-1) >= 0:
                    key = int(t[i-1])
                    self.current_value = key

        return super().set_current_value(self.current_value)
    
    def get_current_value_constant(self):
        current_value = self.get_current_value()    
        if str(current_value) in bpm_sub_divisions.keys():
            current_value_tuple = bpm_sub_divisions[str(current_value)]
            return current_value_tuple
        

    def minus_btn_click(self, x, y):
        # processes the events for the plus botton click
        # A button click is simply looking for a finger 
        # landmark intersection
        if self.visible:
            if self.min_value < self.current_value:
            
                point = Point(x, y)
                bounding_box = create_rectangle_array(
                    (self.x1, self.y1), (self.x2, self.y2)
                )
                if point_intersects(point, bounding_box):
                    self.set_current_value(self.current_value-1)

    def plus_btn_click(self, x, y):
        # processes the events for the minus botton click
        # A button click is simply looking for a finger 
        # landmark intersection
        if self.visible:
            if self.max_value > self.current_value:
                point = Point(x, y)
                bounding_box = create_rectangle_array(
                    (self.x1 + 100, self.y1), ((self.x2 + 100), self.y2)
                )
                if point_intersects(point, bounding_box):
                    self.set_current_value(self.current_value+1)
                        