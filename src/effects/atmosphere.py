import math

import cv2
import numpy as np

from effects.anchors import EffectAnchor


class AtmosphereSystem:
    """
    Lightweight ambient glow layer.

    The glow is rendered at reduced resolution to keep
    the real-time pipeline responsive.
    """

    def __init__(self):
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

        if active:
            self.anchors = anchors

        target_strength = 1.0 if active else 0.0

        fade_speed = 3.5

        self.strength += (
            target_strength - self.strength
        ) * min(1.0, fade_speed * dt)

    def render(self, frame):
        if self.strength <= 0.01:
            return frame

        if "palm_center" in self.anchors:
            anchor = self.anchors["palm_center"]
        elif "wrist" in self.anchors:
            anchor = self.anchors["wrist"]
        else:
            return frame

        height, width = frame.shape[:2]

        # Render glow at 1/4 resolution.
        scale = 4

        small_width = max(1, width // scale)
        small_height = max(1, height // scale)

        glow_layer = np.zeros(
            (small_height, small_width, 3),
            dtype=np.uint8,
        )

        center_x = int(anchor.x / scale)
        center_y = int(anchor.y / scale)

        pulse = (
            0.5
            + 0.5 * math.sin(self.time * 2.0)
        )

        radius = int(
            35 + 12 * pulse
        )

        glow_color = (160, 40, 220)

        cv2.circle(
            glow_layer,
            (center_x, center_y),
            radius,
            glow_color,
            -1,
            cv2.LINE_AA,
        )

        # Much cheaper because the image is 1/16
        # the number of pixels.
        glow_layer = cv2.GaussianBlur(
            glow_layer,
            (0, 0),
            sigmaX=12,
            sigmaY=12,
        )

        # Scale back to camera resolution.
        glow_layer = cv2.resize(
            glow_layer,
            (width, height),
            interpolation=cv2.INTER_LINEAR,
        )

        frame = cv2.addWeighted(
            frame,
            1.0,
            glow_layer,
            0.16 * self.strength,
            0,
        )

        return frame

    def reset(self):
        self.strength = 0.0
        self.time = 0.0
        self.anchors.clear()