import math

import cv2
import numpy as np

from effects.anchors import EffectAnchor


class FocusSystem:
    """
    Visual effect for the FOCUS gesture.

    The thumb acts as the central anchor.
    Lines connect the thumb tip to every other
    fingertip and follow the hand in real time.
    """

    def __init__(self):
        self.active = False
        self.strength = 0.0
        self.time = 0.0

        self.anchors: dict[str, EffectAnchor] = {}

    def update(
        self,
        dt: float,
        active: bool,
        anchors: dict[str, EffectAnchor],
    ):
        self.time += dt
        self.active = active

        # Keep the most recent hand geometry while active.
        if active:
            self.anchors = anchors

        # Smooth appearance/disappearance.
        target_strength = 1.0 if active else 0.0

        fade_speed = 8.0

        self.strength += (
            target_strength - self.strength
        ) * min(1.0, fade_speed * dt)

    def _distance(
        self,
        a: EffectAnchor,
        b: EffectAnchor,
    ) -> float:
        dx = b.x - a.x
        dy = b.y - a.y

        return math.sqrt(
            dx * dx + dy * dy
        )

    def render(self, frame):
        if self.strength <= 0.01:
            return frame

        required = (
            "thumb_tip",
            "index_tip",
            "middle_tip",
            "ring_tip",
            "pinky_tip",
        )

        if not all(
            name in self.anchors
            for name in required
        ):
            return frame

        thumb = self.anchors["thumb_tip"]

        fingertip_names = (
            "index_tip",
            "middle_tip",
            "ring_tip",
            "pinky_tip",
        )

        # -----------------------------
        # Pulse
        # -----------------------------

        pulse = (
            0.5
            + 0.5 * math.sin(self.time * 5.0)
        )

        # Yellow in OpenCV BGR.
        color = (255, 255, 255)

        # Transparent-style glow layer.
        glow_layer = np.zeros_like(frame)

        # -----------------------------
        # Draw thin glow lines
        # -----------------------------

        for name in fingertip_names:

            fingertip = self.anchors[name]

            start = (
                thumb.x,
                thumb.y,
            )

            end = (
                fingertip.x,
                fingertip.y,
            )

            # Soft outer glow.
            cv2.line(
                glow_layer,
                start,
                end,
                color,
                6,
                cv2.LINE_AA,
            )

        # -----------------------------
        # Blur glow
        # -----------------------------

        glow_layer = cv2.GaussianBlur(
            glow_layer,
            (0, 0),
            sigmaX=8,
            sigmaY=8,
        )

        frame = cv2.addWeighted(
            frame,
            1.0,
            glow_layer,
            0.65 * self.strength,
            0,
        )

        # -----------------------------
        # Thin core lines
        # -----------------------------

        core_thickness = 1

        for name in fingertip_names:

            fingertip = self.anchors[name]

            cv2.line(
                frame,
                (thumb.x, thumb.y),
                (fingertip.x, fingertip.y),
                color,
                core_thickness,
                cv2.LINE_AA,
            )

        # -----------------------------
        # Thumb glow point
        # -----------------------------

        thumb_radius = int(
            4 + 3 * pulse
        )

        cv2.circle(
            frame,
            (thumb.x, thumb.y),
            thumb_radius,
            color,
            -1,
            cv2.LINE_AA,
        )

        # -----------------------------
        # Fingertip glow points
        # -----------------------------

        for name in fingertip_names:

            fingertip = self.anchors[name]

            radius = int(
                3 + 2 * pulse
            )

            cv2.circle(
                frame,
                (fingertip.x, fingertip.y),
                radius,
                color,
                -1,
                cv2.LINE_AA,
            )

        return frame

    def reset(self):
        self.active = False
        self.strength = 0.0
        self.anchors.clear()