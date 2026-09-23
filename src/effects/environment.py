import cv2
import numpy as np


class EnvironmentSystem:
    """
    Procedural 2D architectural environment.

    The static architecture is rendered only when the
    canvas size changes. This avoids rebuilding the
    entire environment every frame.
    """

    def __init__(self):
        self.time = 0.0
        self.cached_environment = None
        self.cached_size = None

    def update(self, dt: float):
        self.time += dt

    def _build_environment(self, width: int, height: int):
        # ---------------------------------
        # Base background
        # ---------------------------------

        environment = np.zeros(
            (height, width, 3),
            dtype=np.uint8,
        )

        # Fast vertical gradient
        gradient = np.linspace(
            7,
            22,
            height,
            dtype=np.uint8,
        ).reshape(height, 1)

        environment[:, :, 0] = gradient
        environment[:, :, 1] = gradient
        environment[:, :, 2] = np.clip(
            gradient + 2,
            0,
            255,
        )

        center_x = width // 2
        floor_y = int(height * 0.76)

        # ---------------------------------
        # Back wall
        # ---------------------------------

        cv2.rectangle(
            environment,
            (0, int(height * 0.08)),
            (width, floor_y),
            (18, 12, 24),
            -1,
        )

        # ---------------------------------
        # Central soft glow
        # ---------------------------------

        glow = np.zeros_like(environment)

        cv2.ellipse(
            glow,
            (
                center_x,
                int(height * 0.42),
            ),
            (
                int(width * 0.38),
                int(height * 0.42),
            ),
            0,
            0,
            360,
            (34, 12, 46),
            -1,
        )

        # Use only one moderate blur.
        glow = cv2.GaussianBlur(
            glow,
            (0, 0),
            20,
        )

        environment = cv2.add(
            environment,
            glow,
        )

        # ---------------------------------
        # Architectural columns
        # ---------------------------------

        column_width = max(
            6,
            int(width * 0.022),
        )

        columns = (
            (0.08, 0.14, (48, 27, 52)),
            (0.18, 0.20, (34, 20, 40)),
            (0.29, 0.28, (34, 20, 40)),
            (0.71, 0.28, (34, 20, 40)),
            (0.82, 0.20, (34, 20, 40)),
            (0.92, 0.14, (48, 27, 52)),
        )

        for position, top_ratio, color in columns:

            x = int(width * position)

            top = int(
                height * top_ratio
            )

            current_width = (
                column_width
                if position in (0.08, 0.92)
                else max(4, column_width // 2)
            )

            cv2.rectangle(
                environment,
                (
                    x - current_width // 2,
                    top,
                ),
                (
                    x + current_width // 2,
                    floor_y,
                ),
                color,
                -1,
            )

        # ---------------------------------
        # Large outer arch
        # ---------------------------------

        cv2.ellipse(
            environment,
            (
                center_x,
                int(height * 0.77),
            ),
            (
                int(width * 0.29),
                int(height * 0.41),
            ),
            0,
            180,
            360,
            (65, 38, 69),
            4,
            cv2.LINE_AA,
        )

        # ---------------------------------
        # Inner arch
        # ---------------------------------

        cv2.ellipse(
            environment,
            (
                center_x,
                int(height * 0.77),
            ),
            (
                int(width * 0.215),
                int(height * 0.34),
            ),
            0,
            180,
            360,
            (48, 26, 52),
            2,
            cv2.LINE_AA,
        )

        # ---------------------------------
        # Central doorway
        # ---------------------------------

        doorway_width = int(
            width * 0.27
        )

        doorway_left = (
            center_x
            - doorway_width // 2
        )

        doorway_right = (
            center_x
            + doorway_width // 2
        )

        doorway_top = int(
            height * 0.27
        )

        cv2.rectangle(
            environment,
            (
                doorway_left,
                doorway_top,
            ),
            (
                doorway_right,
                floor_y,
            ),
            (3, 2, 6),
            -1,
        )

        # Rounded top
        cv2.ellipse(
            environment,
            (
                center_x,
                doorway_top,
            ),
            (
                doorway_width // 2,
                int(doorway_width * 0.55),
            ),
            0,
            180,
            360,
            (3, 2, 6),
            -1,
        )

        # ---------------------------------
        # Doorway edge highlights
        # ---------------------------------

        highlight = (62, 31, 68)

        cv2.line(
            environment,
            (
                doorway_left,
                doorway_top,
            ),
            (
                doorway_left,
                floor_y,
            ),
            highlight,
            1,
            cv2.LINE_AA,
        )

        cv2.line(
            environment,
            (
                doorway_right,
                doorway_top,
            ),
            (
                doorway_right,
                floor_y,
            ),
            highlight,
            1,
            cv2.LINE_AA,
        )

        # ---------------------------------
        # Ceiling ribs
        # ---------------------------------

        ceiling_color = (32, 18, 38)

        top = int(height * 0.08)
        middle = int(height * 0.28)

        for x in np.linspace(
            width * 0.10,
            width * 0.90,
            7,
        ):
            cv2.line(
                environment,
                (
                    int(x),
                    top,
                ),
                (
                    center_x,
                    middle,
                ),
                ceiling_color,
                1,
                cv2.LINE_AA,
            )

        # ---------------------------------
        # Floor
        # ---------------------------------

        cv2.rectangle(
            environment,
            (0, floor_y),
            (width, height),
            (12, 8, 16),
            -1,
        )

        floor_color = (39, 21, 44)

        # Horizontal perspective lines
        for i in range(7):

            t = i / 7

            y = int(
                floor_y
                + (height - floor_y)
                * (t ** 0.60)
            )

            cv2.line(
                environment,
                (0, y),
                (width, y),
                floor_color,
                1,
                cv2.LINE_AA,
            )

        # Perspective lines
        vanishing_point = (
            center_x,
            floor_y,
        )

        for x in np.linspace(
            0,
            width,
            13,
        ):

            cv2.line(
                environment,
                vanishing_point,
                (
                    int(x),
                    height,
                ),
                floor_color,
                1,
                cv2.LINE_AA,
            )

        # Central aisle
        cv2.line(
            environment,
            (
                center_x,
                floor_y,
            ),
            (
                center_x,
                height,
            ),
            (56, 28, 60),
            1,
            cv2.LINE_AA,
        )

        return environment

    def render(self, frame):
        height, width = frame.shape[:2]

        # ---------------------------------
        # Build static scene only once
        # ---------------------------------

        current_size = (width, height)

        if (
            self.cached_environment is None
            or self.cached_size != current_size
        ):
            self.cached_environment = (
                self._build_environment(
                    width,
                    height,
                )
            )

            self.cached_size = current_size

        # Return a copy so other effects can
        # safely draw on top of it.
        return self.cached_environment.copy()

    def reset(self):
        self.time = 0.0
        self.cached_environment = None
        self.cached_size = None