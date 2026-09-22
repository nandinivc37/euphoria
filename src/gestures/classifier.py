from gestures.definitions import FingerState, Gesture
from gestures.features import (
    finger_angles,
    thumb_angles,
)
from hand_tracking.landmarks import HandLandmarks


EXTENDED_ANGLE_THRESHOLD = 160.0

THUMB_MCP_THRESHOLD = 145.0
THUMB_IP_THRESHOLD = 145.0


class GestureClassifier:

    def finger_states(
        self,
        hand: HandLandmarks,
    ) -> dict[str, FingerState]:

        # -----------------------------
        # Four long fingers
        # -----------------------------

        angles = finger_angles(hand)

        states = {
            finger: (
                FingerState.OPEN
                if joint_angle >= EXTENDED_ANGLE_THRESHOLD
                else FingerState.CLOSED
            )
            for finger, joint_angle in angles.items()
        }

        # -----------------------------
        # Thumb
        # -----------------------------

        thumb = thumb_angles(hand)

        thumb_is_open = (
            thumb["thumb_mcp"] >= THUMB_MCP_THRESHOLD
            and thumb["thumb_ip"] >= THUMB_IP_THRESHOLD
        )

        states["thumb"] = (
            FingerState.OPEN
            if thumb_is_open
            else FingerState.CLOSED
        )

        return states

    def classify(
        self,
        hand: HandLandmarks,
    ) -> Gesture:

        states = self.finger_states(hand)

        thumb = states["thumb"] == FingerState.OPEN
        index = states["index"] == FingerState.OPEN
        middle = states["middle"] == FingerState.OPEN
        ring = states["ring"] == FingerState.OPEN
        pinky = states["pinky"] == FingerState.OPEN

        # -----------------------------
        # FIVE
        # All five fingers open
        # -----------------------------

        if (
            thumb
            and index
            and middle
            and ring
            and pinky
        ):
            return Gesture.FIVE

        # -----------------------------
        # FOUR
        # Four long fingers open,
        # thumb closed
        # -----------------------------

        if (
            not thumb
            and index
            and middle
            and ring
            and pinky
        ):
            return Gesture.FOUR

        # -----------------------------
        # THREE
        # Thumb ignored
        # -----------------------------

        if (
            index
            and middle
            and ring
            and not pinky
        ):
            return Gesture.THREE

        # -----------------------------
        # TWO
        # Thumb ignored
        # -----------------------------

        if (
            index
            and middle
            and not ring
            and not pinky
        ):
            return Gesture.TWO

        # -----------------------------
        # ONE
        # Thumb ignored
        # -----------------------------

        if (
            index
            and not middle
            and not ring
            and not pinky
        ):
            return Gesture.ONE

        # -----------------------------
        # FIST
        # All five fingers closed
        # -----------------------------

        if (
            not thumb
            and not index
            and not middle
            and not ring
            and not pinky
        ):
            return Gesture.FIST

        return Gesture.UNKNOWN