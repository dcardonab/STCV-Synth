import cv2
from shapely.geometry import Point
from geometry_utility import create_rectangle_array, point_intersects


class Slider:
    """
    This class creates a slider control where the data value falls inside
    the bounding rectangle. 
    """
    def __init__(
        self, BPM=100, visible=True, textlabel="BPM", x1=1000, y1=250, x2=1225, y2=300
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

    def draw_controls(
        self,
        img,
        ):
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
            self.BPM = int(x1 - 1000)

        return img
