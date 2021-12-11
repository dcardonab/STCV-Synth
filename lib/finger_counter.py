# Python Libraries
import time

# Third-Party Libraries
import cv2

# Local Files
from hand_tracking import HandDetector as hd


def finger_visible(img, fingers, colors):
    output_frame = img.copy()
    for num in fingers:
        cv2.rectangle(
            output_frame,
            (0, 60 + num * 40),
            (int(1.0 * 100), 90 + num * 40),
            colors[num],
            -1,
        )
        cv2.putText(
            output_frame,
            fingers[num],
            (0, 85 + num * 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    return output_frame
