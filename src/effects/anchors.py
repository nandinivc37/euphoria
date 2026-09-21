from dataclasses import dataclass

from hand_tracking.landmarks import HandLandmarks


@dataclass(frozen=True)
class EffectAnchor:
    name: str
    x: int
    y: int


class AnchorExtractor:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def _to_pixel(self, x: float, y: float) -> tuple[int, int]:
        return (
            int(x * self.width),
            int(y * self.height),
        )

    def from_hand(
        self,
        hand: HandLandmarks,
    ) -> dict[str, EffectAnchor]:

        anchors = {}

        # Named fingertip / wrist anchors
        named_points = {
            "wrist": hand.wrist,
            "thumb_tip": hand.thumb_tip,
            "index_tip": hand.index_tip,
            "middle_tip": hand.middle_tip,
            "ring_tip": hand.ring_tip,
            "pinky_tip": hand.pinky_tip,
        }

        for name, landmark in named_points.items():

            x, y = self._to_pixel(
                landmark.x,
                landmark.y,
            )

            anchors[name] = EffectAnchor(
                name=name,
                x=x,
                y=y,
            )

        # Palm center
        palm_points = [
            hand.wrist,
            hand[5],
            hand[9],
            hand[13],
            hand[17],
        ]

        palm_x = (
            sum(point.x for point in palm_points)
            / len(palm_points)
        )

        palm_y = (
            sum(point.y for point in palm_points)
            / len(palm_points)
        )

        x, y = self._to_pixel(
            palm_x,
            palm_y,
        )

        anchors["palm_center"] = EffectAnchor(
            name="palm_center",
            x=x,
            y=y,
        )

        return anchors