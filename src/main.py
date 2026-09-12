import cv2

from camera.camera import Camera
from gestures.classifier import GestureClassifier
from hand_tracking.detector import HandDetector


def main():
    camera = Camera(camera_index=0)
    detector = HandDetector()
    classifier = GestureClassifier()

    print("Gesture Visual Controller started.")
    print("Press Q to quit.")

    try:
        while True:
            frame = camera.read()

            results = detector.process(frame)

            hands = detector.extract_landmarks(results)

            if hands:
                gesture = classifier.classify(hands[0])

                cv2.putText(
                    frame,
                    f"Gesture: {gesture.value}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                )

            frame = detector.draw_landmarks(
                frame,
                results,
            )

            cv2.imshow(
                "Gesture Visual Controller",
                frame,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        detector.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
