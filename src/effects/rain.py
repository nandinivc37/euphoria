import random
import math

import cv2
import numpy as np


class RainSystem:
    def __init__(
        self,
        world_width: int,
        world_height: int,
    ):
        self.width = world_width
        self.height = world_height

        self.drops: list[dict] = []

        # Central cathedral region
        self.center_x = self.width // 2
        self.spawn_width = int(self.width * 0.24)

        # Rain falls through the middle of the cathedral
        self.spawn_top = int(self.height * 0.08)
        self.fall_bottom = int(self.height * 0.82)

        self.active = False
        self.strength = 0.0

    def _spawn_drop(self):
        x = self.center_x + random.randint(
            -self.spawn_width // 2,
            self.spawn_width // 2,
        )

        y = random.randint(
            self.spawn_top,
            int(self.height * 0.28),
        )

        speed = random.uniform(
            self.height * 0.55,
            self.height * 0.95,
        )

        length = random.randint(8, 18)

        self.drops.append(
            {
                "x": float(x),
                "y": float(y),
                "speed": speed,
                "length": length,
                "alpha": random.uniform(0.45, 0.9),
                "phase": random.uniform(0.0, math.pi * 2.0),
            }
        )

    def update(
        self,
        dt: float,
        active: bool,
    ):
        self.active = active

        target_strength = 1.0 if active else 0.0

        fade_speed = 5.0
        self.strength += (
            target_strength - self.strength
        ) * min(1.0, fade_speed * dt)

        # Spawn while the right palm is open
        if self.strength > 0.05:
            spawn_count = int(
                34 * self.strength * dt
            )

            # Keep the effect smooth even at high FPS
            if random.random() < (
                (34 * self.strength * dt) % 1.0
            ):
                spawn_count += 1

            for _ in range(spawn_count):
                self._spawn_drop()

        # Move droplets
        alive = []

        for drop in self.drops:
            drop["y"] += drop["speed"] * dt

            if drop["y"] < self.fall_bottom:
                alive.append(drop)

        self.drops = alive

        # Hard cap for safety
        if len(self.drops) > 260:
            self.drops = self.drops[-260:]

    def render(self, frame):
        if self.strength <= 0.01:
            return frame

        overlay = np.zeros_like(frame)

        for drop in self.drops:
            x = int(drop["x"])
            y = int(drop["y"])

            length = drop["length"]

            # Slight sideways shimmer
            shimmer = math.sin(
                drop["phase"] + y * 0.015
            )

            x2 = x + int(shimmer * 1.2)
            y2 = y + length

            alpha = drop["alpha"] * self.strength

            cv2.line(
                overlay,
                (x, y),
                (x2, y2),
                (175, 210, 255),
                1,
                cv2.LINE_AA,
            )

        # Soft glow around the rain
        glow = cv2.GaussianBlur(
            overlay,
            (0, 0),
            2.0,
        )

        frame = cv2.addWeighted(
            frame,
            1.0,
            glow,
            0.35 * self.strength,
            0,
        )

        frame = cv2.addWeighted(
            frame,
            1.0,
            overlay,
            0.75 * self.strength,
            0,
        )

        return frame

    def reset(self):
        self.drops.clear()
        self.active = False
        self.strength = 0.0