import cv2
import numpy as np


class EnvironmentSystem:
    """
    Procedural 2D architectural environment.

    The static scene is cached so the environment does not
    need to be rebuilt every frame.
    """

    def __init__(self):
        self.time = 0.0
        self.cached_environment = None
        self.cached_size = None

    def update(self, dt: float):
        self.time += dt

    # ---------------------------------
    # Point helper
    # ---------------------------------

    def _pointed_arch_points(
        self,
        center_x: int,
        bottom_y: int,
        spring_y: int,
        peak_y: int,
        half_width: int,
        samples: int = 24,
    ):
        """
        Create a smooth pointed-arch outline using two
        quadratic Bezier curves.
        """

        left_base = (
            center_x - half_width,
            bottom_y,
        )

        left_spring = (
            center_x - half_width,
            spring_y,
        )

        right_spring = (
            center_x + half_width,
            spring_y,
        )

        right_base = (
            center_x + half_width,
            bottom_y,
        )

        peak = (
            center_x,
            peak_y,
        )

        points = []

        # Left vertical side
        points.append(left_base)
        points.append(left_spring)

        # Left curve → peak
        p0 = np.array(left_spring, dtype=np.float32)
        p1 = np.array(
            (
                center_x - int(half_width * 0.72),
                peak_y + int((spring_y - peak_y) * 0.10),
            ),
            dtype=np.float32,
        )
        p2 = np.array(peak, dtype=np.float32)

        for t in np.linspace(0.0, 1.0, samples):
            point = (
                (1 - t) ** 2 * p0
                + 2 * (1 - t) * t * p1
                + t**2 * p2
            )

            points.append(
                (
                    int(point[0]),
                    int(point[1]),
                )
            )

        # Peak
        points.append(peak)

        # Right curve → spring
        p0 = np.array(peak, dtype=np.float32)
        p1 = np.array(
            (
                center_x + int(half_width * 0.72),
                peak_y + int((spring_y - peak_y) * 0.10),
            ),
            dtype=np.float32,
        )
        p2 = np.array(right_spring, dtype=np.float32)

        for t in np.linspace(0.0, 1.0, samples):
            point = (
                (1 - t) ** 2 * p0
                + 2 * (1 - t) * t * p1
                + t**2 * p2
            )

            points.append(
                (
                    int(point[0]),
                    int(point[1]),
                )
            )

        points.append(right_spring)
        points.append(right_base)

        return points

    # ---------------------------------
    # Build static scene
    # ---------------------------------

    def _build_environment(
        self,
        width: int,
        height: int,
    ):
        environment = np.zeros(
            (height, width, 3),
            dtype=np.uint8,
        )

        center_x = width // 2

        # ---------------------------------
        # Background gradient
        # ---------------------------------

        gradient = np.linspace(
            7,
            20,
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

        floor_y = int(height * 0.77)

        # ---------------------------------
        # Main wall
        # ---------------------------------

        cv2.rectangle(
            environment,
            (0, int(height * 0.04)),
            (width, floor_y),
            (15, 9, 21),
            -1,
        )

        # ---------------------------------
        # Central ambient illumination
        # ---------------------------------

        glow = np.zeros_like(environment)

        cv2.ellipse(
            glow,
            (
                center_x,
                int(height * 0.42),
            ),
            (
                int(width * 0.34),
                int(height * 0.40),
            ),
            0,
            0,
            360,
            (38, 12, 52),
            -1,
        )

        glow = cv2.GaussianBlur(
            glow,
            (0, 0),
            18,
        )

        environment = cv2.add(
            environment,
            glow,
        )

        # ---------------------------------
        # Far wall divisions
        # ---------------------------------

        wall_line = (31, 17, 36)

        for ratio in (
            0.13,
            0.20,
            0.27,
        ):
            y = int(height * ratio)

            cv2.line(
                environment,
                (0, y),
                (width, y),
                wall_line,
                1,
                cv2.LINE_AA,
            )

        # ---------------------------------
        # Main outer columns
        # ---------------------------------

        outer_column = (48, 25, 51)
        outer_highlight = (73, 37, 76)

        outer_positions = (
            0.07,
            0.93,
        )

        outer_width = max(
            8,
            int(width * 0.025),
        )

        for position in outer_positions:

            x = int(width * position)

            top = int(height * 0.12)

            cv2.rectangle(
                environment,
                (
                    x - outer_width // 2,
                    top,
                ),
                (
                    x + outer_width // 2,
                    floor_y,
                ),
                outer_column,
                -1,
            )

            cv2.line(
                environment,
                (
                    x - outer_width // 2,
                    top,
                ),
                (
                    x - outer_width // 2,
                    floor_y,
                ),
                outer_highlight,
                1,
                cv2.LINE_AA,
            )

        # ---------------------------------
        # Secondary columns
        # ---------------------------------

        secondary_column = (33, 18, 40)

        secondary_positions = (
            0.18,
            0.30,
            0.70,
            0.82,
        )

        for position in secondary_positions:

            x = int(width * position)

            column_width = max(
                4,
                int(width * 0.012),
            )

            top = int(
                height * (
                    0.18
                    if position in (0.18, 0.82)
                    else 0.25
                )
            )

            cv2.rectangle(
                environment,
                (
                    x - column_width // 2,
                    top,
                ),
                (
                    x + column_width // 2,
                    floor_y,
                ),
                secondary_column,
                -1,
            )

        # ---------------------------------
        # Side alcoves
        # ---------------------------------

        alcove_color = (22, 11, 28)

        alcove_width = int(
            width * 0.13
        )

        alcove_top = int(
            height * 0.34
        )

        alcove_bottom = floor_y

        for x in (
            int(width * 0.18),
            int(width * 0.82),
        ):

            left = x - alcove_width // 2
            right = x + alcove_width // 2

            cv2.rectangle(
                environment,
                (
                    left,
                    alcove_top,
                ),
                (
                    right,
                    alcove_bottom,
                ),
                alcove_color,
                -1,
            )

            cv2.ellipse(
                environment,
                (
                    x,
                    alcove_top,
                ),
                (
                    alcove_width // 2,
                    int(alcove_width * 0.55),
                ),
                0,
                180,
                360,
                alcove_color,
                -1,
            )

            cv2.ellipse(
                environment,
                (
                    x,
                    alcove_top,
                ),
                (
                    alcove_width // 2,
                    int(alcove_width * 0.55),
                ),
                0,
                180,
                360,
                (52, 27, 57),
                2,
                cv2.LINE_AA,
            )

        # ---------------------------------
        # Grand central pointed arch
        # ---------------------------------

        arch_bottom = int(
            height * 0.78
        )

        arch_spring = int(
            height * 0.44
        )

        arch_peak = int(
            height * 0.10
        )

        arch_half_width = int(
            width * 0.29
        )

        outer_arch = self._pointed_arch_points(
            center_x,
            arch_bottom,
            arch_spring,
            arch_peak,
            arch_half_width,
        )

        # Soft arch glow
        arch_glow = np.zeros_like(environment)

        cv2.polylines(
            arch_glow,
            [
                np.array(
                    outer_arch,
                    dtype=np.int32,
                )
            ],
            False,
            (91, 36, 108),
            7,
            cv2.LINE_AA,
        )

        arch_glow = cv2.GaussianBlur(
            arch_glow,
            (0, 0),
            9,
        )

        environment = cv2.add(
            environment,
            arch_glow,
        )

        # Main arch
        cv2.polylines(
            environment,
            [
                np.array(
                    outer_arch,
                    dtype=np.int32,
                )
            ],
            False,
            (69, 35, 73),
            4,
            cv2.LINE_AA,
        )

        # ---------------------------------
        # Second arch layer
        # ---------------------------------

        inner_arch = self._pointed_arch_points(
            center_x,
            int(height * 0.78),
            int(height * 0.49),
            int(height * 0.17),
            int(width * 0.23),
        )

        cv2.polylines(
            environment,
            [
                np.array(
                    inner_arch,
                    dtype=np.int32,
                )
            ],
            False,
            (49, 25, 53),
            2,
            cv2.LINE_AA,
        )

        # ---------------------------------
        # Central deep portal
        # ---------------------------------

        portal_width = int(
            width * 0.245
        )

        portal_left = (
            center_x - portal_width // 2
        )

        portal_right = (
            center_x + portal_width // 2
        )

        portal_top = int(
            height * 0.29
        )

        # Portal interior
        cv2.rectangle(
            environment,
            (
                portal_left,
                portal_top,
            ),
            (
                portal_right,
                floor_y,
            ),
            (2, 1, 5),
            -1,
        )

        portal_arch = self._pointed_arch_points(
            center_x,
            floor_y,
            int(height * 0.50),
            int(height * 0.26),
            portal_width // 2,
            samples=18,
        )

        cv2.fillPoly(
            environment,
            [
                np.array(
                    portal_arch,
                    dtype=np.int32,
                )
            ],
            (2, 1, 5),
        )

        # Portal edges
        cv2.polylines(
            environment,
            [
                np.array(
                    portal_arch,
                    dtype=np.int32,
                )
            ],
            False,
            (55, 26, 59),
            2,
            cv2.LINE_AA,
        )

        # ---------------------------------
        # Vertical portal light accents
        # ---------------------------------

        portal_highlight = (83, 40, 87)

        cv2.line(
            environment,
            (
                portal_left,
                int(height * 0.50),
            ),
            (
                portal_left,
                floor_y,
            ),
            portal_highlight,
            1,
            cv2.LINE_AA,
        )

        cv2.line(
            environment,
            (
                portal_right,
                int(height * 0.50),
            ),
            (
                portal_right,
                floor_y,
            ),
            portal_highlight,
            1,
            cv2.LINE_AA,
        )

        # ---------------------------------
        # Ceiling ribs
        # ---------------------------------

        ceiling_color = (34, 18, 40)

        ceiling_top = int(
            height * 0.04
        )

        ceiling_center = int(
            height * 0.30
        )

        for x in np.linspace(
            width * 0.05,
            width * 0.95,
            9,
        ):

            cv2.line(
                environment,
                (
                    int(x),
                    ceiling_top,
                ),
                (
                    center_x,
                    ceiling_center,
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
            (11, 7, 15),
            -1,
        )

        floor_color = (42, 22, 47)

        # Horizontal depth bands
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
            15,
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
            vanishing_point,
            (
                center_x,
                height,
            ),
            (58, 28, 62),
            2,
            cv2.LINE_AA,
        )

        # ---------------------------------
        # Return cached static scene
        # ---------------------------------

        return environment

    def render(self, frame):
        height, width = frame.shape[:2]

        current_size = (
            width,
            height,
        )

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

        return self.cached_environment.copy()

    def reset(self):
        self.time = 0.0
        self.cached_environment = None
        self.cached_size = None