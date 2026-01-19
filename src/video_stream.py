# src/video_stream.py (updated)

import cv2
from config.settings import IP_CAMERA_URL

class VideoStream:
    def __init__(self, url=IP_CAMERA_URL, width=480, height=640):
        self.url = url
        self.cap = cv2.VideoCapture(self.url)
        if not self.cap.isOpened():
            raise ValueError(f"Unable to open video stream: {self.url}")
        self.width = width
        self.height = height

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return False, None
        # Resize frame to reduce computation
        frame = cv2.resize(frame, (self.width, self.height))
        return True, frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
