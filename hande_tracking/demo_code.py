from handtracking import HandDetector as hd
import cv2
import time


def demo_hand_tracker(w_cam=640, h_cam=480):
    p_time = 0
    cap = cv2.VideoCapture(0)
    cap.set(3, w_cam)
    cap.set(4, h_cam)

    detector = hd(min_detection_confidence=0.75)

    while True:
        success, img = cap.read()
        img = detector.findHands(img)

        if detector.handCount() > 0:
            for handNumber in range(0, detector.handCount()):
                lmList = detector.find_position(img, handNumber=handNumber, draw=False)

                if len(lmList) != 0:
                    print(detector.is_left_or_right_hand(handNumber))
                    fingersOpen = detector.finger_is_open(lmList)
                    print(fingersOpen)

                print(detector.find_z_depth(img, handNumber=handNumber))

        cTime = time.time()
        fps = 1 / (cTime - p_time)
        p_time = cTime

        cv2.putText(img, f'FPS: {int(fps)}', (400, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    demo_hand_tracker()

