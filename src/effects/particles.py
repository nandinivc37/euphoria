import math
import random
from dataclasses import dataclass

import cv2
import numpy as np

from effects.anchors import EffectAnchor


@dataclass
class Particle:
    x: float
    y: float

    previous_x: float
    previous_y: float

    vx: float
    vy: float

    life: float
    max_life: float

    radius: int

    color: tuple[int, int, int]


class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []

    def emit_from_anchor(
        self,
        anchor: EffectAnchor,
        count: int = 30,
        color: tuple[int, int, int] = (255, 0, 255),
    ):
        """
        Create particles that originate from an effect anchor.
        """

        for _ in range(count):

            angle = random.uniform(
                0,
                2 * math.pi,
            )

            speed = random.uniform(
                60.0,
                220.0,
            )

            life = random.uniform(
                0.45,
                1.0,
            )

            self.particles.append(
                Particle(
                    x=float(anchor.x),
                    y=float(anchor.y),

                    previous_x=float(anchor.x),
                    previous_y=float(anchor.y),

                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,

                    life=life,
                    max_life=life,

                    radius=random.randint(2, 5),

                    color=color,
                )
            )

    def update(self, dt: float):
        """
        Update particle position and lifetime.

        dt is the time elapsed since the previous frame,
        measured in seconds.
        """

        alive_particles: list[Particle] = []

        for particle in self.particles:

            particle.previous_x = particle.x
            particle.previous_y = particle.y

            # Move using pixels per second.
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt

            # Mild gravity.
            particle.vy += 45.0 * dt

            # Very mild drag.
            particle.vx *= 0.995
            particle.vy *= 0.995

            particle.life -= dt

            if particle.life > 0:
                alive_particles.append(particle)

        self.particles = alive_particles

    def render(self, frame):
        """
        Render particles, motion trails and soft glow.
        """

        if not self.particles:
            return frame

        # Separate transparent layer for glow.
        glow_layer = np.zeros_like(frame)

        for particle in self.particles:

            if particle.life <= 0:
                continue

            life_ratio = max(
                0.0,
                min(
                    1.0,
                    particle.life / particle.max_life,
                ),
            )

            x = int(particle.x)
            y = int(particle.y)

            previous_x = int(particle.previous_x)
            previous_y = int(particle.previous_y)

            # -----------------------------
            # Motion trail
            # -----------------------------

            trail_thickness = max(
                1,
                particle.radius // 2,
            )

            cv2.line(
                frame,
                (previous_x, previous_y),
                (x, y),
                particle.color,
                trail_thickness,
            )

            # -----------------------------
            # Particle
            # -----------------------------

            brightness = int(
                255 * life_ratio
            )

            scaled_color = tuple(
                int(channel * life_ratio)
                for channel in particle.color
            )

            cv2.circle(
                frame,
                (x, y),
                particle.radius,
                scaled_color,
                -1,
            )

            # -----------------------------
            # Glow source
            # -----------------------------

            glow_radius = max(
                8,
                particle.radius * 4,
            )

            cv2.circle(
                glow_layer,
                (x, y),
                glow_radius,
                tuple(
                    int(channel * 0.8 * life_ratio)
                    for channel in particle.color
                ),
                -1,
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

        # Add glow to frame.
        frame = cv2.addWeighted(
            frame,
            1.0,
            glow_layer,
            0.65,
            0,
        )

        return frame

    def clear(self):
        self.particles.clear()