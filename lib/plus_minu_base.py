from lib.plus_minus_buttons import PlusMinusButtons
from constants import base_mult_options; 

class PlusMinusBase(PlusMinusButtons):
    def get_current_value(self):
        return super().get_current_value()

    def get_current_value_constant(self):
        current_value = super().get_current_value()    
        return current_value