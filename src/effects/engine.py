from gestures.definitions import Gesture
from gestures.events import GestureEvent

from effects.anchors import EffectAnchor
from effects.beams import BeamSystem
from effects.focus import FocusSystem
from effects.particles import ParticleSystem
from effects.atmosphere import AtmosphereSystem
from effects.environment import EnvironmentSystem


class EffectsEngine:
    def __init__(
        self,
        world_width: int,
        world_height: int,
    ):
        self.particles = ParticleSystem()
        self.beams = BeamSystem()
        self.focus = FocusSystem()
        self.atmosphere = AtmosphereSystem()
        self.environment = EnvironmentSystem()

        # --------------------------------
        # Portal target
        # --------------------------------

        portal_x = world_width // 2
        portal_y = int(world_height * 0.56)

        self.portal_target = EffectAnchor(
            name="portal",
            x=portal_x,
            y=portal_y,
        )

        # --------------------------------
        # TWO gesture targets
        # --------------------------------

        target_offset = int(
            world_width * 0.055
        )

        self.two_left_target = (
            EffectAnchor(
                name="two_left_portal",
                x=portal_x - target_offset,
                y=portal_y,
            )
        )

        self.two_right_target = (
            EffectAnchor(
                name="two_right_portal",
                x=portal_x + target_offset,
                y=portal_y,
            )
        )

        self.active_gesture = (
            Gesture.UNKNOWN
        )

        # --------------------------------
        # Continuous emission timers
        # --------------------------------

        self.one_emit_timer = 0.0
        self.two_emit_timer = 0.0

    # --------------------------------
    # Particle helper
    # --------------------------------

    def _emit(
        self,
        anchor: EffectAnchor,
        count: int,
        color: tuple[int, int, int],
        target: EffectAnchor | None = None,
        target_strength: float = 0.0,
    ):
        self.particles.emit_from_anchor(
            anchor,
            count=count,
            color=color,
            target=target,
            target_strength=target_strength,
        )

    # --------------------------------
    # One-time gesture events
    # --------------------------------

    def handle_event(
        self,
        event: GestureEvent,
    ):
        self.active_gesture = (
            event.gesture
        )

        anchors = event.anchors

        # --------------------------------
        # ONE
        # --------------------------------

        if event.gesture == Gesture.ONE:

            # Small initial burst.
            self._emit(
                anchors["index_tip"],
                count=12,
                color=(255, 120, 0),
                target=self.portal_target,
                target_strength=520.0,
            )

        # --------------------------------
        # TWO
        # --------------------------------

        elif event.gesture == Gesture.TWO:

            # Initial burst from index finger
            # toward left side of portal.
            self._emit(
                anchors["index_tip"],
                count=8,
                color=(255, 0, 255),
                target=self.two_left_target,
                target_strength=500.0,
            )

            # Initial burst from middle finger
            # toward right side of portal.
            self._emit(
                anchors["middle_tip"],
                count=8,
                color=(255, 0, 255),
                target=self.two_right_target,
                target_strength=500.0,
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
        # --------------------------------
        # Environment
        # --------------------------------

        self.environment.update(dt)

        # --------------------------------
        # Particles
        # --------------------------------

        self.particles.update(dt)

        # --------------------------------
        # Continuous ONE stream
        # --------------------------------

        if (
            gesture == Gesture.ONE
            and "index_tip" in world_anchors
        ):
            self.one_emit_timer += dt

            emission_interval = 0.07

            while (
                self.one_emit_timer
                >= emission_interval
            ):
                self.one_emit_timer -= (
                    emission_interval
                )

                self._emit(
                    world_anchors[
                        "index_tip"
                    ],
                    count=2,
                    color=(255, 120, 0),
                    target=self.portal_target,
                    target_strength=520.0,
                )

        else:
            self.one_emit_timer = 0.0

        # --------------------------------
        # Continuous TWO streams
        # --------------------------------

        if (
            gesture == Gesture.TWO
            and
            "index_tip" in world_anchors
            and
            "middle_tip" in world_anchors
        ):
            self.two_emit_timer += dt

            emission_interval = 0.09

            while (
                self.two_emit_timer
                >= emission_interval
            ):
                self.two_emit_timer -= (
                    emission_interval
                )

                # Index → left portal target
                self._emit(
                    world_anchors[
                        "index_tip"
                    ],
                    count=1,
                    color=(255, 0, 255),
                    target=self.two_left_target,
                    target_strength=500.0,
                )

                # Middle → right portal target
                self._emit(
                    world_anchors[
                        "middle_tip"
                    ],
                    count=1,
                    color=(255, 0, 255),
                    target=self.two_right_target,
                    target_strength=500.0,
                )

        else:
            self.two_emit_timer = 0.0

        # --------------------------------
        # Beams disabled
        # --------------------------------

        self.beams.update(
            dt,
            active=False,
            anchors={},
        )

        # --------------------------------
        # Camera web
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

        frame = self.environment.render(
            frame
        )

        frame = self.atmosphere.render(
            frame
        )

        frame = self.particles.render(
            frame
        )

        return frame

    # --------------------------------
    # Render CAMERA
    # --------------------------------

    def render_camera(self, frame):

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

        self.active_gesture = (
            Gesture.UNKNOWN
        )

        self.one_emit_timer = 0.0
        self.two_emit_timer = 0.0