from dataclasses import dataclass
from time import monotonic

from gestures.definitions import Gesture
from effects.anchors import EffectAnchor


@dataclass(frozen=True)
class GestureEvent:
    gesture: Gesture
    anchors: list[EffectAnchor]
    timestamp: float


class GestureEventManager:
    def __init__(self):
        self.previous_gesture = Gesture.UNKNOWN

    def update(
        self,
        gesture: Gesture,
        anchors: list[EffectAnchor],
    ) -> GestureEvent | None:

        event = None

        # Trigger an event only when the gesture changes.
        if gesture != self.previous_gesture:
            event = GestureEvent(
                gesture=gesture,
                anchors=anchors,
                timestamp=monotonic(),
            )

            self.previous_gesture = gesture

        return event
