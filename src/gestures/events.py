from dataclasses import dataclass
from time import monotonic

from effects.anchors import EffectAnchor
from gestures.definitions import Gesture


@dataclass(frozen=True)
class GestureEvent:
    gesture: Gesture
    anchors: dict[str, EffectAnchor]
    timestamp: float


class GestureEventManager:
    def __init__(self):
        self.previous_gesture = Gesture.UNKNOWN

    def update(
        self,
        gesture: Gesture,
        anchors: dict[str, EffectAnchor],
    ) -> GestureEvent | None:

        if gesture == self.previous_gesture:
            return None

        event = GestureEvent(
            gesture=gesture,
            anchors=anchors,
            timestamp=monotonic(),
        )

        self.previous_gesture = gesture

        return event