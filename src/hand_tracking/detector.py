import cv2
import math
import mediapipe as mp
import numpy as np

from hand_tracking.landmarks import Landmark, HandLandmarks


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
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        RunningMode = mp.tasks.vision.RunningMode

        base_options = BaseOptions(
            model_asset_path=model_path
        )

        options = HandLandmarkerOptions(
            base_options=base_options,
            running_mode=RunningMode.VIDEO,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_presence_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

        self.detector = HandLandmarker.create_from_options(options)

        # Hand connection definitions
        self.hand_connections = (
            mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS
        )

    def extract_landmarks(self, results):
        hands = []

        for hand_landmarks in results.hand_landmarks:
            points = [
                Landmark(
                    x=landmark.x,
                    y=landmark.y,
                    z=landmark.z,
                )
                for landmark in hand_landmarks
            ]

            hands.append(HandLandmarks(points))

        return hands

    def process(self, frame):
        """
        Process one OpenCV BGR frame and return
        MediaPipe HandLandmarkerResult.
        """

        # OpenCV → RGB
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        # RGB numpy array → MediaPipe Image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        # VIDEO mode requires monotonically increasing timestamps.
        self.timestamp_ms += 33

        results = self.detector.detect_for_video(
            mp_image,
            self.timestamp_ms,
        )

        return results

    def draw_star(
        self,
        frame,
        center,
        outer_radius,
        color,
    ):
        """
        Draw a filled 5-point star.
        """

        cx, cy = center
        points = []

        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5

            if i % 2 == 0:
                radius = outer_radius
            else:
                radius = outer_radius * 0.45

            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle))

            points.append((x, y))

        points = np.array(points, dtype=np.int32)

        cv2.fillPoly(
            frame,
            [points],
            color,
        )

    def draw_landmarks(self, frame, results):
        """
        Draw detected hand landmarks and connections
        onto the OpenCV frame.
        """

        height, width, _ = frame.shape

        # Colors are written in OpenCV BGR format.
        white = (255, 255, 255)
        purple = (255, 0, 190)

        for hand_landmarks in results.hand_landmarks:

            # -----------------------------
            # Draw pink connections
            # -----------------------------

            for connection in self.hand_connections:
                start = hand_landmarks[connection.start]
                end = hand_landmarks[connection.end]

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
                    white,
                    1,
                    cv2.LINE_AA,
                )

            # -----------------------------
            # Draw purple landmarks
            # -----------------------------

            for landmark in hand_landmarks:
                point = (
                    int(landmark.x * width),
                    int(landmark.y * height),
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