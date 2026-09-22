import time

import cv2

from camera.camera import Camera
from hand_tracking.detector import HandDetector

from gestures.classifier import GestureClassifier
from gestures.definitions import Gesture
from gestures.events import GestureEventManager
from gestures.stabilizer import GestureStabilizer

from effects.anchors import AnchorExtractor
from effects.engine import EffectsEngine


def main():
    # -----------------------------
    # Initialize components
    # -----------------------------

    camera = Camera(camera_index=0)
    detector = HandDetector()

    classifier = GestureClassifier()

    stabilizer = GestureStabilizer(
        required_frames=5,
        unknown_frames=8,
    )

    event_manager = GestureEventManager()
    effects = EffectsEngine()

    print("Gesture Visual Controller started.")
    print("Press Q to quit.")

    previous_time = time.perf_counter()

    try:
        while True:

            # -----------------------------
            # Capture frame
            # -----------------------------

            frame = camera.read()

            height, width, _ = frame.shape

            # -----------------------------
            # Detect hand
            # -----------------------------

            results = detector.process(frame)

            hands = detector.extract_landmarks(
                results
            )

            # -----------------------------
            # Calculate delta time
            # -----------------------------

            current_time = time.perf_counter()

            dt = current_time - previous_time
            previous_time = current_time

            # -----------------------------
            # Defaults
            # -----------------------------

            raw_gesture = Gesture.UNKNOWN
            anchors = {}

            # -----------------------------
            # Process detected hand
            # -----------------------------

            if hands:

                hand = hands[0]

                # Raw classification
                raw_gesture = classifier.classify(
                    hand
                )

                # -----------------------------
                # Extract named anchors
                # -----------------------------

                anchor_extractor = AnchorExtractor(
                    width=width,
                    height=height,
                )

                anchors = (
                    anchor_extractor.from_hand(
                        hand
                    )
                )

            # -----------------------------
            # Stabilize gesture
            # -----------------------------

            stable_gesture = stabilizer.update(
                raw_gesture
            )

            # -----------------------------
            # Create event on gesture change
            # -----------------------------

            event = event_manager.update(
                stable_gesture,
                anchors,
            )

            if event:
                effects.handle_event(event)

            # -----------------------------
            # Update particles + beams
            # -----------------------------

            effects.update(
                dt,
                stable_gesture,
                anchors,
            )

            # -----------------------------
            # Draw visual effects FIRST
            # -----------------------------

            frame = effects.render(frame)

            # -----------------------------
            # Draw hand landmarks ON TOP
            # -----------------------------

            frame = detector.draw_landmarks(
                frame,
                results,
            )

            # -----------------------------
            # Display gesture
            # -----------------------------

            if stable_gesture != Gesture.UNKNOWN:

                cv2.putText(
                    frame,
                    f"Gesture: {stable_gesture.value}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                )

            # -----------------------------
            # Display
            # -----------------------------

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