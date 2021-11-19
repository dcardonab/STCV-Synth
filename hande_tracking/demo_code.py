from handtracking import HandDetector as hd
import cv2
import time

def demo_handtracker(wCam=640, hCam=480):

    pTime = 0
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)

    detector = hd(min_detection_confidence=0.75)

    while True:
        success, img = cap.read()
        img = detector.findHands(img)

        if detector.handCount() > 0:
            for handNumber in range(0, detector.handCount()):
                lmList = detector.findPosition(img, handNumber=handNumber, draw=False)
                
                # Here you can determine the hand and it finger positions, either opened or closed
                if len(lmList) != 0:
                    print(detector.isLeftorRightHand(handNumber))
                    fingersOpen = detector.fingerIsOpen(lmList)
                    print(fingersOpen)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, f'FPS: {int(fps)}', (400, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    demo_handtracker()
