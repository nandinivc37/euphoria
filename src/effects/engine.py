from gestures.definitions import Gesture
from gestures.events import GestureEvent

from effects.anchors import EffectAnchor
from effects.beams import BeamSystem
from effects.focus import FocusSystem
from effects.particles import ParticleSystem
from effects.atmosphere import AtmosphereSystem
from effects.environment import EnvironmentSystem
from effects.rain import RainSystem
from effects.central_light import CentralLightSystem
from effects.pillar_lights import PillarLightSystem


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

        #--------------------------------
        # Rain System
        #--------------------------------
        self.rain = RainSystem(
            world_width=world_width,
            world_height=world_height,
        )

        #-------------------------------
        # Central Light System
        #-------------------------------
        self.central_light = CentralLightSystem(
            world_width=world_width,
            world_height=world_height,
        )

        #-------------------------------
        # Pillar Light System
        #-------------------------------
        self.pillar_lights = PillarLightSystem(
            world_width=world_width,
            world_height=world_height,
        )

        self.active_gesture = Gesture.UNKNOWN

    
    
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
        # THREE
        # --------------------------------

        if event.gesture == Gesture.THREE:

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

        # # --------------------------------
        # # FIVE
        # # --------------------------------

        # elif event.gesture == Gesture.FIVE:

        #     self._emit(
        #         anchors["palm_center"],
        #         count=70,
        #         color=(0, 220, 255),
        #     )

        #     for name in (
        #         "thumb_tip",
        #         "index_tip",
        #         "middle_tip",
        #         "ring_tip",
        #         "pinky_tip",
        #     ):
        #         self._emit(
        #             anchors[name],
        #             count=20,
        #             color=(0, 220, 255),
        #         )

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
        active_camera_hands: list [
            dict[str, EffectAnchor],
        ],
        right_palm_open: bool,
        pinch_trigger: bool,
    ):
        # --------------------------------
        # Environment
        # --------------------------------

        self.environment.update(dt)

        # --------------------------------
        # Rain
        # --------------------------------
        self.rain.update(
            dt,
            active=right_palm_open,
        )

        # --------------------------------
        # Central Light
        # --------------------------------

        self.central_light.update(
            dt,
            pinch_trigger=pinch_trigger,
        )

        # --------------------------------
        # Pillar Lights
        # --------------------------------

        palm = world_anchors.get("palm_center")

        pillar_active = (
            gesture in (
                Gesture.FIVE,
                Gesture.FOCUS,
            )
        )

        self.pillar_lights.update(
            dt,
            active=pillar_active,
            palm_x=palm.x if palm else None,
            palm_y=palm.y if palm else None,
        )

        # --------------------------------
        # Particles
        # --------------------------------

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
        # Camera web
        # --------------------------------

        # focus_active = (
        #     gesture in (
        #         Gesture.FOCUS,
        #         Gesture.FIVE,
        #     )
        #     and len(camera_anchors) > 0
        # )

        self.focus.update(
            dt,
            #active=focus_active,
            active_hand_anchors=active_camera_hands,
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

        frame = self.rain.render(
            frame
        )

        frame = self.central_light.render(
            frame
        )

        frame = self.pillar_lights.render(
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
        self.rain.reset()
        self.central_light.reset()
        self.pillar_lights.reset()

        self.active_gesture = (
            Gesture.UNKNOWN
        )

