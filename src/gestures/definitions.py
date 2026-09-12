from enum import Enum


class FingerState(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Gesture(Enum):
    UNKNOWN = "UNKNOWN"
    FIST = "FIST"
    OPEN_PALM = "OPEN_PALM"
    POINT = "POINT"
    PEACE = "PEACE"
    THREE = "THREE"
