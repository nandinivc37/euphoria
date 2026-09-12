import math

from hand_tracking.landmarks import HandLandmarks, Landmark


def distance(a: Landmark, b: Landmark) -> float:
    return math.sqrt(
        (a.x - b.x) ** 2 +
        (a.y - b.y) ** 2 +
        (a.z - b.z) ** 2
    )


def angle(a: Landmark, b: Landmark, c: Landmark) -> float:
    """
    Returns angle ABC in degrees.
    """
    ba = (
        a.x - b.x,
        a.y - b.y,
        a.z - b.z,
    )

    bc = (
        c.x - b.x,
        c.y - b.y,
        c.z - b.z,
    )

    dot_product = sum(x * y for x, y in zip(ba, bc))

    magnitude_ba = math.sqrt(sum(x * x for x in ba))
    magnitude_bc = math.sqrt(sum(x * x for x in bc))

    if magnitude_ba == 0 or magnitude_bc == 0:
        return 0.0

    cosine = dot_product / (magnitude_ba * magnitude_bc)

    # Protect against floating-point errors.
    cosine = max(-1.0, min(1.0, cosine))

    return math.degrees(math.acos(cosine))


def finger_angles(hand: HandLandmarks) -> dict[str, float]:
    return {
        "index": angle(hand[5], hand[6], hand[7]),
        "middle": angle(hand[9], hand[10], hand[11]),
        "ring": angle(hand[13], hand[14], hand[15]),
        "pinky": angle(hand[17], hand[18], hand[19]),
    }
