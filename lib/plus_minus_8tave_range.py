from lib.plus_minus_base import PlusMinusButtons
from lib.constants import bpm_sub_divisions

class PlusMinus8taveRange(PlusMinusButtons):
    def init_value(self, value):
        self.current_value = value
    
    def set_current_value(self, new_value):
        if new_value == self.current_value:
            # No change in the current value
            pass
        elif new_value > self.current_value:
            # The values here increase only by one step. Since the 
            # values are pulled from a dictionary, the key
            # is the value of that can be selected
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
        return super().set_current_value(new_value)

