#camera_handler.py
from picamera2 import Picamera2
import time

_camera_instance = None

def get_camera():
    global _camera_instance
    if _camera_instance is None:
        _camera_instance = Picamera2()
        _camera_instance.configure(_camera_instance.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
        _camera_instance.start()
        time.sleep(2)  # Allow camera to warm up
    return _camera_instance


