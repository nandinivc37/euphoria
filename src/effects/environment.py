from pathlib import Path

import cv2
import numpy as np


class EnvironmentSystem:
    """
    Static cathedral environment.

    Uses the selected cathedral image as the world background.
    The image is loaded once and reused every frame.
    """

    def __init__(
        self,
        image_path: str = (
            "assets/backgrounds/"
            "cathedral_stylized_900x597.png"
        ),
    ):
        self.image_path = Path(image_path)

        self.background = None
        self.cached_size = None

        self._load_background()

    def _load_background(self):
        image = cv2.imread(
            str(self.image_path),
            cv2.IMREAD_COLOR,
        )

        if image is None:
            raise FileNotFoundError(
                "Could not load cathedral "
                f"background: {self.image_path}"
            )

        self.background = image

    def update(self, dt: float):
        # Static environment for now.
        pass

    def render(self, frame):
        height, width = frame.shape[:2]

        # Use the prepared image directly when
        # the canvas matches its size.
        if (
            self.background.shape[1] == width
            and self.background.shape[0] == height
        ):
            return self.background.copy()

        # Fallback for a different world size.
        return cv2.resize(
            self.background,
            (width, height),
            interpolation=cv2.INTER_AREA,
        )

    def reset(self):
        self.cached_size = None