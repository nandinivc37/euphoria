import time

import cv2

from camera.camera import Camera
from hand_tracking.detector import HandDetector

from gestures.classifier import GestureClassifier
from gestures.events import GestureEventManager

from effects.anchors import AnchorExtractor
from effects.engine import EffectsEngine


def main():
    # -----------------------------
    # Initialize components
    # -----------------------------

    camera = Camera(camera_index=0)
    detector = HandDetector()

    classifier = GestureClassifier()
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

            gesture = None

            # -----------------------------
            # Process first detected hand
            # -----------------------------

            if hands:

                hand = hands[0]

                # Recognize gesture
                gesture = classifier.classify(hand)

                # -----------------------------
                # Extract named anchors
                # -----------------------------

                anchor_extractor = AnchorExtractor(
                    width=width,
                    height=height,
                )

                anchors = anchor_extractor.from_hand(hand)

                # -----------------------------
                # Gesture → Event
                # -----------------------------

                event = event_manager.update(
                    gesture,
                    anchors,
                )

                if event:
                    effects.handle_event(event)

            # -----------------------------
            # Update effects
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
            # Display gesture
            # -----------------------------

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

            # -----------------------------
            # Show final frame
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