import math

from hand_tracking.landmarks import HandLandmarks, Landmark


def distance(a: Landmark, b: Landmark) -> float:
    return math.sqrt(
        (a.x - b.x) ** 2
        + (a.y - b.y) ** 2
        + (a.z - b.z) ** 2
    )


def angle(
    a: Landmark,
    b: Landmark,
    c: Landmark,
) -> float:
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

    dot_product = sum(
        x * y
        for x, y in zip(ba, bc)
    )

    magnitude_ba = math.sqrt(
        sum(x * x for x in ba)
    )

    magnitude_bc = math.sqrt(
        sum(x * x for x in bc)
    )

    if magnitude_ba == 0 or magnitude_bc == 0:
        return 0.0

    cosine = dot_product / (
        magnitude_ba * magnitude_bc
    )

    cosine = max(
        -1.0,
        min(1.0, cosine),
    )

    return math.degrees(
        math.acos(cosine)
    )


def finger_angles(
    hand: HandLandmarks,
) -> dict[str, float]:
    """
    Calculate joint angles for the
    index, middle, ring and pinky fingers.
    """

    return {
        "index": angle(
            hand[5],
            hand[6],
            hand[7],
        ),
        "middle": angle(
            hand[9],
            hand[10],
            hand[11],
        ),
        "ring": angle(
            hand[13],
            hand[14],
            hand[15],
        ),
        "pinky": angle(
            hand[17],
            hand[18],
            hand[19],
        ),
    }


def thumb_angles(
    hand: HandLandmarks,
) -> dict[str, float]:
    """
    Calculate the two main thumb joint angles.

    Thumb landmarks:
        1 = CMC
        2 = MCP
        3 = IPPYTHONPATH=src python src/main.py
        4 = TIP
    """

    return {
        "thumb_mcp": angle(
            hand[1],
            hand[2],
            hand[3],
        ),
        "thumb_ip": angle(
            hand[2],
            hand[3],
            hand[4],
        ),
    }

def vector(a: Landmark, b: Landmark) -> tuple[float, float, float]:
    return (
        b.x - a.x,
        b.y - a.y,
        b.z - a.z,
    )


def vector_angle(
    v1: tuple[float, float, float],
    v2: tuple[float, float, float],
) -> float:
    dot = sum(
        a * b
        for a, b in zip(v1, v2)
    )

    mag1 = math.sqrt(
        sum(value * value for value in v1)
    )

    mag2 = math.sqrt(
        sum(value * value for value in v2)
    )

    if mag1 == 0 or mag2 == 0:
        return 0.0

    cosine = dot / (mag1 * mag2)

    cosine = max(
        -1.0,
        min(1.0, cosine),
    )

    return math.degrees(
        math.acos(cosine)
    )


def l_shape_angle(
    hand: HandLandmarks,
) -> float:
    """
    Angle between the index-finger direction
    and thumb direction.
    """

    index_vector = vector(
        hand[5],
        hand[8],
    )

    thumb_vector = vector(
        hand[2],
        hand[4],
    )

    return vector_angle(
        index_vector,
        thumb_vector,
    )


def thumb_extension_distance(
    hand: HandLandmarks,
) -> float:
    """
    Thumb-tip distance from the palm center,
    normalized by palm width.
    """

    palm_points = [
        hand[0],
        hand[5],
        hand[9],
        hand[13],
        hand[17],
    ]

    palm_x = sum(
        point.x for point in palm_points
    ) / len(palm_points)

    palm_y = sum(
        point.y for point in palm_points
    ) / len(palm_points)

    palm_center = Landmark(
        x=palm_x,
        y=palm_y,
        z=0.0,
    )

    palm_width = distance(
        hand[5],
        hand[17],
    )

    if palm_width == 0:
        return 0.0

    return (
        distance(
            hand.thumb_tip,
            palm_center,
        )
        / palm_width
    )