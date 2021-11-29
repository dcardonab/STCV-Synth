import time
import cv2
import mediapipe as mp


class HandDetector():
    def __init__(self, static_image_mode=False,
                 max_num_hands=2,
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):

        self.static_image_mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.tipIds = [4, 8, 12, 16, 20]
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.static_image_mode,
                                        max_num_hands=self.max_num_hands,
                                        min_detection_confidence=self.min_detection_confidence,
                                        min_tracking_confidence=self.min_tracking_confidence)

        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def handCount(self):
        if self.results.multi_handedness:
            return len(self.results.multi_handedness)
        else:
            return 0

    def find_position(self, img, handNumber=0, draw=True, circleDia=7, R=255, G=0, B=255):
        lmList = []

        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNumber]

            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                lmList.append([id, cx, cy])

                if draw:
                    cv2.circle(img, (cx, cy), circleDia, (R, G, B), cv2.FILLED)

        return lmList

    def find_z_depth(self, img, handNumber=0):
        if self.results.multi_hand_landmarks:
            z_depth = self.results.multi_hand_landmarks[handNumber].landmark[0].z
            return z_depth
        else:
            return 0

    def is_left_or_right_hand(self, index):
        if self.results.multi_handedness:
            hand = self.results.multi_handedness[index]
            print("results.multi_handedness ", len(self.results.multi_handedness))
        return hand.classification[0].label

    def finger_is_open(self, lmList):
        openTips = []
        if len(lmList) != 0:

            # Right Thumb
            if lmList[self.tipIds[0]][1] > lmList[self.tipIds[0] - 1][1]:
                openTips.append(1)
            else:
                openTips.append(0)

            #  four fingers
            for id in range(1, 5):
                if lmList[self.tipIds[id]][2] < lmList[self.tipIds[id] - 2][2]:
                    openTips.append(1)
                else:
                    openTips.append(0)

        return openTips
