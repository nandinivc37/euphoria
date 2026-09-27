import math

import cv2
import numpy as np


class CentralLightSystem:
    def __init__(
        self,
        world_width: int,
        world_height: int,
    ):
        self.width = world_width
        self.height = world_height

        # Main focal point / altar area
        self.x = int(world_width * 0.50)
        self.y = int(world_height * 0.47)

        self.flash = 0.0
        self.cooldown = 0.0

    def update(
        self,
        dt: float,
        pinch_trigger: bool,
    ):
        if pinch_trigger and self.cooldown <= 0.0:
            self.flash = 1.0
            self.cooldown = 0.10

        self.cooldown = max(
            0.0,
            self.cooldown - dt,
        )

        # Fast blink / fade
        self.flash *= math.exp(-11.0 * dt)

    def render(self, frame):
        if self.flash <= 0.01:
            return frame

        glow = np.zeros_like(frame)

        # Large soft glow
        radius = int(
            18 + 55 * self.flash
        )

        cv2.circle(
            glow,
            (self.x, self.y),
            radius,
            (255, 225, 190),
            -1,
            cv2.LINE_AA,
        )

        glow = cv2.GaussianBlur(
            glow,
            (0, 0),
            18,
        )

        frame = cv2.addWeighted(
            frame,
            1.0,
            glow,
            0.55 * self.flash,
            0,
        )

        # Bright central core
        core = np.zeros_like(frame)

        core_radius = int(
            3 + 9 * self.flash
        )

        cv2.circle(
            core,
            (self.x, self.y),
            core_radius,
            (255, 245, 225),
            -1,
            cv2.LINE_AA,
        )

        frame = cv2.addWeighted(
            frame,
            1.0,
            core,
            0.9 * self.flash,
            0,
        )

        return frame

    def reset(self):
        self.flash = 0.0
        self.cooldown = 0.0