import math

import cv2
import mediapipe as mp
import numpy as np

from hand_tracking.landmarks import (
    Landmark,
    HandLandmarks,
)


class HandDetector:
    def __init__(
        self,
        model_path: str = "assets/models/hand_landmarker.task",
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.5,
        min_presence_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        self.max_num_hands = max_num_hands
        self.timestamp_ms = 0

        # MediaPipe Tasks API
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarkerOptions = (
            mp.tasks.vision.HandLandmarkerOptions
        )
        HandLandmarker = (
            mp.tasks.vision.HandLandmarker
        )
        RunningMode = (
            mp.tasks.vision.RunningMode
        )

        base_options = BaseOptions(
            model_asset_path=model_path
        )

        options = HandLandmarkerOptions(
            base_options=base_options,
            running_mode=RunningMode.VIDEO,
            num_hands=max_num_hands,
            min_hand_detection_confidence=(
                min_detection_confidence
            ),
            min_hand_presence_confidence=(
                min_presence_confidence
            ),
            min_tracking_confidence=(
                min_tracking_confidence
            ),
        )

        self.detector = (
            HandLandmarker.create_from_options(
                options
            )
        )

        self.hand_connections = (
            mp.tasks.vision
            .HandLandmarksConnections
            .HAND_CONNECTIONS
        )

    # --------------------------------
    # Extract landmarks + handedness
    # --------------------------------

    def extract_landmarks(self, results):
        hands = []

        for index, hand_landmarks in enumerate(
            results.hand_landmarks
        ):
            points = [
                Landmark(
                    x=landmark.x,
                    y=landmark.y,
                    z=landmark.z,
                )
                for landmark in hand_landmarks
            ]

            handedness = "Unknown"

            if (
                index < len(results.handedness)
                and results.handedness[index]
            ):
                category = (
                    results.handedness[index][0]
                )

                if getattr(
                    category,
                    "category_name",
                    None,
                ):
                    handedness = (
                        category.category_name
                    )
                elif getattr(
                    category,
                    "display_name",
                    None,
                ):
                    handedness = (
                        category.display_name
                    )

            hands.append(
                HandLandmarks(
                    points=points,
                    handedness=handedness,
                )
            )

        return hands

    # --------------------------------
    # Process frame
    # --------------------------------

    def process(self, frame):
        """
        Process one OpenCV BGR frame and return
        MediaPipe HandLandmarkerResult.
        """

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        mp_image = mp.Image(
            image_format=(
                mp.ImageFormat.SRGB
            ),
            data=rgb_frame,
        )

        self.timestamp_ms += 33

        results = (
            self.detector.detect_for_video(
                mp_image,
                self.timestamp_ms,
            )
        )

        return results

    # --------------------------------
    # Draw star
    # --------------------------------

    def draw_star(
        self,
        frame,
        center,
        outer_radius,
        color,
    ):
        cx, cy = center
        points = []

        for i in range(10):
            angle = (
                -math.pi / 2
                + i * math.pi / 5
            )

            if i % 2 == 0:
                radius = outer_radius
            else:
                radius = (
                    outer_radius * 0.45
                )

            x = int(
                cx
                + radius * math.cos(angle)
            )

            y = int(
                cy
                + radius * math.sin(angle)
            )

            points.append(
                (x, y)
            )

        points = np.array(
            points,
            dtype=np.int32,
        )

        cv2.fillPoly(
            frame,
            [points],
            color,
        )

    # --------------------------------
    # Draw landmarks
    # --------------------------------

    def draw_landmarks(
        self,
        frame,
        results,
    ):
        height, width, _ = frame.shape

        # OpenCV uses BGR.
        pink = (
            180,
            80,
            255,
        )

        purple = (
            255,
            0,
            190,
        )

        for hand_landmarks in (
            results.hand_landmarks
        ):

            # --------------------------------
            # Pink skeleton
            # --------------------------------

            for connection in (
                self.hand_connections
            ):
                start = hand_landmarks[
                    connection.start
                ]

                end = hand_landmarks[
                    connection.end
                ]

                start_point = (
                    int(start.x * width),
                    int(start.y * height),
                )

                end_point = (
                    int(end.x * width),
                    int(end.y * height),
                )

                cv2.line(
                    frame,
                    start_point,
                    end_point,
                    pink,
                    1,
                    cv2.LINE_AA,
                )

            # --------------------------------
            # Purple star landmarks
            # --------------------------------

            for landmark in hand_landmarks:
                point = (
                    int(
                        landmark.x * width
                    ),
                    int(
                        landmark.y * height
                    ),
                )

                self.draw_star(
                    frame,
                    point,
                    6,
                    purple,
                )

        return frame

    def close(self):
        self.detector.close()