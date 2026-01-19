# src/detector.py

from ultralytics import YOLO
from config.settings import DEVICE, CONFIDENCE_THRESHOLD

class Detector:
    def __init__(self, model_path="models/yolov8n.pt", device=DEVICE):
        self.model = YOLO(model_path)
        self.device = device

    def detect_people(self, frame):
        """
        Detect people in a single frame.
        Args:
            frame (ndarray): input image
        Returns:
            person_boxes (list of tuples): [ (x1, y1, x2, y2, confidence), ... ]
        """
        results = self.model(frame, device=self.device, conf=CONFIDENCE_THRESHOLD)
        person_boxes = []

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                if cls == 0:  # class 0 = person
                    x1, y1, x2, y2 = box.xyxy[0]
                    conf = float(box.conf[0])
                    person_boxes.append((x1, y1, x2, y2, conf))

        return person_boxes
