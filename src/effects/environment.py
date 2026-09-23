import cv2
import numpy as np


class EnvironmentSystem:
    """
    Procedural 2D architectural environment.

    The environment is built once for a given canvas size
    and reused every frame for performance.
    """

    def __init__(self):
        self.time = 0.0
        self.cached_environment = None
        self.cached_size = None

    def update(self, dt: float):
        self.time += dt

    # ---------------------------------
    # Pointed arch helper
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

        points = [
            left_base,
            left_spring,
        ]

        # Left side of arch
        p0 = np.array(
            left_spring,
            dtype=np.float32,
        )

        p1 = np.array(
            (
                center_x
                - int(half_width * 0.72),
                peak_y
                + int(
                    (spring_y - peak_y)
                    * 0.12
                ),
            ),
            dtype=np.float32,
        )

        p2 = np.array(
            peak,
            dtype=np.float32,
        )

        for t in np.linspace(
            0.0,
            1.0,
            samples,
        ):
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

        points.append(peak)

        # Right side of arch
        p0 = np.array(
            peak,
            dtype=np.float32,
        )

        p1 = np.array(
            (
                center_x
                + int(half_width * 0.72),
                peak_y
                + int(
                    (spring_y - peak_y)
                    * 0.12
                ),
            ),
            dtype=np.float32,
        )

        p2 = np.array(
            right_spring,
            dtype=np.float32,
        )

        for t in np.linspace(
            0.0,
            1.0,
            samples,
        ):
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

        points.extend(
            [
                right_spring,
                right_base,
            ]
        )

        return points

    # ---------------------------------
    # Build static environment
    # ---------------------------------

    def _build_environment(
        self,
        width: int,
        height: int,
    ):
        environment = np.zeros(
            (
                height,
                width,
                3,
            ),
            dtype=np.uint8,
        )

        center_x = width // 2

        floor_y = int(
            height * 0.77
        )

        # ---------------------------------
        # Dark base
        # ---------------------------------

        gradient = np.linspace(
            5,
            18,
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

        # ---------------------------------
        # Back wall
        # ---------------------------------

        cv2.rectangle(
            environment,
            (
                0,
                int(height * 0.04),
            ),
            (
                width,
                floor_y,
            ),
            (13, 8, 19),
            -1,
        )

        # ---------------------------------
        # Central wall illumination
        # ---------------------------------

        wall_light = np.zeros_like(
            environment
        )

        cv2.ellipse(
            wall_light,
            (
                center_x,
                int(height * 0.43),
            ),
            (
                int(width * 0.31),
                int(height * 0.37),
            ),
            0,
            0,
            360,
            (34, 10, 45),
            -1,
        )

        wall_light = cv2.GaussianBlur(
            wall_light,
            (0, 0),
            28,
        )

        environment = cv2.add(
            environment,
            wall_light,
        )

        # ---------------------------------
        # Side wall darkness
        # ---------------------------------

        side_shadow = np.zeros_like(
            environment
        )

        cv2.rectangle(
            side_shadow,
            (
                0,
                0,
            ),
            (
                int(width * 0.22),
                height,
            ),
            (0, 0, 0),
            -1,
        )

        cv2.rectangle(
            side_shadow,
            (
                int(width * 0.78),
                0,
            ),
            (
                width,
                height,
            ),
            (0, 0, 0),
            -1,
        )

        side_shadow = cv2.GaussianBlur(
            side_shadow,
            (0, 0),
            45,
        )

        environment = cv2.addWeighted(
            environment,
            1.0,
            side_shadow,
            0.12,
            0,
        )

        # ---------------------------------
        # Outer columns
        # ---------------------------------

        outer_column = (
            46,
            24,
            50,
        )

        outer_highlight = (
            70,
            35,
            74,
        )

        outer_width = max(
            8,
            int(width * 0.023),
        )

        for position in (
            0.075,
            0.925,
        ):
            x = int(
                width * position
            )

            top = int(
                height * 0.12
            )

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
        # Inner columns
        # ---------------------------------

        inner_column = (
            31,
            17,
            37,
        )

        for position, top_ratio in (
            (0.18, 0.19),
            (0.30, 0.26),
            (0.70, 0.26),
            (0.82, 0.19),
        ):
            x = int(
                width * position
            )

            column_width = max(
                4,
                int(width * 0.011),
            )

            top = int(
                height * top_ratio
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
                inner_column,
                -1,
            )

        # ---------------------------------
        # Side alcoves
        # ---------------------------------

        alcove_color = (
            17,
            9,
            22,
        )

        alcove_edge = (
            49,
            24,
            53,
        )

        alcove_width = int(
            width * 0.12
        )

        alcove_top = int(
            height * 0.35
        )

        for x in (
            int(width * 0.18),
            int(width * 0.82),
        ):

            left = (
                x - alcove_width // 2
            )

            right = (
                x + alcove_width // 2
            )

            cv2.rectangle(
                environment,
                (
                    left,
                    alcove_top,
                ),
                (
                    right,
                    floor_y,
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
                    int(
                        alcove_width
                        * 0.56
                    ),
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
                    int(
                        alcove_width
                        * 0.56
                    ),
                ),
                0,
                180,
                360,
                alcove_edge,
                2,
                cv2.LINE_AA,
            )

        # ---------------------------------
        # Main outer arch
        # ---------------------------------

        outer_arch = (
            self._pointed_arch_points(
                center_x=center_x,
                bottom_y=int(
                    height * 0.78
                ),
                spring_y=int(
                    height * 0.44
                ),
                peak_y=int(
                    height * 0.08
                ),
                half_width=int(
                    width * 0.29
                ),
            )
        )

        # Arch glow
        arch_glow = np.zeros_like(
            environment
        )

        cv2.polylines(
            arch_glow,
            [
                np.array(
                    outer_arch,
                    dtype=np.int32,
                )
            ],
            False,
            (
                82,
                31,
                99,
            ),
            7,
            cv2.LINE_AA,
        )

        arch_glow = cv2.GaussianBlur(
            arch_glow,
            (0, 0),
            8,
        )

        environment = cv2.add(
            environment,
            arch_glow,
        )

        cv2.polylines(
            environment,
            [
                np.array(
                    outer_arch,
                    dtype=np.int32,
                )
            ],
            False,
            (
                67,
                35,
                72,
            ),
            4,
            cv2.LINE_AA,
        )

        # ---------------------------------
        # Second arch
        # ---------------------------------

        second_arch = (
            self._pointed_arch_points(
                center_x=center_x,
                bottom_y=int(
                    height * 0.78
                ),
                spring_y=int(
                    height * 0.50
                ),
                peak_y=int(
                    height * 0.15
                ),
                half_width=int(
                    width * 0.235
                ),
            )
        )

        cv2.polylines(
            environment,
            [
                np.array(
                    second_arch,
                    dtype=np.int32,
                )
            ],
            False,
            (
                48,
                24,
                52,
            ),
            2,
            cv2.LINE_AA,
        )

        # ---------------------------------
        # Central portal
        # ---------------------------------

        portal_width = int(
            width * 0.205
        )

        portal_left = (
            center_x
            - portal_width // 2
        )

        portal_right = (
            center_x
            + portal_width // 2
        )

        portal_bottom = floor_y

        portal_arch = (
            self._pointed_arch_points(
                center_x=center_x,
                bottom_y=portal_bottom,
                spring_y=int(
                    height * 0.50
                ),
                peak_y=int(
                    height * 0.24
                ),
                half_width=portal_width // 2,
                samples=18,
            )
        )

        # Dark portal interior
        cv2.fillPoly(
            environment,
            [
                np.array(
                    portal_arch,
                    dtype=np.int32,
                )
            ],
            (
                2,
                1,
                5,
            ),
        )

        cv2.polylines(
            environment,
            [
                np.array(
                    portal_arch,
                    dtype=np.int32,
                )
            ],
            False,
            (
                56,
                27,
                61,
            ),
            2,
            cv2.LINE_AA,
        )

        # ---------------------------------
        # Portal light source
        # ---------------------------------

        portal_light = np.zeros_like(
            environment
        )

        cv2.ellipse(
            portal_light,
            (
                center_x,
                int(height * 0.56),
            ),
            (
                int(width * 0.095),
                int(height * 0.17),
            ),
            0,
            0,
            360,
            (
                70,
                20,
                78,
            ),
            -1,
        )

        portal_light = cv2.GaussianBlur(
            portal_light,
            (0, 0),
            18,
        )

        environment = cv2.add(
            environment,
            portal_light,
        )

        # Brighter inner core
        core_light = np.zeros_like(
            environment
        )

        cv2.ellipse(
            core_light,
            (
                center_x,
                int(height * 0.55),
            ),
            (
                int(width * 0.045),
                int(height * 0.11),
            ),
            0,
            0,
            360,
            (
                52,
                10,
                57,
            ),
            -1,
        )

        core_light = cv2.GaussianBlur(
            core_light,
            (0, 0),
            12,
        )

        environment = cv2.add(
            environment,
            core_light,
        )

        # ---------------------------------
        # Light rays from portal
        # ---------------------------------

        light_rays = np.zeros_like(
            environment
        )

        ray_color = (
            42,
            13,
            47,
        )

        ray_top = int(
            height * 0.30
        )

        ray_bottom = int(
            height * 0.69
        )

        ray_width = int(
            width * 0.09
        )

        rays = (
            (
                center_x
                - ray_width,
                center_x
                - int(width * 0.015),
            ),
            (
                center_x
                + int(width * 0.015),
                center_x
                + ray_width,
            ),
        )

        for left_x, right_x in rays:

            polygon = np.array(
                [
                    (
                        left_x,
                        ray_top,
                    ),
                    (
                        right_x,
                        ray_top,
                    ),
                    (
                        center_x
                        + int(
                            (
                                right_x
                                - center_x
                            )
                            * 0.42
                        ),
                        ray_bottom,
                    ),
                    (
                        center_x
                        + int(
                            (
                                left_x
                                - center_x
                            )
                            * 0.42
                        ),
                        ray_bottom,
                    ),
                ],
                dtype=np.int32,
            )

            cv2.fillPoly(
                light_rays,
                [polygon],
                ray_color,
            )

        light_rays = cv2.GaussianBlur(
            light_rays,
            (0, 0),
            6,
        )

        environment = cv2.add(
            environment,
            light_rays,
        )

        # ---------------------------------
        # Receding portal depth lines
        # ---------------------------------

        depth_color = (
            25,
            12,
            29,
        )

        inner_width = int(
            portal_width * 0.62
        )

        inner_top = int(
            height * 0.39
        )

        inner_left = (
            center_x
            - inner_width // 2
        )

        inner_right = (
            center_x
            + inner_width // 2
        )

        cv2.line(
            environment,
            (
                portal_left,
                portal_bottom,
            ),
            (
                inner_left,
                inner_top,
            ),
            depth_color,
            2,
            cv2.LINE_AA,
        )

        cv2.line(
            environment,
            (
                portal_right,
                portal_bottom,
            ),
            (
                inner_right,
                inner_top,
            ),
            depth_color,
            2,
            cv2.LINE_AA,
        )

        # ---------------------------------
        # Ceiling ribs
        # ---------------------------------

        ceiling_color = (
            28,
            15,
            34,
        )

        ceiling_top = int(
            height * 0.04
        )

        ceiling_center = int(
            height * 0.31
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
        # Floor base
        # ---------------------------------

        cv2.rectangle(
            environment,
            (
                0,
                floor_y,
            ),
            (
                width,
                height,
            ),
            (
                9,
                6,
                13,
            ),
            -1,
        )

        # ---------------------------------
        # Portal light on floor
        # ---------------------------------

        floor_light = np.zeros_like(
            environment
        )

        floor_polygon = np.array(
            [
                (
                    center_x
                    - int(width * 0.035),
                    floor_y,
                ),
                (
                    center_x
                    + int(width * 0.035),
                    floor_y,
                ),
                (
                    center_x
                    + int(width * 0.17),
                    height,
                ),
                (
                    center_x
                    - int(width * 0.17),
                    height,
                ),
            ],
            dtype=np.int32,
        )

        cv2.fillPoly(
            floor_light,
            [floor_polygon],
            (
                24,
                8,
                28,
            ),
        )

        floor_light = cv2.GaussianBlur(
            floor_light,
            (0, 0),
            15,
        )

        environment = cv2.add(
            environment,
            floor_light,
        )

        # ---------------------------------
        # Subtle floor architecture
        # ---------------------------------

        floor_line = (
            30,
            15,
            35,
        )

        # Fewer horizontal lines
        for i in range(5):

            t = i / 5

            y = int(
                floor_y
                + (
                    height
                    - floor_y
                )
                * (t ** 0.62)
            )

            cv2.line(
                environment,
                (
                    0,
                    y,
                ),
                (
                    width,
                    y,
                ),
                floor_line,
                1,
                cv2.LINE_AA,
            )

        # Fewer perspective divisions
        vanishing_point = (
            center_x,
            floor_y,
        )

        for x in np.linspace(
            0,
            width,
            9,
        ):

            cv2.line(
                environment,
                vanishing_point,
                (
                    int(x),
                    height,
                ),
                floor_line,
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
            (
                51,
                24,
                56,
            ),
            1,
            cv2.LINE_AA,
        )

        # ---------------------------------
        # Soft foreground darkening
        # ---------------------------------

        vignette = np.zeros_like(
            environment
        )

        cv2.rectangle(
            vignette,
            (
                0,
                0,
            ),
            (
                width,
                height,
            ),
            (
                0,
                0,
                0,
            ),
            -1,
        )

        vignette = cv2.GaussianBlur(
            vignette,
            (0, 0),
            35,
        )

        environment = cv2.addWeighted(
            environment,
            1.0,
            vignette,
            0.07,
            0,
        )

        return environment

    # ---------------------------------
    # Render cached scene
    # ---------------------------------

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

    # ---------------------------------
    # Reset
    # ---------------------------------

    def reset(self):
        self.time = 0.0
        self.cached_environment = None
        self.cached_size = None