import math

import cv2
import numpy as np


class PillarLightSystem:
    def __init__(
        self,
        world_width: int,
        world_height: int,
    ):
        self.width = world_width
        self.height = world_height

        # Approximate pillar positions in the cathedral image.
        self.pillar_x = [
            0.10,
            0.22,
            0.33,
            0.67,
            0.78,
            0.90,
        ]

        self.y_top = 0.20
        self.y_bottom = 0.80

        # Persistent activated points.
        self.lit_points: list[list[float]] = [
            [] for _ in self.pillar_x
        ]

        # Currently controlled light.
        self.current_pillar = None
        self.current_y = None

        self.capture_timer = 0.0
        self.capture_interval = 0.18
        self.max_total_points = 24

        # ------------------------------------------------
        # Color state
        # ------------------------------------------------

        # Open-palm starting color.
        self.color_palette = [
            (255, 240, 220),  # warm white
            (255, 255, 0),    # cyan
            (220, 120, 255),  # violet
            (120, 210, 255),  # warm gold
        ]

        self.color_index = 0

        # ------------------------------------------------
        # Rotation state
        # ------------------------------------------------

        self.rotation_reference_angle = None
        self.last_rotation_step = 0

    # ----------------------------------------------------
    # Helpers
    # ----------------------------------------------------

    @staticmethod
    def _angle_difference(
        current: float,
        reference: float,
    ) -> float:
        """
        Returns signed angular difference in degrees
        in the range [-180, 180].
        """
        difference = current - reference

        while difference > 180.0:
            difference -= 360.0

        while difference < -180.0:
            difference += 360.0

        return difference

    # ----------------------------------------------------
    # Update
    # ----------------------------------------------------

    def update(
        self,
        dt: float,
        active: bool,
        palm_x: float | None,
        palm_y: float | None,
        palm_angle: float | None,
    ):
        self.current_pillar = None
        self.current_y = None

        # Right hand is not controlling pillars.
        # IMPORTANT:
        # Do NOT clear lit_points here.
        #
        # They must remain when the left palm is holding
        # the current interaction state.
        if (
            not active
            or palm_x is None
            or palm_y is None
        ):
            self.capture_timer = 0.0
            self.rotation_reference_angle = None
            self.last_rotation_step = 0
            return

        # ------------------------------------------------
        # Find nearest pillar
        # ------------------------------------------------

        normalized_x = palm_x / self.width

        distances = [
            abs(normalized_x - pillar_x)
            for pillar_x in self.pillar_x
        ]

        pillar_index = int(
            np.argmin(distances)
        )

        if distances[pillar_index] > 0.16:
            self.capture_timer = 0.0
            return

        normalized_y = palm_y / self.height

        normalized_y = max(
            self.y_top,
            min(
                self.y_bottom,
                normalized_y,
            ),
        )

        self.current_pillar = pillar_index
        self.current_y = normalized_y

        # ------------------------------------------------
        # Hand rotation → color
        # ------------------------------------------------

        if palm_angle is not None:

            # First frame of a new right-palm interaction.
            if self.rotation_reference_angle is None:
                self.rotation_reference_angle = palm_angle
                self.last_rotation_step = 0

            rotation = self._angle_difference(
                palm_angle,
                self.rotation_reference_angle,
            )

            # One color step every ~60 degrees.
            rotation_step = int(
                rotation / 60.0
            )

            if rotation_step != self.last_rotation_step:
                self.last_rotation_step = rotation_step

                self.color_index = (
                    rotation_step
                    % len(self.color_palette)
                )

        # ------------------------------------------------
        # Persistent light points
        # ------------------------------------------------

        self.capture_timer += dt

        if self.capture_timer >= self.capture_interval:
            self.capture_timer = 0.0

            points = self.lit_points[pillar_index]

            too_close = any(
                abs(existing_y - normalized_y) < 0.05
                for existing_y in points
            )

            if not too_close:
                points.append(normalized_y)

                total_points = sum(
                    len(group)
                    for group in self.lit_points
                )

                if total_points > self.max_total_points:
                    for group in self.lit_points:
                        if group:
                            group.pop(0)
                            break

    # ----------------------------------------------------
    # Render
    # ----------------------------------------------------

    def render(self, frame):

        color = self.color_palette[
            self.color_index
        ]

        glow = np.zeros_like(frame)

        # ------------------------------------------------
        # Persistent lights
        # ------------------------------------------------

        for pillar_index, points in enumerate(
            self.lit_points
        ):
            x = int(
                self.pillar_x[pillar_index]
                * self.width
            )

            for normalized_y in points:

                y = int(
                    normalized_y * self.height
                )

                cv2.circle(
                    glow,
                    (x, y),
                    14,
                    color,
                    -1,
                    cv2.LINE_AA,
                )

        # ------------------------------------------------
        # Current moving light
        # ------------------------------------------------

        if (
            self.current_pillar is not None
            and self.current_y is not None
        ):
            x = int(
                self.pillar_x[
                    self.current_pillar
                ]
                * self.width
            )

            y = int(
                self.current_y
                * self.height
            )

            cv2.circle(
                glow,
                (x, y),
                22,
                color,
                -1,
                cv2.LINE_AA,
            )

        # ------------------------------------------------
        # One blur only
        # ------------------------------------------------

        if np.any(glow):

            glow = cv2.GaussianBlur(
                glow,
                (0, 0),
                8,
            )

            frame = cv2.addWeighted(
                frame,
                1.0,
                glow,
                0.42,
                0,
            )

        # ------------------------------------------------
        # Persistent cores
        # ------------------------------------------------

        for pillar_index, points in enumerate(
            self.lit_points
        ):
            x = int(
                self.pillar_x[pillar_index]
                * self.width
            )

            for normalized_y in points:

                y = int(
                    normalized_y * self.height
                )

                cv2.circle(
                    frame,
                    (x, y),
                    2,
                    color,
                    -1,
                    cv2.LINE_AA,
                )

        # ------------------------------------------------
        # Moving core
        # ------------------------------------------------

        if (
            self.current_pillar is not None
            and self.current_y is not None
        ):
            x = int(
                self.pillar_x[
                    self.current_pillar
                ]
                * self.width
            )

            y = int(
                self.current_y
                * self.height
            )

            cv2.circle(
                frame,
                (x, y),
                3,
                color,
                -1,
                cv2.LINE_AA,
            )

        return frame

    # ----------------------------------------------------
    # Clear interaction state
    # ----------------------------------------------------

    def reset(self):
        self.lit_points = [
            [] for _ in self.pillar_x
        ]

        self.current_pillar = None
        self.current_y = None

        self.capture_timer = 0.0

        self.rotation_reference_angle = None
        self.last_rotation_step = 0

        self.color_index = 0