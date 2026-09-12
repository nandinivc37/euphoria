from gestures.definitions import FingerState, Gesture
from gestures.features import finger_angles
from hand_tracking.landmarks import HandLandmarks


EXTENDED_ANGLE_THRESHOLD = 160.0


class GestureClassifier:

    def finger_states(
        self,
        hand: HandLandmarks,
    ) -> dict[str, FingerState]:

        angles = finger_angles(hand)

        return {
            finger: (
                FingerState.OPEN
                if joint_angle >= EXTENDED_ANGLE_THRESHOLD
                else FingerState.CLOSED
            )
            for finger, joint_angle in angles.items()
        }

    def classify(
        self,
        hand: HandLandmarks,
    ) -> Gesture:

        states = self.finger_states(hand)

        index = states["index"] == FingerState.OPEN
        middle = states["middle"] == FingerState.OPEN
        ring = states["ring"] == FingerState.OPEN
        pinky = states["pinky"] == FingerState.OPEN

        if index and middle and ring and pinky:
            return Gesture.OPEN_PALM

        if not index and not middle and not ring and not pinky:
            return Gesture.FIST

        if index and not middle and not ring and not pinky:
            return Gesture.POINT

        if index and middle and not ring and not pinky:
            return Gesture.PEACE

        if index and middle and ring and not pinky:
            return Gesture.THREE

        return Gesture.UNKNOWN
