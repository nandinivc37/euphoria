from gestures.definitions import Gesture
from gestures.events import GestureEvent

from effects.particles import ParticleSystem


class EffectsEngine:
    def __init__(self):
        self.particles = ParticleSystem()
        self.active_gesture = Gesture.UNKNOWN

    def handle_event(self, event: GestureEvent):
        self.active_gesture = event.gesture

        if event.gesture == Gesture.PEACE:
            self.particles.emit(
                event.x,
                event.y,
                count=60,
            )

        elif event.gesture == Gesture.OPEN_PALM:
            self.particles.emit(
                event.x,
                event.y,
                count=100,
            )

        elif event.gesture == Gesture.FIST:
            self.particles.clear()

    def update(self, dt: float):
        self.particles.update(dt)

    def render(self, frame):
        return self.particles.render(frame)

    def reset(self):
        self.particles.clear()
        self.active_gesture = Gesture.UNKNOWN
