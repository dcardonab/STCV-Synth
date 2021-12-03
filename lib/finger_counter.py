import cv2
import time
import os
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


wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)


pTime = 0
detector = hd(min_detection_confidence=0.75)

while True:
    success, img = cap.read()
    img = detector.findHands(img)

    if detector.handCount() > 0:
        for handNumber in range(0, detector.handCount()):
            lmList = detector.find_position(img, hand_number=handNumber, draw=False)

            if len(lmList) != 0:
                print(detector.is_left_or_right_hand(handNumber))
                fingersOpen = detector.finger_is_open(lmList)
                print(fingersOpen)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(
        img, f"FPS: {int(fps)}", (400, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 2
    )
    cv2.imshow("Image", img)
    cv2.waitKey(1)
