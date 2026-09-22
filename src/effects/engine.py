from gestures.definitions import Gesture
from gestures.events import GestureEvent

from effects.anchors import EffectAnchor
from effects.particles import ParticleSystem


class EffectsEngine:
    def __init__(self):
        self.particles = ParticleSystem()
        self.active_gesture = Gesture.UNKNOWN

    def _emit(self, anchor: EffectAnchor, count: int):
        self.particles.emit_from_anchor(
            anchor,
            count=count,
        )

    def handle_event(self, event: GestureEvent):
        self.active_gesture = event.gesture

        anchors = event.anchors

        # -----------------------------
        # ONE
        # Index fingertip
        # -----------------------------
        if event.gesture == Gesture.ONE:

            self._emit(
                anchors["index_tip"],
                count=30,
            )

        # -----------------------------
        # TWO
        # Index + middle fingertips
        # -----------------------------
        elif event.gesture == Gesture.TWO:

            self._emit(
                anchors["index_tip"],
                count=30,
            )

            self._emit(
                anchors["middle_tip"],
                count=30,
            )

        # -----------------------------
        # THREE
        # Index + middle + ring
        # -----------------------------
        elif event.gesture == Gesture.THREE:

            self._emit(
                anchors["index_tip"],
                count=25,
            )

            self._emit(
                anchors["middle_tip"],
                count=25,
            )

            self._emit(
                anchors["ring_tip"],
                count=25,
            )

        # -----------------------------
        # FOUR
        # Four fingertips
        # -----------------------------
        elif event.gesture == Gesture.FOUR:

            for name in (
                "index_tip",
                "middle_tip",
                "ring_tip",
                "pinky_tip",
            ):
                self._emit(
                    anchors[name],
                    count=20,
                )

        # -----------------------------
        # FIVE
        # Palm + all fingertips
        # -----------------------------
        elif event.gesture == Gesture.FIVE:

            self._emit(
                anchors["palm_center"],
                count=60,
            )

            for name in (
                "thumb_tip",
                "index_tip",
                "middle_tip",
                "ring_tip",
                "pinky_tip",
            ):
                self._emit(
                    anchors[name],
                    count=15,
                )

        # -----------------------------
        # FIST
        # Clear all effects
        # -----------------------------
        elif event.gesture == Gesture.FIST:

            self.particles.clear()

    def update(self, dt: float):
        self.particles.update(dt)

    def render(self, frame):
        return self.particles.render(frame)

    def reset(self):
        self.particles.clear()
        self.active_gesture = Gesture.UNKNOWN