import math

import cv2
import numpy as np

from effects.anchors import EffectAnchor


class BeamSystem:
    """
    Manages continuous fingertip beams.

    The beam follows the current fingertip position
    every frame and smoothly fades in/out.
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

        # Smooth fade.
        target_strength = 1.0 if active else 0.0

        fade_speed = 6.0

        self.strength += (
            target_strength - self.strength
        ) * min(1.0, fade_speed * dt)

    def _endpoint(
        self,
        fingertip: EffectAnchor,
        palm: EffectAnchor,
        length: float,
    ) -> tuple[int, int]:

        dx = fingertip.x - palm.x
        dy = fingertip.y - palm.y

        magnitude = math.sqrt(
            dx * dx + dy * dy
        )

        if magnitude < 1e-6:
            return fingertip.x, fingertip.y

        direction_x = dx / magnitude
        direction_y = dy / magnitude

        return (
            int(fingertip.x + direction_x * length),
            int(fingertip.y + direction_y * length),
        )

    def render(self, frame):
        if self.strength <= 0.01:
            return frame

        required = (
            "index_tip",
            "middle_tip",
            "palm_center",
        )

        if not all(
            name in self.anchors
            for name in required
        ):
            return frame

        pulse = (
            0.5
            + 0.5
            * math.sin(self.time * 5.0)
        )

        beam_length = 150 + int(
            50 * pulse
        )

        # Purple / magenta in BGR.
        color = (255, 0, 255)

        glow_layer = np.zeros_like(frame)

        beam_points = []

        for name in (
            "index_tip",
            "middle_tip",
        ):
            fingertip = self.anchors[name]
            palm = self.anchors["palm_center"]

            start = (
                fingertip.x,
                fingertip.y,
            )

            end = self._endpoint(
                fingertip,
                palm,
                beam_length,
            )

            beam_points.append(
                (start, end)
            )

        # --------------------------------
        # Create broad glow
        # --------------------------------

        glow_strength = self.strength * (
            0.7 + 0.3 * pulse
        )

        for start, end in beam_points:

            cv2.line(
                glow_layer,
                start,
                end,
                tuple(
                    int(channel * glow_strength)
                    for channel in color
                ),
                18,
                cv2.LINE_AA,
            )

        glow_layer = cv2.GaussianBlur(
            glow_layer,
            (0, 0),
            sigmaX=12,
            sigmaY=12,
        )

        frame = cv2.addWeighted(
            frame,
            1.0,
            glow_layer,
            0.8 * self.strength,
            0,
        )

        # --------------------------------
        # Draw bright beam core
        # --------------------------------

        core_color = tuple(
            int(channel * self.strength)
            for channel in color
        )

        core_thickness = max(
            2,
            int(4 * self.strength),
        )

        for start, end in beam_points:

            cv2.line(
                frame,
                start,
                end,
                core_color,
                core_thickness,
                cv2.LINE_AA,
            )

            # Bright point at the origin.
            cv2.circle(
                frame,
                start,
                max(
                    3,
                    int(6 * self.strength),
                ),
                core_color,
                -1,
                cv2.LINE_AA,
            )

        return frame

    def reset(self):
        self.active = False
        self.strength = 0.0
        self.anchors.clear()