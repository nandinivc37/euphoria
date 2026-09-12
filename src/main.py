import time

import cv2

from camera.camera import Camera
from hand_tracking.detector import HandDetector

from gestures.classifier import GestureClassifier
from gestures.events import GestureEventManager

from effects.engine import EffectsEngine


def main():
    # -----------------------------
    # 1. Initialize all components
    # -----------------------------

    camera = Camera(camera_index=0)
    detector = HandDetector()

    classifier = GestureClassifier()
    event_manager = GestureEventManager()
    effects = EffectsEngine()

    print("Gesture Visual Controller started.")
    print("Press Q to quit.")

    # Used to calculate time between frames
    previous_time = time.perf_counter()

    try:
        # -----------------------------
        # 2. Main application loop
        # -----------------------------

        while True:

            # Get frame from webcam
            frame = camera.read()

            # --------------------------------
            # 3. Detect hand landmarks
            # --------------------------------

            results = detector.process(frame)

            # Convert MediaPipe result into
            # our own HandLandmarks objects
            hands = detector.extract_landmarks(results)

            # --------------------------------
            # 4. Calculate frame time
            # --------------------------------

            current_time = time.perf_counter()

            dt = current_time - previous_time

            previous_time = current_time

            # --------------------------------
            # 5. Recognize gesture
            # --------------------------------

            gesture = None

            if hands:

                # For now, use the first detected hand
                hand = hands[0]

                # Classify the hand pose
                gesture = classifier.classify(hand)

                # --------------------------------
                # 6. Find hand position
                # --------------------------------

                height, width, _ = frame.shape

                # Landmark 0 = wrist
                hand_x = int(hand[0].x * width)
                hand_y = int(hand[0].y * height)

                # --------------------------------
                # 7. Convert gesture into an event
                # --------------------------------

                event = event_manager.update(
                    gesture,
                    hand_x,
                    hand_y,
                )

                # If this is a NEW gesture,
                # send it to the effects engine
                if event:

                    effects.handle_event(event)

            # --------------------------------
            # 8. Update visual effects
            # --------------------------------

            effects.update(dt)

            # --------------------------------
            # 9. Draw hand landmarks
            # --------------------------------

            frame = detector.draw_landmarks(
                frame,
                results,
            )

            # --------------------------------
            # 10. Draw visual effects
            # --------------------------------

            frame = effects.render(frame)

            # --------------------------------
            # 11. Display current gesture
            # --------------------------------

            if gesture:

                cv2.putText(
                    frame,
                    f"Gesture: {gesture.value}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                )

            # --------------------------------
            # 12. Show final frame
            # --------------------------------

            cv2.imshow(
                "Gesture Visual Controller",
                frame,
            )

            # Press Q to quit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        # --------------------------------
        # 13. Clean everything up
        # --------------------------------

        detector.close()
        camera.release()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
