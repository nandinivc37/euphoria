from gestures.definitions import Gesture


class GestureStabilizer:
    """
    Filters short-lived gesture changes caused by
    frame-to-frame detection noise.

    A new gesture must appear for several consecutive
    frames before becoming the stable gesture.

    UNKNOWN is treated specially: short UNKNOWN periods
    do not immediately erase the current stable gesture.
    """

    def __init__(
        self,
        required_frames: int = 5,
        unknown_frames: int = 8,
    ):
        self.required_frames = required_frames
        self.unknown_frames = unknown_frames

        self.current_gesture = Gesture.UNKNOWN

        self.candidate_gesture = Gesture.UNKNOWN
        self.candidate_count = 0

        self.unknown_count = 0

    def update(self, raw_gesture: Gesture) -> Gesture:
        # --------------------------------
        # Same as current stable gesture
        # --------------------------------

        if raw_gesture == self.current_gesture:

            self.candidate_gesture = raw_gesture
            self.candidate_count = 0
            self.unknown_count = 0

            return self.current_gesture

        # --------------------------------
        # UNKNOWN handling
        # --------------------------------

        if raw_gesture == Gesture.UNKNOWN:

            self.unknown_count += 1

            self.candidate_gesture = Gesture.UNKNOWN
            self.candidate_count = 0

            # Do not immediately lose the current
            # gesture because of a few bad frames.
            if self.unknown_count >= self.unknown_frames:

                self.current_gesture = Gesture.UNKNOWN
                self.unknown_count = 0

            return self.current_gesture

        # --------------------------------
        # New non-UNKNOWN gesture
        # --------------------------------

        self.unknown_count = 0

        if raw_gesture != self.candidate_gesture:

            self.candidate_gesture = raw_gesture
            self.candidate_count = 1

        else:

            self.candidate_count += 1

        # --------------------------------
        # Confirm new gesture
        # --------------------------------

        if self.candidate_count >= self.required_frames:

            self.current_gesture = self.candidate_gesture
            self.candidate_count = 0

        return self.current_gesture