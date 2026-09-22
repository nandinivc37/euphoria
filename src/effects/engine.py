from gestures.definitions import Gesture
from gestures.events import GestureEvent

from effects.anchors import EffectAnchor
from effects.particles import ParticleSystem


class EffectsEngine:
    def __init__(self):
        self.particles = ParticleSystem()
        self.active_gesture = Gesture.UNKNOWN

    def _emit(
        self,
        anchor: EffectAnchor,
        count: int,
        color: tuple[int, int, int],
    ):
        self.particles.emit_from_anchor(
            anchor,
            count=count,
            color=color,
        )

    def handle_event(
        self,
        event: GestureEvent,
    ):
        self.active_gesture = event.gesture

        anchors = event.anchors

        # --------------------------------
        # ONE
        # --------------------------------

        if event.gesture == Gesture.ONE:

            self._emit(
                anchors["index_tip"],
                count=45,
                color=(255, 120, 0),
            )

        # --------------------------------
        # TWO
        # --------------------------------

        elif event.gesture == Gesture.TWO:

            self._emit(
                anchors["index_tip"],
                count=40,
                color=(255, 0, 255),
            )

            self._emit(
                anchors["middle_tip"],
                count=40,
                color=(255, 0, 255),
            )

        # --------------------------------
        # THREE
        # --------------------------------

        elif event.gesture == Gesture.THREE:

            self._emit(
                anchors["index_tip"],
                count=30,
                color=(255, 120, 0),
            )

            self._emit(
                anchors["middle_tip"],
                count=30,
                color=(255, 120, 0),
            )

            self._emit(
                anchors["ring_tip"],
                count=30,
                color=(255, 120, 0),
            )

        # --------------------------------
        # FOUR
        # --------------------------------

        elif event.gesture == Gesture.FOUR:

            for name in (
                "index_tip",
                "middle_tip",
                "ring_tip",
                "pinky_tip",
            ):
                self._emit(
                    anchors[name],
                    count=25,
                    color=(0, 220, 255),
                )

        # --------------------------------
        # FIVE
        # --------------------------------

        elif event.gesture == Gesture.FIVE:

            # Central palm burst
            self._emit(
                anchors["palm_center"],
                count=70,
                color=(0, 220, 255),
            )

            # Five fingertip emitters
            for name in (
                "thumb_tip",
                "index_tip",
                "middle_tip",
                "ring_tip",
                "pinky_tip",
            ):
                self._emit(
                    anchors[name],
                    count=20,
                    color=(0, 220, 255),
                )

        # --------------------------------
        # FIST
        # --------------------------------

        elif event.gesture == Gesture.FIST:

            self.particles.clear()

    def update(self, dt: float):
        self.particles.update(dt)

    def render(self, frame):
        return self.particles.render(frame)

    def reset(self):
        self.particles.clear()
        self.active_gesture = Gesture.UNKNOWN