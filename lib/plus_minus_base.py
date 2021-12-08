from lib import constants
from lib.plus_minus_buttons import PlusMinusButtons
from lib.constants import base_mult_options; 

class PlusMinusBase(PlusMinusButtons):
    def get_current_value(self):
        return super().get_current_value()

    def get_current_value_constant(self):
        current_value = super().get_current_value()    
        if str(current_value) in constants.base_mult_options.keys():
            current_value_tuple = constants.base_mult_options[str(current_value)]
        return current_value_tuple 