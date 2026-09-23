import time

import cv2
import numpy as np

from camera.camera import Camera
from hand_tracking.detector import HandDetector

from gestures.classifier import GestureClassifier
from gestures.definitions import Gesture
from gestures.events import GestureEventManager
from gestures.stabilizer import GestureStabilizer

from effects.anchors import AnchorExtractor, EffectAnchor
from effects.engine import EffectsEngine


OUTPUT_WIDTH = 1200
OUTPUT_HEIGHT = 900

CAMERA_HEIGHT = OUTPUT_HEIGHT // 2
SEPARATOR_HEIGHT = 3
WORLD_HEIGHT = (
    OUTPUT_HEIGHT
    - CAMERA_HEIGHT
    - SEPARATOR_HEIGHT
)


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

    anchor_extractor = None

    print("Gesture Visual Controller started.")
    print("Press Q to quit.")

    # -----------------------------
    # Create output window
    # -----------------------------

    window_name = "Gesture Visual Controller"

    cv2.namedWindow(
        window_name,
        cv2.WINDOW_NORMAL,
    )

    cv2.resizeWindow(
        window_name,
        OUTPUT_WIDTH,
        OUTPUT_HEIGHT,
    )

    previous_time = time.perf_counter()

    try:
        while True:

            # -----------------------------
            # Capture camera frame
            # -----------------------------

            camera_frame = camera.read()

            camera_height_original, camera_width_original = (
                camera_frame.shape[:2]
            )

            # -----------------------------
            # Create anchor extractor once
            # -----------------------------

            if anchor_extractor is None:
                anchor_extractor = AnchorExtractor(
                    width=camera_width_original,
                    height=camera_height_original,
                )

            # -----------------------------
            # Detect hand
            # -----------------------------

            results = detector.process(
                camera_frame
            )

            hands = detector.extract_landmarks(
                results
            )

            # -----------------------------
            # Calculate delta time
            # -----------------------------

            current_time = time.perf_counter()

            dt = (
                current_time
                - previous_time
            )

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

                # Classify gesture
                raw_gesture = classifier.classify(
                    hand
                )

                # Camera-space anchors
                camera_anchors = (
                    anchor_extractor.from_hand(
                        hand
                    )
                )

                # ---------------------------------
                # Convert hand coordinates into
                # bottom-world coordinates
                # ---------------------------------

                for name, anchor in camera_anchors.items():

                    world_x = int(
                        anchor.x
                        * OUTPUT_WIDTH
                        / camera_width_original
                    )

                    world_y = int(
                        anchor.y
                        * WORLD_HEIGHT
                        / camera_height_original
                    )

                    anchors[name] = EffectAnchor(
                        name=anchor.name,
                        x=world_x,
                        y=world_y,
                    )

            # -----------------------------
            # Stabilize gesture
            # -----------------------------

            stable_gesture = stabilizer.update(
                raw_gesture
            )

            # -----------------------------
            # Create gesture event
            # -----------------------------

            event = event_manager.update(
                stable_gesture,
                anchors,
            )

            if event:
                effects.handle_event(event)

            # -----------------------------
            # Update effects
            # -----------------------------

            effects.update(
                dt,
                stable_gesture,
                anchors,
            )

            # -----------------------------
            # Create world canvas
            # -----------------------------

            world_frame = np.zeros(
                (
                    WORLD_HEIGHT,
                    OUTPUT_WIDTH,
                    3,
                ),
                dtype=np.uint8,
            )

            world_frame = effects.render(
                world_frame
            )

            # -----------------------------
            # Create camera panel
            # -----------------------------

            camera_panel = cv2.resize(
                camera_frame,
                (
                    OUTPUT_WIDTH,
                    CAMERA_HEIGHT,
                ),
                interpolation=cv2.INTER_AREA,
            )

            # Draw MediaPipe landmarks
            camera_panel = (
                detector.draw_landmarks(
                    camera_panel,
                    results,
                )
            )

            # -----------------------------
            # Gesture text
            # -----------------------------

            if stable_gesture != Gesture.UNKNOWN:

                cv2.putText(
                    camera_panel,
                    f"Gesture: {stable_gesture.value}",
                    (25, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            # -----------------------------
            # Separator
            # -----------------------------

            separator = np.zeros(
                (
                    SEPARATOR_HEIGHT,
                    OUTPUT_WIDTH,
                    3,
                ),
                dtype=np.uint8,
            )

            separator[:] = (
                180,
                80,
                180,
            )

            # -----------------------------
            # Combine camera + world
            # -----------------------------

            output = np.vstack(
                (
                    camera_panel,
                    separator,
                    world_frame,
                )
            )

            # -----------------------------
            # Display
            # -----------------------------

            cv2.imshow(
                window_name,
                output,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        detector.close()
        camera.release()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()