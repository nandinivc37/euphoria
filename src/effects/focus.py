import math

import cv2
import numpy as np

from effects.anchors import EffectAnchor


class FocusSystem:
    """
    Continuous visual effect for the FOCUS/L gesture.

    The effect is anchored between the thumb and index
    fingertips and follows them in real time.
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

        if active:
            self.anchors = anchors

        target_strength = 1.0 if active else 0.0
        fade_speed = 7.0

        self.strength += (
            target_strength - self.strength
        ) * min(1.0, fade_speed * dt)

    def render(self, frame):
        if self.strength <= 0.01:
            return frame

        required = (
            "thumb_tip",
            "index_tip",
        )

        if not all(
            name in self.anchors
            for name in required
        ):
            return frame

        thumb = self.anchors["thumb_tip"]
        index = self.anchors["index_tip"]

        center_x = (thumb.x + index.x) // 2
        center_y = (thumb.y + index.y) // 2

        dx = index.x - thumb.x
        dy = index.y - thumb.y

        distance = math.sqrt(
            dx * dx + dy * dy
        )

        radius = int(
            max(
                18,
                min(65, distance * 0.55),
            )
        )

        pulse = (
            0.5
            + 0.5 * math.sin(self.time * 5.0)
        )

        # Yellow in OpenCV BGR format.
        color = (0, 255, 255)

        glow_layer = np.zeros_like(frame)

        # Connecting line
        cv2.line(
            glow_layer,
            (thumb.x, thumb.y),
            (index.x, index.y),
            color,
            12,
            cv2.LINE_AA,
        )

        # Main pulsing ring
        pulse_radius = radius + int(5 * pulse)

        cv2.circle(
            glow_layer,
            (center_x, center_y),
            pulse_radius,
            color,
            8,
            cv2.LINE_AA,
        )

        # Outer ring
        outer_radius = radius + 10 + int(8 * pulse)

        cv2.circle(
            glow_layer,
            (center_x, center_y),
            outer_radius,
            color,
            4,
            cv2.LINE_AA,
        )

        # Blur = glow
        glow_layer = cv2.GaussianBlur(
            glow_layer,
            (0, 0),
            sigmaX=10,
            sigmaY=10,
        )

        frame = cv2.addWeighted(
            frame,
            1.0,
            glow_layer,
            0.8 * self.strength,
            0,
        )

        # Bright core line
        core_thickness = max(
            1,
            int(2 * self.strength),
        )

        cv2.line(
            frame,
            (thumb.x, thumb.y),
            (index.x, index.y),
            color,
            core_thickness,
            cv2.LINE_AA,
        )

        # Reticle corners
        corner_length = max(
            8,
            int(radius * 0.35),
        )

        x1 = center_x - radius
        y1 = center_y - radius

        x2 = center_x + radius
        y2 = center_y + radius

        # Top-left
        cv2.line(
            frame,
            (x1, y1),
            (x1 + corner_length, y1),
            color,
            2,
            cv2.LINE_AA,
        )

        cv2.line(
            frame,
            (x1, y1),
            (x1, y1 + corner_length),
            color,
            2,
            cv2.LINE_AA,
        )

        # Top-right
        cv2.line(
            frame,
            (x2, y1),
            (x2 - corner_length, y1),
            color,
            2,
            cv2.LINE_AA,
        )

        cv2.line(
            frame,
            (x2, y1),
            (x2, y1 + corner_length),
            color,
            2,
            cv2.LINE_AA,
        )

        # Bottom-left
        cv2.line(
            frame,
            (x1, y2),
            (x1 + corner_length, y2),
            color,
            2,
            cv2.LINE_AA,
        )

        cv2.line(
            frame,
            (x1, y2),
            (x1, y2 - corner_length),
            color,
            2,
            cv2.LINE_AA,
        )

        # Bottom-right
        cv2.line(
            frame,
            (x2, y2),
            (x2 - corner_length, y2),
            color,
            2,
            cv2.LINE_AA,
        )

        cv2.line(
            frame,
            (x2, y2),
            (x2, y2 - corner_length),
            color,
            2,
            cv2.LINE_AA,
        )

        # Center point
        center_radius = max(
            2,
            int(4 + 3 * pulse),
        )

        cv2.circle(
            frame,
            (center_x, center_y),
            center_radius,
            color,
            -1,
            cv2.LINE_AA,
        )

        return frame

    def reset(self):
        self.active = False
        self.strength = 0.0
        self.anchors.clear()