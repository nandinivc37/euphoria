from dataclasses import dataclass


@dataclass(frozen=True)
class Landmark:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class HandLandmarks:
    points: list[Landmark]

    def __post_init__(self):
        if len(self.points) != 21:
            raise ValueError(
                f"A hand must contain 21 landmarks, "
                f"got {len(self.points)}"
            )

    def __getitem__(self, index: int) -> Landmark:
        return self.points[index]
