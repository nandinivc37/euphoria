import math
import random
from dataclasses import dataclass

import cv2

from effects.anchors import EffectAnchor


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    radius: int


class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []

    def emit_from_anchor(
        self,
        anchor: EffectAnchor,
        count: int = 30,
    ):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 4.5)

            self.particles.append(
                Particle(
                    x=anchor.x,
                    y=anchor.y,
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                    life=random.uniform(0.5, 1.0),
                    radius=random.randint(2, 5),
                )
            )

    def update(self, dt: float):
        alive_particles = []

        for particle in self.particles:
            particle.x += particle.vx
            particle.y += particle.vy

            particle.vy += 20 * dt
            particle.life -= dt

            if particle.life > 0:
                alive_particles.append(particle)

        self.particles = alive_particles

    def render(self, frame):
        for particle in self.particles:
            if particle.life <= 0:
                continue

            alpha = max(0.0, min(1.0, particle.life))
            brightness = int(255 * alpha)

            cv2.circle(
                frame,
                (int(particle.x), int(particle.y)),
                particle.radius,
                (brightness, 0, brightness),
                -1,
            )

        return frame

    def clear(self):
        self.particles.clear()
