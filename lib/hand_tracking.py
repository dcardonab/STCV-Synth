""" Hand detector abstraction based on MediaPipe. """

# Third-Party Libraries
import cv2
import mediapipe as mp


class HandDetector:
    """ Hand feature detection class and functions. """

    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:

        self.static_image_mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        # Fingertip landmark identifiers
        self.tip_ids = [4, 8, 12, 16, 20]

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            self.static_image_mode,
            max_num_hands=self.max_num_hands,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        )

        self.mp_draw = mp.solutions.drawing_utils

        self.results = None

    def find_hands(self, img, draw=True):
        """ Find hands in the field of view. """

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_landmark in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        img, hand_landmark, self.mp_hands.HAND_CONNECTIONS
                    )
        return img

    def hand_count(self):
        """ Return the number of hands in the field of view. """
        return len(self.results.multi_handedness) if self.results.multi_handedness else 0

    def find_position(
        self, img, hand_number=0, draw=True, circle_diameter=7,
        r=255, g=0, b=255
    ):
        """ Find the position of the hand landmarks. """
        landmark_list = []

        if self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[hand_number]

            for i, landmark in enumerate(hand.landmark):
                height, width, _ = img.shape
                x_coord, y_coord = \
                    int(landmark.x * width), int(landmark.y * height)
                landmark_list.append([i, x_coord, y_coord])

                if draw:
                    cv2.circle(
                        img, (x_coord, y_coord), circle_diameter, (r, g, b), cv2.FILLED)

        return landmark_list

    # def _find_z_depth(self, hand_number=0):
    #     if self.results.multi_hand_landmarks:
    #         z_depth = \
    #             self.results.multi_hand_landmarks[hand_number].landmark[0].z
    #         return z_depth
    #     else:
    #         return 0

    # def _is_left_or_right_hand(self, index):
    #     if self.results.multi_handedness:
    #         hand = self.results.multi_handedness[index]
    #         print(
    #             "results.multi_handedness ", len(self.results.multi_handedness)
    #         )
    #     return hand.classification[0].label

    # def _finger_is_open(self, landmark_list):
    #     open_tips = []

    #     if len(landmark_list) != 0:

    #         # Right Thumb
    #         if landmark_list[self.tip_ids[0]][1] > landmark_list[self.tip_ids[0] - 1][1]:
    #             open_tips.append(1)
    #         else:
    #             open_tips.append(0)

    #         #  four fingers
    #         for i in range(1, 5):
    #             if landmark_list[self.tip_ids[i]][2] < landmark_list[self.tip_ids[i] - 2][2]:
    #                 open_tips.append(1)
    #             else:
    #                 open_tips.append(0)

    #     return open_tips
