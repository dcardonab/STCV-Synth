import cv2

import os
import hand_tracking as htm
from shapely.geometry import Point
from geometry_utility import create_rectangle_array, point_intersects
from plus_minus_subdivisions import PlusMinusSubdivions
from plus_minus_buttons import PlusMinusButtons
from menu import Menu
from slider import Slider
from constants import scales
import asyncio


class Screen:
    """
    Screen object to serve as drawing platform
    """
    def __init__(self, screen_number=0, screen_size_x=1280, screen_size_y=720):
        self.cap = cv2.VideoCapture(screen_number)
        self.cap.set(3, screen_size_x)
        self.cap.set(4, screen_size_y)
        self.header_index = 0
        self.overlayList = self.setup_header_list()
        self.detector = htm.HandDetector(min_detection_confidence=0.50)
        self.switch_delay = 0
        self.BPM = 100
        self.octave_range = 1
        self.octave_base = 1
        self.subdivision = 1
        self.pulse_sustain_index = 3
        self.left_right_index = 4

        self.init_controls()

    def init_controls(self):
        # Visual Control Members
        self.plus_minus_subdivision = PlusMinusSubdivions(
            x=1000, y=350, label="Subdivision", label_offset_x=827, visible=False
        )
        self.plus_minus_octave_range = PlusMinusButtons(
            x=1000, y=450, label="8ve range", label_offset_x=840, visible=False
        )
        self.plus_minus_octave_base = PlusMinusButtons(
            x=1000, y=550, label="8ve base", label_offset_x=840, visible=False
        )
        self.scales_menu = Menu(x=200, y=100, menu_dictionary=scales)
        pulse_sustain_dict = {"Pulse": 0, "Sustain": 1}
        self.pulse_sustain_menu = Menu(
            750, 100, menu_dictionary=pulse_sustain_dict, btm_text_color=(255, 0, 0)
        )
        left_right_dict = {"Left": 0, "Right": 1}
        self.left_right_menu = Menu(
            1000, 100, menu_dictionary=left_right_dict, btm_text_color=(255, 0, 255)
        )
        self.bpm_slider = Slider()

    def setup_header_list(self, folder_path="lib/header"):
        print(os.getcwd())
        myList = os.listdir(folder_path)
        overlayList = []

        myList.sort()

        for imPath in myList:
            image = cv2.imread(f"{folder_path}/{imPath}")
            overlayList.append(image)

        return overlayList

    def draw_run_controls(self, img):

        img = self.bpm_slider.draw_controls(img)

        self.plus_minus_subdivision.set_visible(True)
        img = self.plus_minus_subdivision.draw(img)

        # Octave Range Control
        self.plus_minus_octave_range.set_visible(True)
        img = self.plus_minus_octave_range.draw(img)

        self.plus_minus_octave_base.set_visible(True)
        img = self.plus_minus_octave_base.draw(img)

        return img

    def hide_run_controls(self):
        self.plus_minus_subdivision.set_visible(False)
        self.plus_minus_octave_range.set_visible(False)
        self.plus_minus_octave_base.set_visible(False)


    def event_processing(self, img, lm_list):

        if len(lm_list) != 0:

            # Tip of index and middle finger
            x1, y1 = lm_list[8][1:]
            x2, y2 = lm_list[12][1:]
            fingers = self.detector.finger_is_open(lmList=lm_list)
            # print(fingers)

            # Selection mode, if two fingers are up
            if fingers[1] and fingers[2]:
                cv2.rectangle(
                    img, (x1, y1 - 15), (x2, y2 + 15), (255, 0, 255), cv2.FILLED
                )
                print("Selection Mode", x1, y1)
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

            img = self.bpm_slider.set_sliders(img, x1, y1)
            self.plus_minus_subdivision.plus_btn_click(x1, y1)
            self.plus_minus_subdivision.minus_btn_click(x1, y1)

            self.plus_minus_octave_range.plus_btn_click(x1, y1)
            self.plus_minus_octave_range.minus_btn_click(x1, y1)

            self.plus_minus_octave_base.plus_btn_click(x1, y1)
            self.plus_minus_octave_base.minus_btn_click(x1, y1)

            self.scales_menu.menu_item_clicked(x1, y1)
            self.left_right_menu.menu_item_clicked(x1, y1)
            self.pulse_sustain_menu.menu_item_clicked(x1, y1)

        return img

    async def show(self):

        while True:

            # Import the image
            success, img = self.cap.read()
            img = cv2.flip(img, 1)

            # Find hand landmarks
            img = self.detector.findHands(img=img, draw=False)
            for handNumber in range(0, self.detector.handCount()):
                lmList = self.detector.find_position(
                    img, hand_number=handNumber, draw=True
                )
                img = self.event_processing(img, lmList)

            img = self.scales_menu.draw(img)
            img = self.pulse_sustain_menu.draw(img)
            img = self.left_right_menu.draw(img)

            header = self.overlayList[self.header_index]

            if self.header_index == 1:
                self.draw_run_controls(img)

                self.pulse_sustain_menu.set_visible(False)
                self.scales_menu.set_visible(False)
                self.left_right_menu.set_visible(False)
            else:
                self.pulse_sustain_menu.set_visible(True)
                self.scales_menu.set_visible(True)
                self.left_right_menu.set_visible(True)
                self.hide_run_controls()
                

            assert isinstance(header, object)
            img[0: header.shape[0], 0: header.shape[1]] = header

            cv2.imshow("Image", img)

            cv2.waitKey(1)
            self.switch_delay += 1
            if self.switch_delay > 500:
                self.switch_delay = 0


if __name__ == "__main__":
    screen = Screen()
    asyncio.run(screen.show())
