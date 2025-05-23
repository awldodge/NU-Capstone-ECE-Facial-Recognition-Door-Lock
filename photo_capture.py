#photo_capture.py
import os
import cv2
from datetime import datetime
from picamera2 import Picamera2
import time

def capture_face_photos(name):
    folder = os.path.join("dataset", name)
    os.makedirs(folder, exist_ok=True)

    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam2.start()
    time.sleep(2)

    photo_count = 0
    while True:
        frame = picam2.capture_array()
        cv2.imshow("Capture", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(" "):
            photo_count += 1
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(os.path.join(folder, f"{name}_{ts}.jpg"), frame)
            print(f"Saved {photo_count} photo(s) for {name}")
        elif key == ord("q"):
            break

    picam2.stop()
    cv2.destroyAllWindows()
