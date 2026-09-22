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
            # Get camera frame
            # -----------------------------

            frame = camera.read()

            height, width, _ = frame.shape

            # -----------------------------
            # Detect hand landmarks
            # -----------------------------

            results = detector.process(frame)

            hands = detector.extract_landmarks(results)

            # -----------------------------
            # Calculate delta time
            # -----------------------------

            current_time = time.perf_counter()

            dt = current_time - previous_time
            previous_time = current_time

            # -----------------------------
            # Default: no hand
            # -----------------------------

            raw_gesture = Gesture.UNKNOWN
            anchors = {}

            # -----------------------------
            # Process detected hand
            # -----------------------------

            if hands:

                # For now, use the first detected hand
                hand = hands[0]

                # Raw gesture from classifier
                raw_gesture = classifier.classify(hand)

                states = classifier.finger_states(hand)

                cv2.putText(
                    frame,
                    f"Thumb: {states['thumb'].value}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Index: {states['index'].value}",
                    (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Middle: {states['middle'].value}",
                    (20, 140),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Ring: {states['ring'].value}",
                    (20, 170),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Pinky: {states['pinky'].value}",
                    (20, 200),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Raw: {raw_gesture.value}",
                    (20, 230),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

                # -----------------------------
                # Extract hand anchors
                # -----------------------------

                anchor_extractor = AnchorExtractor(
                    width=width,
                    height=height,
                )

                anchors = anchor_extractor.from_hand(hand)

            # -----------------------------
            # Stabilize gesture
            # -----------------------------

            stable_gesture = stabilizer.update(
                raw_gesture
            )

            # -----------------------------
            # Gesture → Event
            # -----------------------------

            event = event_manager.update(
                stable_gesture,
                anchors,
            )

            if event:
                effects.handle_event(event)

            # -----------------------------
            # Update visual effects
            # -----------------------------

            effects.update(dt)

            # -----------------------------
            # Draw hand landmarks
            # -----------------------------

            frame = detector.draw_landmarks(
                frame,
                results,
            )

            # -----------------------------
            # Draw effects
            # -----------------------------

            frame = effects.render(frame)

            # -----------------------------
            # Display stable gesture
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
            # Show final frame
            # -----------------------------

            cv2.imshow(
                "Gesture Visual Controller",
                frame,
            )

            # -----------------------------
            # Quit
            # -----------------------------

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        detector.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()