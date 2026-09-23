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

    target_x: float | None = None
    target_y: float | None = None
    target_strength: float = 0.0


class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []

        # Safety limit so continuous effects
        # never create an excessive number
        # of particles.
        self.max_particles = 250

    def emit_from_anchor(
        self,
        anchor: EffectAnchor,
        count: int = 30,
        color: tuple[int, int, int] = (255, 0, 255),
        target: EffectAnchor | None = None,
        target_strength: float = 0.0,
    ):
        """
        Create particles from an anchor.

        When a target is provided, particles start with
        a velocity biased toward that target and continue
        receiving attraction while alive.
        """

        if len(self.particles) >= self.max_particles:
            return

        count = min(
            count,
            self.max_particles
            - len(self.particles),
        )

        for _ in range(count):

            # ---------------------------------
            # Default random motion
            # ---------------------------------

            angle = random.uniform(
                0,
                2 * math.pi,
            )

            speed = random.uniform(
                60.0,
                160.0,
            )

            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            target_x = None
            target_y = None

            # ---------------------------------
            # Portal-directed motion
            # ---------------------------------

            if target is not None:

                target_x = float(target.x)
                target_y = float(target.y)

                dx = (
                    target_x
                    - anchor.x
                )

                dy = (
                    target_y
                    - anchor.y
                )

                distance = math.hypot(
                    dx,
                    dy,
                )

                if distance > 1.0:

                    direction_x = (
                        dx / distance
                    )

                    direction_y = (
                        dy / distance
                    )

                    # Strong forward movement toward
                    # the portal.
                    travel_speed = random.uniform(
                        80.0,
                        150.0,
                    )

                    # Small sideways randomness keeps
                    # the stream organic.
                    sideways = random.uniform(
                        -45.0,
                        45.0,
                    )

                    vx = (
                        direction_x
                        * travel_speed
                        + -direction_y
                        * sideways
                    )

                    vy = (
                        direction_y
                        * travel_speed
                        + direction_x
                        * sideways
                    )

            # ---------------------------------
            # Particle lifetime
            # ---------------------------------

            if target is not None:
                life = random.uniform(
                    0.9,
                    1.7,
                )
            else:
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

                    vx=vx,
                    vy=vy,

                    life=life,
                    max_life=life,

                    radius=random.randint(
                        2,
                        4,
                    ),

                    color=color,

                    target_x=target_x,
                    target_y=target_y,
                    target_strength=target_strength,
                )
            )

    def update(self, dt: float):
        """
        Update particle position and lifetime.

        Targeted particles disappear once they reach
        the portal instead of flying through it.
        """

        alive_particles: list[Particle] = []

        for particle in self.particles:

            particle.previous_x = particle.x
            particle.previous_y = particle.y

            # ---------------------------------
            # Attraction toward target
            # ---------------------------------

            reached_target = False

            if (
                particle.target_x is not None
                and particle.target_y is not None
            ):
                dx = (
                    particle.target_x
                    - particle.x
                )

                dy = (
                    particle.target_y
                    - particle.y
                )

                distance = math.hypot(
                    dx,
                    dy,
                )

                # Absorb particle near portal.
                if distance <= 18.0:
                    reached_target = True

                elif distance > 3.0:

                    direction_x = dx / distance
                    direction_y = dy / distance

                    particle.vx += (
                        direction_x
                        * particle.target_strength
                        * dt
                    )

                    particle.vy += (
                        direction_y
                        * particle.target_strength
                        * dt
                    )

            if reached_target:
                continue

            # ---------------------------------
            # Move
            # ---------------------------------

            particle.x += particle.vx * dt
            particle.y += particle.vy * dt

            # ---------------------------------
            # Very mild gravity
            # ---------------------------------

            particle.vy += 15.0 * dt

            # ---------------------------------
            # Mild drag
            # ---------------------------------

            particle.vx *= 0.997
            particle.vy *= 0.997

            # ---------------------------------
            # Lifetime
            # ---------------------------------

            particle.life -= dt

            if particle.life > 0:
                alive_particles.append(particle)

        self.particles = alive_particles

            

    def render(self, frame):
        """
        Render particles, motion trails and glow.
        """

        if not self.particles:
            return frame

        glow_layer = np.zeros_like(
            frame
        )

        for particle in self.particles:

            if particle.life <= 0:
                continue

            life_ratio = max(
                0.0,
                min(
                    1.0,
                    particle.life
                    / particle.max_life,
                ),
            )

            x = int(
                particle.x
            )

            y = int(
                particle.y
            )

            previous_x = int(
                particle.previous_x
            )

            previous_y = int(
                particle.previous_y
            )

            # ---------------------------------
            # Motion trail
            # ---------------------------------

            trail_thickness = max(
                1,
                particle.radius // 2,
            )

            cv2.line(
                frame,
                (
                    previous_x,
                    previous_y,
                ),
                (
                    x,
                    y,
                ),
                particle.color,
                trail_thickness,
                cv2.LINE_AA,
            )

            # ---------------------------------
            # Particle
            # ---------------------------------

            scaled_color = tuple(
                int(
                    channel
                    * life_ratio
                )
                for channel
                in particle.color
            )

            cv2.circle(
                frame,
                (
                    x,
                    y,
                ),
                particle.radius,
                scaled_color,
                -1,
                cv2.LINE_AA,
            )

            # ---------------------------------
            # Glow
            # ---------------------------------

            glow_radius = max(
                7,
                particle.radius * 4,
            )

            cv2.circle(
                glow_layer,
                (
                    x,
                    y,
                ),
                glow_radius,
                tuple(
                    int(
                        channel
                        * 0.75
                        * life_ratio
                    )
                    for channel
                    in particle.color
                ),
                -1,
            )

        # ---------------------------------
        # Blur glow once
        # ---------------------------------

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
            0.65,
            0,
        )

        return frame

    def clear(self):
        self.particles.clear()