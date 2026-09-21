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

    @property
    def wrist(self) -> Landmark:
        return self.points[0]

    @property
    def thumb_tip(self) -> Landmark:
        return self.points[4]

    @property
    def index_tip(self) -> Landmark:
        return self.points[8]

    @property
    def middle_tip(self) -> Landmark:
        return self.points[12]

    @property
    def ring_tip(self) -> Landmark:
        return self.points[16]

    @property
    def pinky_tip(self) -> Landmark:
        return self.points[20]