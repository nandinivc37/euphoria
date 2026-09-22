from gestures.definitions import Gesture
from gestures.events import GestureEvent

from effects.anchors import EffectAnchor
from effects.beams import BeamSystem
from effects.focus import FocusSystem
from effects.particles import ParticleSystem


class EffectsEngine:
    def __init__(self):
        self.particles = ParticleSystem()
        self.beams = BeamSystem()
        self.focus = FocusSystem()

        self.active_gesture = Gesture.UNKNOWN

    # --------------------------------
    # Particle helper
    # --------------------------------

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

    # --------------------------------
    # One-time gesture events
    # --------------------------------

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

            for name in (
                "index_tip",
                "middle_tip",
                "ring_tip",
            ):
                self._emit(
                    anchors[name],
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

            self._emit(
                anchors["palm_center"],
                count=70,
                color=(0, 220, 255),
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
                    count=20,
                    color=(0, 220, 255),
                )

        # --------------------------------
        # FOCUS
        # L-shape
        # --------------------------------

        elif event.gesture == Gesture.FOCUS:

            self._emit(
                anchors["thumb_tip"],
                count=35,
                color=(0, 255, 255),
            )

            self._emit(
                anchors["index_tip"],
                count=35,
                color=(0, 255, 255),
            )

    # --------------------------------
    # Continuous effects
    # --------------------------------

    def update(
        self,
        dt: float,
        gesture: Gesture,
        anchors: dict[str, EffectAnchor],
    ):
        # Existing particles.
        self.particles.update(dt)

        # TWO → continuous beams.
        beam_active = (
            gesture == Gesture.TWO
            and "index_tip" in anchors
            and "middle_tip" in anchors
            and "palm_center" in anchors
        )

        self.beams.update(
            dt,
            active=beam_active,
            anchors=anchors,
        )

        # FOCUS → continuous reticle.
        focus_active = (
            gesture in (
                Gesture.FOCUS,
                Gesture.FIVE,
            )
            and all(
                name in anchors
                for name in (
                    "thumb_tip",
                    "index_tip",
                    "middle_tip",
                    "ring_tip",
                    "pinky_tip",
                )
            )
        )

        self.focus.update(
            dt,
            active=focus_active,
            anchors=anchors,
        )

    # --------------------------------
    # Render
    # --------------------------------

    def render(self, frame):

        # Continuous beams.
        frame = self.beams.render(frame)

        # Focus reticle.
        frame = self.focus.render(frame)

        # Particles on top.
        frame = self.particles.render(frame)

        return frame

    # --------------------------------
    # Reset
    # --------------------------------

    def reset(self):
        self.particles.clear()
        self.beams.reset()
        self.focus.reset()

        self.active_gesture = Gesture.UNKNOWN