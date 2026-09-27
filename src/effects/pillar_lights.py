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

        # Approximate pillar x positions in the cathedral image.
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

        # Persistent activated positions.
        self.lit_points: list[list[float]] = [
            [] for _ in self.pillar_x
        ]

        # Current moving light.
        self.current_pillar = None
        self.current_y = None

        self.capture_timer = 0.0
        self.capture_interval = 0.18

        # Hard limit so the effect can never grow indefinitely.
        self.max_total_points = 24

    def update(
        self,
        dt: float,
        active: bool,
        palm_x: float | None,
        palm_y: float | None,
    ):
        self.current_pillar = None
        self.current_y = None

        if (
            not active
            or palm_x is None
            or palm_y is None
        ):
            self.capture_timer = 0.0
            return

        normalized_x = palm_x / self.width

        distances = [
            abs(normalized_x - pillar_x)
            for pillar_x in self.pillar_x
        ]

        pillar_index = int(
            np.argmin(distances)
        )

        # Don't light a pillar if the hand is too far
        # from the architectural sides.
        if distances[pillar_index] > 0.16:
            self.capture_timer = 0.0
            return

        normalized_y = palm_y / self.height

        normalized_y = max(
            self.y_top,
            min(self.y_bottom, normalized_y),
        )

        self.current_pillar = pillar_index
        self.current_y = normalized_y

        # Leave a persistent point behind periodically.
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

                # Global point cap.
                total_points = sum(
                    len(points)
                    for points in self.lit_points
                )

                if total_points > self.max_total_points:
                    # Remove the oldest point.
                    for pillar_points in self.lit_points:
                        if pillar_points:
                            pillar_points.pop(0)
                            break

    def render(self, frame):
        """
        Performance-optimized rendering:
        draw ALL glow sources to one layer,
        blur ONCE, then composite ONCE.
        """

        glow = np.zeros_like(frame)

        # -----------------------------
        # Persistent lights
        # -----------------------------

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
                    (255, 210, 150),
                    -1,
                    cv2.LINE_AA,
                )

        # -----------------------------
        # Moving light
        # -----------------------------

        if (
            self.current_pillar is not None
            and self.current_y is not None
        ):
            x = int(
                self.pillar_x[self.current_pillar]
                * self.width
            )

            y = int(
                self.current_y * self.height
            )

            cv2.circle(
                glow,
                (x, y),
                22,
                (255, 220, 165),
                -1,
                cv2.LINE_AA,
            )

        # -----------------------------
        # One single blur
        # -----------------------------

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

        # -----------------------------
        # Sharp light cores
        # -----------------------------

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
                    (255, 240, 215),
                    -1,
                    cv2.LINE_AA,
                )

        # Current moving light
        if (
            self.current_pillar is not None
            and self.current_y is not None
        ):
            x = int(
                self.pillar_x[self.current_pillar]
                * self.width
            )

            y = int(
                self.current_y * self.height
            )

            cv2.line(
                frame,
                (x, y - 7),
                (x, y + 7),
                (255, 235, 205),
                2,
                cv2.LINE_AA,
            )

            cv2.circle(
                frame,
                (x, y),
                3,
                (255, 245, 225),
                -1,
                cv2.LINE_AA,
            )

        return frame

    def reset(self):
        self.lit_points = [
            [] for _ in self.pillar_x
        ]

        self.current_pillar = None
        self.current_y = None
        self.capture_timer = 0.0