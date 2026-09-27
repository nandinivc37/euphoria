import math

import cv2
import numpy as np

from effects.anchors import EffectAnchor


class FocusSystem:
    """
    Camera-layer hand web.

    Each hand is handled independently.
    A web is drawn only for hands whose individual
    gesture is FOCUS or FIVE.
    """

    def __init__(self):
        self.active = False
        self.strength = 0.0
        self.time = 0.0

        self.active_hand_anchors: list[
            dict[str, EffectAnchor]
        ] = []

    def update(
        self,
        dt: float,
        active_hand_anchors: list[
            dict[str, EffectAnchor]
        ],
    ):
        self.time += dt

        self.active_hand_anchors = (
            active_hand_anchors
        )

        self.active = bool(
            active_hand_anchors
        )

        target_strength = (
            1.0 if self.active else 0.0
        )

        fade_speed = 8.0

        self.strength += (
            target_strength
            - self.strength
        ) * min(
            1.0,
            fade_speed * dt,
        )

    def render(self, frame):

        if self.strength <= 0.01:
            return frame

        fingertip_names = (
            "index_tip",
            "middle_tip",
            "ring_tip",
            "pinky_tip",
        )

        color = (
            255,
            255,
            255,
        )

        pulse = (
            0.5
            + 0.5
            * math.sin(
                self.time * 5.0
            )
        )

        glow_layer = np.zeros_like(
            frame
        )

        # ---------------------------------
        # Glow
        # ---------------------------------

        for anchors in (
            self.active_hand_anchors
        ):

            if not all(
                name in anchors
                for name in (
                    "thumb_tip",
                    "index_tip",
                    "middle_tip",
                    "ring_tip",
                    "pinky_tip",
                )
            ):
                continue

            thumb = anchors[
                "thumb_tip"
            ]

            for name in fingertip_names:

                fingertip = anchors[name]

                cv2.line(
                    glow_layer,
                    (
                        thumb.x,
                        thumb.y,
                    ),
                    (
                        fingertip.x,
                        fingertip.y,
                    ),
                    color,
                    5,
                    cv2.LINE_AA,
                )

        glow_layer = cv2.GaussianBlur(
            glow_layer,
            (0, 0),
            sigmaX=7,
            sigmaY=7,
        )

        frame = cv2.addWeighted(
            frame,
            1.0,
            glow_layer,
            0.65 * self.strength,
            0,
        )

        # ---------------------------------
        # Core lines + points
        # ---------------------------------

        for anchors in (
            self.active_hand_anchors
        ):

            if not all(
                name in anchors
                for name in (
                    "thumb_tip",
                    "index_tip",
                    "middle_tip",
                    "ring_tip",
                    "pinky_tip",
                )
            ):
                continue

            thumb = anchors[
                "thumb_tip"
            ]

            for name in fingertip_names:

                fingertip = anchors[name]

                cv2.line(
                    frame,
                    (
                        thumb.x,
                        thumb.y,
                    ),
                    (
                        fingertip.x,
                        fingertip.y,
                    ),
                    color,
                    1,
                    cv2.LINE_AA,
                )

            # Thumb
            cv2.circle(
                frame,
                (
                    thumb.x,
                    thumb.y,
                ),
                int(4 + 3 * pulse),
                color,
                -1,
                cv2.LINE_AA,
            )

            # Fingertips
            for name in fingertip_names:

                fingertip = anchors[name]

                cv2.circle(
                    frame,
                    (
                        fingertip.x,
                        fingertip.y,
                    ),
                    int(3 + 2 * pulse),
                    color,
                    -1,
                    cv2.LINE_AA,
                )

        return frame

    def reset(self):
        self.active = False
        self.strength = 0.0
        self.active_hand_anchors.clear()