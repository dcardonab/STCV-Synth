import cv2
import asyncio
import numpy as np
import time
import os
import HandTrackingModule as htm
import PIL
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from geometry_utility import create_rectangle_array, point_intersects
from PlusMinusButtons import PlusMinusButtons

    # Leaving gracefully
class Screen():
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

        # Visual Control Member
        self.plus_minus_subdivision = PlusMinusButtons(x=1000, y=350, label="Subdivision", label_offset_x=827, visible=False)
        self.plus_minus_octave_range = PlusMinusButtons(x=1000, y=450, label="8ve range", label_offset_x=840, visible=False)
        self.plus_minus_octave_base = PlusMinusButtons(x=1000, y=550, label="8ve base", label_offset_x=840, visible=False)

    def setup_header_list(self, folder_path="header"):
        myList = os.listdir(folder_path)
        overlayList = []

        myList.sort()

        for imPath in myList:
            image = cv2.imread(f'{folder_path}/{imPath}')
            overlayList.append(image)

        return overlayList

    def draw_controls(self, img):

        cv2.rectangle(img, (1000, 250), (1225, 300), (192, 84, 80), 3)
        cv2.rectangle(img, (1000, 250), (int(self.BPM + 1000), 300), (255, 255, 255), cv2.FILLED)
        cv2.putText(img, "BPM", (930, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(img, str(int(self.BPM)), (1010, 290),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (4, 201, 126), 2, cv2.LINE_AA)



        self.plus_minus_subdivision.set_visible(True)
        img = self.plus_minus_subdivision.draw(img)

        # Octave Range Control
        self.plus_minus_octave_range.set_visible(True)
        img = self.plus_minus_octave_range.draw(img)

        self.plus_minus_octave_base.set_visible(True)
        img = self.plus_minus_octave_base.draw(img)

        # Octave Base Range
        # cv2.rectangle(img, (1000, 550), (1050, 600), (255, 255, 255), cv2.FILLED)
        # cv2.putText(img, "+", (1012, 585),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (4, 201, 126), 2, cv2.LINE_AA)
        # cv2.rectangle(img, (1100, 550), (1150, 600), (255, 255, 255), cv2.FILLED)
        # cv2.putText(img, "-", (1112, 585),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (4, 201, 126), 2, cv2.LINE_AA)
        # cv2.putText(img, "8ve base", (840, 600),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        return img

    def draw(self, img, lmList):

        if len(lmList) != 0:

            # Tip of index and middle finger
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
            fingers = self.detector.finger_is_open(lmList=lmList)
            # print(fingers)

            # Selection mode, if two fingers are up
            if fingers[1] and fingers[2]:
                cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), (255, 0, 255), cv2.FILLED)
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

                self.set_pulse_sustain(x1, y1)

            # Drawing mode
            if fingers[1] and fingers[2] == False:
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                print("Drawing Mode")

            img = self.set_sliders(img, x1, y1)
            self.plus_minus_subdivision.plus_btn_click(x1, y1)
            self.plus_minus_subdivision.minus_btn_click(x1, y1)

            self.plus_minus_octave_range.plus_btn_click(x1, y1)
            self.plus_minus_octave_range.minus_btn_click(x1, y1)

            self.plus_minus_octave_base.plus_btn_click(x1, y1)
            self.plus_minus_octave_base.minus_btn_click(x1, y1)

        return img

    def set_sliders(self, img, x1, y1):
        # Pickup BPM Control
        point = Point(x1, y1)
        bpm_rectangle = create_rectangle_array((1000, 250), (1220, 300))
        if point_intersects(point, bpm_rectangle):
            self.BPM = int(x1 - 1000)

        # Pickup subdivision
        point = Point(x1, y1)
        subdivision_rectangle = create_rectangle_array((1000, 400), (1220, 425))
        if point_intersects(point, subdivision_rectangle):
            self.subdivision = int(x1 - 1000)

        # Pickup Octave
        point = Point(x1, y1)
        octave_range_rectangle = create_rectangle_array((1000, 450), (1220, 475))
        if point_intersects(point, octave_range_rectangle):
            self.octave_range = int(x1 - 1000)

        # Pickup Octave Base
        point = Point(x1, y1)
        octave_range_base_rectangle = create_rectangle_array((1000, 500), (1220, 525))
        if point_intersects(point, octave_range_base_rectangle):
            self.octave_base = int(x1 - 1000)

        # cv2.putText(img, "8ve base", (837, 525),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        return img

    def set_pulse_sustain(self, x1, y1):
        if 402 < y1 < 465:
            if 16 < x1 < 231:
                if self.pulse_sustain_index == 2 and self.switch_delay > 10:
                    self.pulse_sustain_index = 3
                    self.switch_delay = 0
        elif 480 < y1 < 551:
            if 16 < x1 < 231:
                if self.switch_delay > 10:
                    self.pulse_sustain_index = 2
                    self.switch_delay = 0

    async def show(self):

        while True:

            # Import the image
            success, img = self.cap.read()
            img = cv2.flip(img, 1)

            # Find hand landmarks
            img = self.detector.findHands(img=img, draw=False)
            for handNumber in range(0, self.detector.handCount()):
                lmList = self.detector.find_position(img, handNumber=handNumber, draw=True)
                img = self.draw(img, lmList)

            header = self.overlayList[self.header_index]
            if self.header_index == 1:
                self.draw_controls(img)

            left_footer_menu = self.overlayList[self.pulse_sustain_index]
            left_right_selection = self.overlayList[self.left_right_index]
            img[0:header.shape[0], 0:header.shape[1]] = header
            img[400:(left_footer_menu.shape[0]+400), 10:(left_footer_menu.shape[1]+10)] = left_footer_menu
            img[0:(left_right_selection.shape[0]), 1000:(left_right_selection.shape[1] + 1000)] = left_right_selection

            cv2.imshow("Image", img)

            cv2.waitKey(1)
            self.switch_delay += 1
            if self.switch_delay > 500:
                self.switch_delay = 0

if __name__ == "__main__":
    screen = Screen()
    asyncio.run(screen.show())