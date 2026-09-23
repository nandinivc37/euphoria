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

    camera = Camera(
        camera_index=0
    )

    detector = HandDetector()

    classifier = GestureClassifier()

    stabilizer = GestureStabilizer(
        required_frames=5,
        unknown_frames=8,
    )

    event_manager = GestureEventManager()

    effects = EffectsEngine()

    anchor_extractor = None

    print(
        "Gesture Visual Controller started."
    )

    print(
        "Press Q to quit."
    )

    # -----------------------------
    # Create output window
    # -----------------------------

    window_name = (
        "Gesture Visual Controller"
    )

    cv2.namedWindow(
        window_name,
        cv2.WINDOW_NORMAL,
    )

    cv2.resizeWindow(
        window_name,
        OUTPUT_WIDTH,
        OUTPUT_HEIGHT,
    )

    previous_time = (
        time.perf_counter()
    )

    try:

        while True:

            # -----------------------------
            # Capture camera frame
            # -----------------------------

            camera_frame = camera.read()

            (
                camera_height_original,
                camera_width_original,
            ) = camera_frame.shape[:2]

            # -----------------------------
            # Create anchor extractor once
            # -----------------------------

            if anchor_extractor is None:

                anchor_extractor = (
                    AnchorExtractor(
                        width=camera_width_original,
                        height=camera_height_original,
                    )
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
            # Delta time
            # -----------------------------

            current_time = (
                time.perf_counter()
            )

            dt = (
                current_time
                - previous_time
            )

            previous_time = current_time

            # -----------------------------
            # Defaults
            # -----------------------------

            raw_gesture = Gesture.UNKNOWN

            camera_anchors = {}
            world_anchors = {}

            # -----------------------------
            # Process hand
            # -----------------------------

            if hands:

                hand = hands[0]

                # Gesture
                raw_gesture = (
                    classifier.classify(
                        hand
                    )
                )

                # Raw camera-space anchors
                raw_anchors = (
                    anchor_extractor.from_hand(
                        hand
                    )
                )

                # ---------------------------------
                # Camera panel coordinates
                # ---------------------------------

                for name, anchor in (
                    raw_anchors.items()
                ):

                    camera_x = int(
                        anchor.x
                        * OUTPUT_WIDTH
                        / camera_width_original
                    )

                    camera_y = int(
                        anchor.y
                        * CAMERA_HEIGHT
                        / camera_height_original
                    )

                    camera_anchors[name] = (
                        EffectAnchor(
                            name=anchor.name,
                            x=camera_x,
                            y=camera_y,
                        )
                    )

                # ---------------------------------
                # World coordinates
                # ---------------------------------

                for name, anchor in (
                    raw_anchors.items()
                ):

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

                    world_anchors[name] = (
                        EffectAnchor(
                            name=anchor.name,
                            x=world_x,
                            y=world_y,
                        )
                    )

            # -----------------------------
            # Stabilize gesture
            # -----------------------------

            stable_gesture = (
                stabilizer.update(
                    raw_gesture
                )
            )

            # -----------------------------
            # Event
            # -----------------------------

            event = (
                event_manager.update(
                    stable_gesture,
                    world_anchors,
                )
            )

            if event:
                effects.handle_event(
                    event
                )

            # -----------------------------
            # Update effects
            # -----------------------------

            effects.update(
                dt,
                stable_gesture,
                world_anchors,
                camera_anchors,
            )

            # -----------------------------
            # WORLD
            # -----------------------------

            world_frame = np.zeros(
                (
                    WORLD_HEIGHT,
                    OUTPUT_WIDTH,
                    3,
                ),
                dtype=np.uint8,
            )

            world_frame = (
                effects.render_world(
                    world_frame
                )
            )

            # -----------------------------
            # CAMERA
            # -----------------------------

            camera_panel = cv2.resize(
                camera_frame,
                (
                    OUTPUT_WIDTH,
                    CAMERA_HEIGHT,
                ),
                interpolation=cv2.INTER_AREA,
            )

            # MediaPipe skeleton
            camera_panel = (
                detector.draw_landmarks(
                    camera_panel,
                    results,
                )
            )

            # White thumb-fingertip web
            camera_panel = (
                effects.render_camera(
                    camera_panel
                )
            )

            # -----------------------------
            # Gesture text
            # -----------------------------

            if (
                stable_gesture
                != Gesture.UNKNOWN
            ):

                cv2.putText(
                    camera_panel,
                    (
                        f"Gesture: "
                        f"{stable_gesture.value}"
                    ),
                    (
                        25,
                        50,
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (
                        255,
                        255,
                        255,
                    ),
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
            # Final output
            # -----------------------------

            output = np.vstack(
                (
                    camera_panel,
                    separator,
                    world_frame,
                )
            )

            cv2.imshow(
                window_name,
                output,
            )

            if (
                cv2.waitKey(1) & 0xFF
                == ord("q")
            ):
                break

    finally:

        detector.close()
        camera.release()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()