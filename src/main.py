import time
import math
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


# --------------------------------
# Portrait 3:4 output
# --------------------------------

OUTPUT_WIDTH = 900
OUTPUT_HEIGHT = 1200

# 50 / 50 camera + world
CAMERA_HEIGHT = OUTPUT_HEIGHT // 2

SEPARATOR_HEIGHT = 3

WORLD_HEIGHT = (
    OUTPUT_HEIGHT
    - CAMERA_HEIGHT
    - SEPARATOR_HEIGHT
)



def get_hand_rotation_angle(hand):
    wrist = hand.wrist
    thumb = hand.points[2]

    dx = thumb.x - wrist.x
    dy = thumb.y - wrist.y

    return math.degrees(
        math.atan2(
            -dy,
            dx,
        )
    )

def crop_camera_to_panel(
    frame,
    target_width,
    target_height,
):
    """
    Resize the camera proportionally so it fills
    the panel width, then crop vertically.
    """

    source_height, source_width = frame.shape[:2]

    # Scale according to width.
    scale = (
        target_width / source_width
    )

    new_width = int(
        source_width * scale
    )

    new_height = int(
        source_height * scale
    )

    resized = cv2.resize(
        frame,
        (
            new_width,
            new_height,
        ),
        interpolation=cv2.INTER_AREA,
    )

    # Center crop vertically.
    crop_top = max(
        0,
        (
            new_height
            - target_height
        ) // 2,
    )

    cropped = resized[
        crop_top:
        crop_top + target_height,
        :
    ]

    return (
        cropped,
        scale,
        crop_top,
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

    effects = EffectsEngine(
        world_width=OUTPUT_WIDTH,
        world_height=WORLD_HEIGHT,
    )

    anchor_extractor = None

    print(
        "Gesture Visual Controller started."
    )

    print(
        "Press Q to quit."
    )

    # -----------------------------
    # Output window
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

    pinch_states = {}

    previous_left_palm_open = False

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
            # Detect hands
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
            camera_anchor_list = []

            world_anchors = {}

            # IMPORTANT:
            # This must be created BEFORE
            # processing the hands.
            active_camera_hands = []

            right_palm_open = False
            left_palm_open = False

            right_palm_angle = None

            pinch_trigger = False

            #-----------------------------
            # Pinch detection
            #-----------------------------

            for hand_index, hand in enumerate(hands):

                hand_gesture = classifier.classify(hand)

                if (
                    hand.is_right
                    and hand_gesture == Gesture.FIVE
                ):
                    right_palm_open = True
                    right_palm_angle = (
                        get_hand_rotation_angle(hand)
                    )

                if (
                    hand.is_left
                    and hand_gesture == Gesture.FIVE
                ):
                    left_palm_open = True

                # pinch detection goes HERE
                dx = hand.thumb_tip.x - hand.index_tip.x
                dy = hand.thumb_tip.y - hand.index_tip.y

                pinch_distance = (dx * dx + dy * dy) ** 0.5

                hand_key = (
                    hand.handedness
                    if hand.handedness != "Unknown"
                    else f"hand_{hand_index}"
                )

                was_pinched = pinch_states.get(
                    hand_key,
                    False,
                )

                if not was_pinched and pinch_distance < 0.045:
                    pinch_states[hand_key] = True
                    pinch_trigger = True

                elif was_pinched and pinch_distance > 0.065:
                    pinch_states[hand_key] = False

            

            # -----------------------------
            # Process detected hands
            # -----------------------------

            if hands:

                # ---------------------------------
                # Primary hand
                # ---------------------------------

                primary_hand = hands[0]

                # Primary hand still controls
                # the world gesture for now.
                raw_gesture = classifier.classify(
                    primary_hand
                )

                

                # ---------------------------------
                # Process every detected hand
                # ---------------------------------

                for hand in hands:

                    raw_anchors = (
                        anchor_extractor.from_hand(
                            hand
                        )
                    )

                    # ---------------------------------
                    # Gesture for THIS hand
                    # ---------------------------------

                    hand_gesture = (
                        classifier.classify(
                            hand
                        )
                    )

                    # ---------------------------------
                    # Independent hand roles
                    # ---------------------------------

                    if (
                        hand.is_right
                        and hand_gesture == Gesture.FIVE
                    ):
                        right_palm_open = True

                        # Right-hand rotation angle.
                        dx = (
                            hand.thumb_tip.x
                            - hand.wrist.x
                        )

                        dy = (
                            hand.thumb_tip.y
                            - hand.wrist.y
                        )

                        right_palm_angle = math.degrees(
                            math.atan2(-dy, dx)
                        )

                    if (
                        hand.is_left
                        and hand_gesture == Gesture.FIVE
                    ):
                        left_palm_open = True

                    if hand.is_right and hand_gesture == Gesture.FIVE:
                        right_palm_open = True

                    # ---------------------------------
                    # World coordinates
                    #
                    # For now, world effects are
                    # controlled by the primary hand.
                    # ---------------------------------

                    if hand.is_right:

                        for (
                            name,
                            anchor,
                        ) in raw_anchors.items():

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

                    # ---------------------------------
                    # Camera-space anchors
                    #
                    # Keep these in the ORIGINAL
                    # camera coordinate system for now.
                    # We transform them after the camera
                    # panel is created.
                    # ---------------------------------

                    if hand_gesture in (
                        Gesture.FOCUS,
                        Gesture.FIVE,
                    ):

                        active_camera_hands.append(
                            raw_anchors
                        )


            left_palm_released = (
                previous_left_palm_open
                and not left_palm_open
            )

            if left_palm_released:
                effects.reset()

            previous_left_palm_open = left_palm_open

            
            # -----------------------------
            # Stabilize primary gesture
            # -----------------------------

            stable_gesture = (
                stabilizer.update(
                    raw_gesture
                )
            )

            # -----------------------------
            # Gesture event
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
            # Create camera image with
            # MediaPipe landmarks FIRST
            # -----------------------------

            camera_annotated = (
                camera_frame.copy()
            )

            camera_annotated = (
                detector.draw_landmarks(
                    camera_annotated,
                    results,
                )
            )

            # -----------------------------
            # Fit camera into portrait panel
            # -----------------------------

            (
                camera_panel,
                camera_scale,
                crop_top,
            ) = crop_camera_to_panel(
                camera_annotated,
                OUTPUT_WIDTH,
                CAMERA_HEIGHT,
            )

            # -----------------------------
            # Transform only the active
            # hand webs into the final
            # camera-panel coordinates
            # -----------------------------

            transformed_active_hands = []

            for hand_anchors in (
                active_camera_hands
            ):

                transformed = {}

                for (
                    name,
                    anchor,
                ) in hand_anchors.items():

                    x = int(
                        anchor.x
                        * camera_scale
                    )

                    y = int(
                        anchor.y
                        * camera_scale
                        - crop_top
                    )

                    transformed[name] = (
                        EffectAnchor(
                            name=anchor.name,
                            x=x,
                            y=y,
                        )
                    )

                transformed_active_hands.append(
                    transformed
                )

            # -----------------------------
            # Update effects
            # -----------------------------

            effects.update(
                dt,
                stable_gesture,
                world_anchors,
                transformed_active_hands,
                right_palm_open,
                left_palm_open,
                right_palm_angle,
                pinch_trigger,
            )

            # -----------------------------
            # White camera-layer web
            # -----------------------------

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
            # World canvas
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
            # Final portrait output
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