# Python Libraries
import os
import time

# Third-Party Libraries
import cv2

# Local Files
from constants import SCALES, ST_WEARING_HAND, SYNTH_MODE
from gui_elements import *
from hand_tracking import HandDetector


class Screen:
    """
    Screen object to serve as drawing platform
    """

    def __init__(
        self, screen_number: int = 0, 
        screen_size_x: int = 1280, screen_size_y: int = 720
    ) -> None:

        self.cap = cv2.VideoCapture(screen_number)
        self.cap.set(3, screen_size_x)
        self.cap.set(4, screen_size_y)

        # The header index defines whether to display the settings controls
        # or the performance controls.
        self.header_index = 0
        self.overlayList = self.setup_header_list()

        self.detector = HandDetector(min_detection_confidence=0.50)

        # Switch delay is used to ensure that a finger collides for a long
        # enough duration with the toggle control to prevent the toggle from
        # staying engaged, which would result in swapping from settings
        # controls to performance controls every loop.
        self.switch_delay = 0

        # These values are used to calculate the FPS.
        self.cur_time = 0
        self.prev_time = 0
        self.cur_tick = 0
        self.prev_tick = 0

        self.init_controls()

    def init_controls(self) -> None:
        """
        Control initialization function, based on a graphics design pattern.
        Python prefers to have this all in the __init__ method, but this
        reduces readibility.
        """

        """ Performance GUI Controls """

        # The slider control is created here with all default values
        self.bpm_slider = Slider()

        # Layout the coordinates and labels of the PlusMinusSubdivions controls
        # PlusMinusSubdivions is child control of the PlusMinusButtons
        self.subdivision_plus_minus = GUI_Subdivions(
            x = 1000, y = 350,
            label = "Subdivision",
            label_offset_x = -175,
            visible = False
        )

        # Creating PlusMinusButtons instance as member variable
        # Layout the coordinates and labels of the PlusMinusButtons control
        self.octave_base_plus_minus = GUI_OctaveBase(
            x = 1000, y = 450,
            label = "8ve Base",
            label_offset_x = -150,
            visible = False
        )

        # Creating PlusMinusButtons instance as member variable
        # Layout the coordinates and labels of the PlusMinusButtons control
        self.octave_range_plus_minus = PlusMinusButtons(
            x = 1000, y = 550,
            label = "8ve Range",
            label_offset_x = -170,
            visible = False
        )

        """ Settings GUI Controls"""
        # Creating Menu instance with control layout
        # Making use of the controls default layout values
        # The menu dictionary is used as the menu items
        self.scales_menu = ScaleMenu(
            x = 200, y = 100,
            menu_dictionary = SCALES
        )

        # The Menu class is created from configurable dictionary, in this
        # in this case a Pulse and Sustain menu items
        self.pulse_sustain_menu = Menu(
            x = 750, y = 100,
            menu_dictionary = SYNTH_MODE, 
            btm_text_color = (255, 0, 0)
        )

        # The Menu class is created from configurable dictionary, in this
        # in this case a Left and Right menu items
        self.left_right_menu = Menu(
            1000, 100,
            menu_dictionary = ST_WEARING_HAND,
            btm_text_color = (255, 0, 255)
        )

    def CV_loop(self, show_FPS: bool = True) -> None:
        """
        Computer Vision drawing and GUI operation logic.
        """
        # Read the image from the camera
        success, img = self.cap.read()

        # Execute logic if camera read was successful.
        if success:
            # Flip image to display a mirror-like image to the user.
            img = cv2.flip(img, 1)

            # Find hand landmarks (i.e., nodes)
            img = self.detector.findHands(img=img, draw=False)
            for handNumber in range(self.detector.handCount()):
                # lmList is a list of all landmarks present in the screen.
                lmList = self.detector.find_position(
                    img, hand_number=handNumber, draw=True
                )
                if lmList != 0:
                    img = self.event_processing(img, lmList)

            # Display GUI controllers.
            if self.header_index == 0:
                self.hide_settings_gui()
                img = self.draw_performance_gui(img)
            else:
                self.hide_performance_gui()
                img = self.draw_settings_gui(img)
                
            # Retrieve button image to show.
            header = self.overlayList[self.header_index]
            assert isinstance(header, object)

            # Overwrites a subsection of the camera image using the button
            # images that were retrieved.
            img[0: header.shape[0], 0: header.shape[1]] = header

            if show_FPS:
                self.cur_time = time.time()
                self.cur_tick = cv2.getTickCount()
                fps = 1 / (self.cur_time - self.prev_time)
                print(f"Execution time in seconds: {(self.cur_tick - self.prev_tick) / cv2.getTickFrequency()}", end='\r', flush=True)
                self.prev_time = self.cur_time
                self.prev_tick = self.cur_tick

                cv2.putText(
                    img, f"FPS: {int(fps)}", (400, 70),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 2
                )
            
            # Display image in the screen context.
            cv2.imshow("Image", img)
            cv2.waitKey(1)

            # Provision to prevent the toggle from staying engaged.
            self.switch_delay += 1
            if self.switch_delay > 500:
                self.switch_delay = 0

        else:
            print("Unable to read data from the camera.")

    def setup_header_list(self, folder_path: str = "lib/header") -> list:
        """
        setup_header_list gathers a list of files to
        be used in the image display as visual controls
        :param folder_path:
        :return: list of graphic files
        """

        myList = os.listdir(folder_path)
        overlayList = []

        myList.sort()

        for imPath in myList:
            image = cv2.imread(f"{folder_path}/{imPath}")
            overlayList.append(image)

        return overlayList

    def draw_performance_gui(self, img):
        """
        draw_performance_gui sets the performance GUI controls visible.
        """

        # BPM slider. This control has its own visibility controls.
        img = self.bpm_slider.draw_controls(img)

        # Subdivision plus-minus control
        self.subdivision_plus_minus.set_visible(True)
        img = self.subdivision_plus_minus.draw(img)

        # Octave Range Control
        self.octave_range_plus_minus.set_visible(True)
        img = self.octave_range_plus_minus.draw(img)

        # Octave Base Control
        self.octave_base_plus_minus.set_visible(True)
        img = self.octave_base_plus_minus.draw(img)

        return img

    def draw_settings_gui(self, img):
        """
        draw_settings_gui sets the settings GUI controls visible.
        """
        # Scale selector
        self.scales_menu.set_visible(True)
        img = self.scales_menu.draw(img)

        # Synthesizer mode
        self.pulse_sustain_menu.set_visible(True)
        img = self.pulse_sustain_menu.draw(img)

        # SensorTile hand selection
        self.left_right_menu.set_visible(True)
        img = self.left_right_menu.draw(img)

        return img

    def hide_performance_gui(self) -> None:
        """
        hide_performance_gui hides the performance GUI controls.
        """
        self.subdivision_plus_minus.set_visible(False)
        self.octave_range_plus_minus.set_visible(False)
        self.octave_base_plus_minus.set_visible(False)

    def hide_settings_gui(self) -> None:
        """
        hide_settings_gui hides the settings GUI controls.
        """
        self.pulse_sustain_menu.set_visible(False)
        self.scales_menu.set_visible(False)
        self.left_right_menu.set_visible(False)

    def event_processing(self, img, lm_list):
        # Tip of index and middle finger
        # the following values are the landmarks for any hand
        # finger tips pointer and index fingers
        x1, y1 = lm_list[8][1:]
        x2, y2 = lm_list[12][1:]

        """
        This method call tests if the fingers are opened (pointing upward)
        or if in a closed position (like a fist)
        """
        fingers = self.detector.finger_is_open(lmList=lm_list)
        
        """
        Selection mode, if two fingers are up
        Two open fingers are used to determine if we are using 
        performance controls or settings controls
        """
        if fingers[1] and fingers[2]:
            cv2.rectangle(
                img, (x1, y1 - 15), (x2, y2 + 15), (255, 0, 255), cv2.FILLED
            )

            # The print function is used for diagnostic purposes only
            # Will be replaced by logging functionality
            # print("Selection Mode", x1, y1)

            # checking for the click
            if y1 < 89:
                if 0 < x1 < 90:
                    if self.header_index == 0 and self.switch_delay > 10:
                        self.header_index = 1
                        self.switch_delay = 0
                    elif self.switch_delay > 10:
                        self.header_index = 0
                        self.switch_delay = 0

        # Drawing mode
        if fingers[1] and fingers[2] == False:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            print("Single Finger Mode")

        """
        The following code determines if a plus button or a minus
        button has been clicked.  If the button has been clicked
        the state is maintained in the control and can be queried
        """
        
        img = self.bpm_slider.set_sliders(img, x1, y1)

        self.subdivision_plus_minus.plus_btn_click(x1, y1)
        self.subdivision_plus_minus.minus_btn_click(x1, y1)

        self.octave_range_plus_minus.plus_btn_click(x1, y1)
        self.octave_range_plus_minus.minus_btn_click(x1, y1)

        self.octave_base_plus_minus.plus_btn_click(x1, y1)
        self.octave_base_plus_minus.minus_btn_click(x1, y1)

        self.scales_menu.menu_item_clicked(x1, y1)
        self.left_right_menu.menu_item_clicked(x1, y1)
        self.pulse_sustain_menu.menu_item_clicked(x1, y1)

        return img
