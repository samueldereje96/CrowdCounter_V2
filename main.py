from data.db import log_to_db
from src.video_stream import VideoStream
from src.detector import Detector
from src.counter import OccupancyCounter
from utils.visualizer import draw_boxes, draw_occupancy
from config.settings import WEBHOOK_URL
import cv2
import requests
import time

# Configuration
SEND_INTERVAL = 10  # seconds between sending/logging
skip_frames = 5     # detect every 5 frames
BASE_TEMPERATURE = 22.0
TEMPERATURE_CHANGE_RATE = 0.1  # how quickly temp adjusts
AC_THRESHOLD = 23.5  # temperature threshold for AC
temperature = [BASE_TEMPERATURE]  # mutable for loop
last_sent_time = [time.time()]
counts_buffer = []

def send_to_n8n(avg_occ, max_occ, current_count, limit_exceeded, temperature, ac_on):
    data = {
        "avg_occupancy": avg_occ,
        "max_occupancy": max_occ,
        "current_count": current_count,
        "limit_exceeded": limit_exceeded,
        "temperature": temperature,
        "ac_on": ac_on
    }
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=0.5)
        if response.status_code != 200:
            print("Webhook response:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Failed to send to n8n:", e)

def main():
    stream = VideoStream(width=640, height=480)
    detector = Detector()
    counter = OccupancyCounter(window_size=10)
    print("Starting video stream with occupancy counter. Press 'q' to quit.")

    frame_count = 0
    boxes = []

    while True:
        ret, frame = stream.read_frame()
        if not ret:
            break

        frame_count += 1

        # Detect people every 'skip_frames'
        if frame_count % skip_frames == 0:
            boxes = detector.detect_people(frame)
            counter.update(len(boxes))

        avg_occupancy = counter.get_average()
        current_count = len(boxes)
        limit_exceeded = counter.is_over_limit()

        counts_buffer.append(current_count)

        # Simulate temperature
        target_temp = BASE_TEMPERATURE + 0.5 * current_count
        temperature[0] += (target_temp - temperature[0]) * TEMPERATURE_CHANGE_RATE

        # Determine AC state
        ac_on = temperature[0] > AC_THRESHOLD

        # Send/log every SEND_INTERVAL
        if time.time() - last_sent_time[0] >= SEND_INTERVAL:
            avg_occ = sum(counts_buffer) / len(counts_buffer)
            max_occ = max(counts_buffer)

            # Send to n8n
            send_to_n8n(
                avg_occ,
                max_occ,
                current_count,
                limit_exceeded,
                temperature[0],
                ac_on
            )

            # Log to SQLite
            log_to_db(
                current_count=current_count,
                avg_occupancy=avg_occ,
                max_occupancy=max_occ,
                temperature=temperature[0],
                limit_exceeded=limit_exceeded
            )

            counts_buffer.clear()
            last_sent_time[0] = time.time()

        # Draw on frame
        draw_boxes(frame, boxes)
        frame = draw_occupancy(frame, avg_occupancy, temperature[0], ac_on, limit_exceeded, current_count=len(boxes))
        cv2.imshow("Crowd Counter", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stream.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
