from dataclasses import dataclass
from time import monotonic

from gestures.definitions import Gesture

@dataclass(frozen=True)
class GestureEvent:
	gesture: Gesture
	x: float
	y: float
	timestamp: float


class GestureEventManager:
	def __init__(self):
		self.previous_gesture = Gesture.UNKNOWN

	def update(
		self,
		gesture: Gesture,
		x: float,
		y: float,
	) -> GestureEvent | None:

		event = None

		#trigger only when the gesture changes
		if gesture != self.previous_gesture:
			event = GestureEvent(
				gesture = gesture,
				x = x,
				y = y,
				timestamp = monotonic(),
			)

			self.previous_gesture = gesture

		return event
