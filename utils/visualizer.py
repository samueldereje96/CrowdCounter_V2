import cv2
import numpy as np

def draw_boxes(frame, boxes):
    """
    Draw bounding boxes and confidence on the frame
    Args:
        frame (ndarray): the image
        boxes (list of tuples): (x1, y1, x2, y2, conf)
    """
    for x1, y1, x2, y2, conf in boxes:
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, f"{conf:.2f}", (int(x1), int(y1)-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


def draw_occupancy(frame, avg_occupancy, temperature, ac_on, limit_exceeded=False, current_count=None):
    """
    Draw a visually enhanced side strip with occupancy info, temperature, and AC status
    """
    # Dimensions
    frame_h, frame_w = frame.shape[:2]
    strip_w = 350  # wider strip for nicer layout

    # Create new frame with side strip
    new_frame = np.zeros((frame_h, frame_w + strip_w, 3), dtype=np.uint8)
    new_frame[:, :frame_w] = frame  # copy original video frame

    #Draw a gradient background for strip
    for i in range(frame_h):
        color = (50 + i//10, 50 + i//10, 100)  # subtle gradient
        cv2.line(new_frame, (frame_w, i), (frame_w + strip_w, i), color, 1)

    # Box settings
    box_w, box_h = strip_w - 40, 60
    x0 = frame_w + 20
    y0 = 30
    spacing = 80

    # Draw info boxes
    metrics = [
        ("Current Count", current_count, (0, 255, 0)),
        ("Avg Occupancy", f"{avg_occupancy:.1f}", (0, 200, 255)),
        ("Max Limit Exceeded", "YES" if limit_exceeded else "NO", (0, 0, 255) if limit_exceeded else (0, 255, 0)),
        ("Temperature", f"{temperature:.1f}C", (255, 100, 0)),
        ("AC State", "ON" if ac_on else "OFF", (0, 0, 255) if ac_on else (0, 255, 0))
    ]

    for i, (label, value, color) in enumerate(metrics):
        top_left = (x0, y0 + i*spacing)
        bottom_right = (x0 + box_w, y0 + i*spacing + box_h)
        cv2.rectangle(new_frame, top_left, bottom_right, color, -1)  # filled box
        cv2.putText(new_frame, f"{label}: {value}", (x0 + 10, y0 + i*spacing + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return new_frame