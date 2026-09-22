from enum import Enum


class FingerState(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Gesture(Enum):
    UNKNOWN = "UNKNOWN"

    FIST = "FIST"

    ONE = "ONE"
    TWO = "TWO"
    THREE = "THREE"
    FOUR = "FOUR"
    FIVE = "FIVE"