# Python Libraries
import os
from threading import Thread
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

        # VideoCapture is a class to capture images from video files,
        # image sequences, or cameras.
        self.capture = cv2.VideoCapture(screen_number)
        # The the first argument is the CV property identifier and the second
        # is the value that is being assigned to that property.
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, screen_size_x)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_size_y)

        # Limit buffer size property.
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 3)

        # Read first frame to avoid an attribute error.
        self.status, self.frame = self.capture.read()

        # Set Frames Per Second. This value will be used at the end of the
        # CV_loop function, when specifying how long to wait prior to the
        # next iteration.
        self.FPS = 1 / 30
        self.FPS_MS = int(self.FPS * 1000)

        # The header index defines whether to display the settings controls
        # or the performance controls.
        self.header_index = 0
        self.overlayList = self.setup_header_list()
        self.header = self.overlayList[self.header_index]

        self.detector = HandDetector(min_detection_confidence=0.50)

        # Switch delay is used to ensure that a finger collides for a long
        # enough duration with the toggle control to prevent the toggle from
        # staying engaged, which would result in swapping from settings
        # controls to performance controls every loop.
        self.sensitivity = 0

        # These values are used to calculate the FPS.
        self.cur_time = 0
        self.prev_time = 0
        self.cur_tick = 0
        self.prev_tick = 0

        self.show_FPS = False

        self.init_controls()

        # Run frame retrieval through a separate thread.
        self.thread = Thread(target=self.update, args=())
        # A daemon thread flag is used to allow the program to exit when
        # only daemon threads are left.
        self.thread.daemon = True

    # def loop(self):
    #     print("Running thread")
    #     self.update()
    #     self.render()

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
        self.subdivision_buttons = GUI_Subdivions(
            x=1000, y=270,
            label="Subdivision",
            label_offset_x=-175
        )

        # Creating PlusMinusButtons instance as member variable
        # Layout the coordinates and labels of the PlusMinusButtons control
        self.oct_base_buttons = PlusMinusButtons(
            x=1000, y=400,
            label="8ve Base",
            label_offset_x=-150,
            min_value=-2, max_value=4
        )

        # Creating PlusMinusButtons instance as member variable
        # Layout the coordinates and labels of the PlusMinusButtons control
        self.oct_range_buttons = PlusMinusButtons(
            x=1000, y=530,
            label="8ve Range",
            label_offset_x=-170,
            min_value=1, max_value=7
        )

        """ Settings GUI Controls"""
        # Creating Menu instance with control layout
        # Making use of the controls default layout values
        # The menu dictionary is used as the menu items
        self.scales_menu = Menu(
            x=200, y=100,
            menu_dictionary=SCALES,
            columns=2, rows=8
        )

        # The Menu class is created from configurable dictionary, in this
        # in this case a Pulse and Sustain menu items
        self.pulse_sustain_menu = Menu(
            x=750, y=100,
            menu_dictionary=SYNTH_MODE,
            btm_text_color=(255, 0, 0)
        )

        # The Menu class is created from configurable dictionary, in this
        # in this case a Left and Right menu items
        self.st_wearing_hand_menu = Menu(
            x=1000, y=100,
            menu_dictionary=ST_WEARING_HAND,
            btm_text_color=(255, 0, 255)
        )

    def init_values(self, synth) -> None:
        # Set initial GUI values to match the Synth settings.
        self.bpm_slider.set_bpm(int(60 / synth.bpm))
        self.subdivision_buttons.init_value(int(synth.subdivision))
        self.oct_base_buttons.init_value(int(synth.base_key))
        self.oct_range_buttons.init_value(synth.oct_range)

        # Initialize Menus
        self.scales_menu.init_value(synth.scale[0])
        self.pulse_sustain_menu.init_value(list(SYNTH_MODE.keys())[0])
        self.st_wearing_hand_menu.init_value(list(ST_WEARING_HAND.keys())[0])

    def update(self) -> None:
        """
        Computer Vision drawing and GUI operation logic.
        """
        while True:
            if self.capture.isOpened():
                # Flip image to display a mirror-like image to the user.
                # The second argument '1' flips the image horizontally.
                self.frame = cv2.flip(self.capture.read()[1], 1)

                # Find hand landmarks (i.e., nodes)
                self.frame = self.detector.find_hands(
                    img=self.frame, draw=False
                )

                for handNumber in range(self.detector.hand_count()):
                    # lmList is a list of all landmarks present in the screen.
                    lmList = self.detector.find_position(
                        self.frame, hand_number=handNumber, draw=True
                    )
                    if lmList != 0:
                        self.event_processing(lmList)

                # Provision to prevent the toggle from staying engaged.
                self.sensitivity += 1
                if self.sensitivity > 500:
                    self.sensitivity = 0

            # time.sleep(self.FPS)

    def render(self) -> None:
        # Display GUI controllers.
        if self.header_index == 0:
            self.draw_performance_gui()
        else:
            self.draw_settings_gui()

        # Overwrites a subsection of the camera image using the button
        # images that were retrieved.
        self.frame[0: self.header.shape[0], 0: self.header.shape[1]] = \
            self.header

        if self.show_FPS:
            self.cur_time = time.time()
            self.cur_tick = cv2.getTickCount()
            fps = 1 / (self.cur_time - self.prev_time)
            self.prev_time = self.cur_time
            self.prev_tick = self.cur_tick

            cv2.putText(
                self.frame, f"FPS: {int(fps)}", (25, 670),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 2
            )

        # Display image in the screen context.
        cv2.imshow('frame', self.frame)
        cv2.waitKey(self.FPS_MS)

    def setup_header_list(self, folder_path: str = "lib/header") -> list:
        """
        Gather list of files to display as visual controls.
        """
        # Get images.
        myList = os.listdir(folder_path)
        myList.sort()

        # Retrieve images into local list.
        overlayList = []
        for imPath in myList:
            image = cv2.imread(f"{folder_path}/{imPath}")
            overlayList.append(image)

        return overlayList

    def draw_performance_gui(self) -> None:
        """
        Draw the performance GUI controls.
        """
        self.frame = self.bpm_slider.render(self.frame)
        self.frame = self.subdivision_buttons.render(self.frame)
        self.frame = self.oct_range_buttons.render(self.frame)
        self.frame = self.oct_base_buttons.render(self.frame)

    def draw_settings_gui(self) -> None:
        """
        Draw the settings GUI controls.
        """
        self.frame = self.scales_menu.render(self.frame)
        self.frame = self.pulse_sustain_menu.render(self.frame)
        self.frame = self.st_wearing_hand_menu.render(self.frame)

    def event_processing(self, lm_list):
        # Get the node corresponding to the tip of the index finger. The
        # following values are the landmarks for any hand's index finger tips.
        x, y = lm_list[8][1:]

        """
        Check for GUI collisions.
        """
        if y < 89:
            if 0 < x < 90:
                # Ensure that finger is on toggle button for longer than 10
                # frames before switching from performance to settings views.
                if self.header_index == 0 and self.sensitivity > 10:
                    self.header_index = 1
                    self.sensitivity = 0
                elif self.sensitivity > 10:
                    self.header_index = 0
                    self.sensitivity = 0

                # Retrieve button image to show.
                self.header = self.overlayList[self.header_index]

        collision = self.check_collision(x, y)

        # Reset sensitivity counter if a collision was detected.
        if collision:
            self.sensitivity = 0

    def check_collision(self, x: int, y: int) -> bool:
        """
        Check for collision against the various GUI items.
        """
        col = False

        self.frame = self.bpm_slider.set_sliders(self.frame, x, y)

        if self.sensitivity > 8:
            # Check for collision against performance GUI.
            if self.header_index == 0:
                # 'col' will be set to true if there was a collision detected.
                col = self.subdivision_buttons.plus_btn_check_collision(x, y)
                col = self.subdivision_buttons.minus_btn_check_collision(x, y)

                col = self.oct_range_buttons.plus_btn_check_collision(x, y)
                col = self.oct_range_buttons.minus_btn_check_collision(x, y)

                col = self.oct_base_buttons.plus_btn_check_collision(x, y)
                col = self.oct_base_buttons.minus_btn_check_collision(x, y)

            # Check for collision against settings GUI.
            else:
                col = self.scales_menu.check_collision(x, y)
                col = self.st_wearing_hand_menu.check_collision(x, y)
                col = self.pulse_sustain_menu.check_collision(x, y)

        return col
