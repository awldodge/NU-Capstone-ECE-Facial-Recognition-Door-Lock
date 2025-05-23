#camera_manager.py
from picamera2 import Picamera2
import threading

_camera_instance = None
_camera_lock = threading.Lock()

def get_camera():
    global _camera_instance
    if _camera_instance is None:
        _camera_instance = Picamera2()
        _camera_instance.configure(
            _camera_instance.create_preview_configuration(
                main={"format": "RGB888", "size": (640, 480)}
            )
        )
        _camera_instance.start()
    return _camera_instance

def get_camera_lock():
    return _camera_lock

def release_camera():
    global _camera_instance
    if _camera_instance:
        try:
            _camera_instance.stop()
        except:
            pass
        try:
            _camera_instance.close()
        except:
            pass
        _camera_instance = None

def safe_reset_camera():
    release_camera()
    return get_camera()

def get_frame():
    with get_camera_lock():
        camera = get_camera()
        return camera.capture_array()
