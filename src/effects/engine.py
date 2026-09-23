from gestures.definitions import Gesture
from gestures.events import GestureEvent

from effects.anchors import EffectAnchor
from effects.beams import BeamSystem
from effects.focus import FocusSystem
from effects.particles import ParticleSystem
from effects.atmosphere import AtmosphereSystem
from effects.environment import EnvironmentSystem


class EffectsEngine:
    def __init__(self):
        self.particles = ParticleSystem()
        self.beams = BeamSystem()
        self.focus = FocusSystem()
        self.atmosphere = AtmosphereSystem()
        self.environment = EnvironmentSystem()

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

            # No beams.
            # Only particles in the world.

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
        world_anchors: dict[str, EffectAnchor],
        camera_anchors: dict[str, EffectAnchor],
    ):
        # Environment
        self.environment.update(dt)

        # Particles live in world
        self.particles.update(dt)

        # --------------------------------
        # Beams disabled
        # --------------------------------

        self.beams.update(
            dt,
            active=False,
            anchors={},
        )

        # --------------------------------
        # Focus web lives in camera
        # --------------------------------

        focus_active = (
            gesture in (
                Gesture.FOCUS,
                Gesture.FIVE,
            )
            and all(
                name in camera_anchors
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
            anchors=camera_anchors,
        )

        # --------------------------------
        # Atmosphere
        # --------------------------------

        atmosphere_active = (
            gesture != Gesture.UNKNOWN
        )

        self.atmosphere.update(
            dt,
            active=atmosphere_active,
            anchors=world_anchors,
        )

    # --------------------------------
    # Render WORLD
    # --------------------------------

    def render_world(self, frame):

        # 1. Architecture
        frame = self.environment.render(
            frame
        )

        # 2. Atmosphere
        frame = self.atmosphere.render(
            frame
        )

        # 3. Particles
        frame = self.particles.render(
            frame
        )

        return frame

    # --------------------------------
    # Render CAMERA
    # --------------------------------

    def render_camera(self, frame):
        # Only the hand web belongs here.
        frame = self.focus.render(
            frame
        )

        return frame

    # --------------------------------
    # Reset
    # --------------------------------

    def reset(self):
        self.particles.clear()
        self.beams.reset()
        self.focus.reset()
        self.atmosphere.reset()
        self.environment.reset()

        self.active_gesture = Gesture.UNKNOWN