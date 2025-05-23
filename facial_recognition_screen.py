# facial_recognition_screen.py
import cv2
import face_recognition
import os
import numpy as np
from threading import Thread
import time
import access_log
import door_lock
from camera_manager import get_camera_lock
import json

FACES_DIR = "/home/awldodge/known_faces"
SETTINGS_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen/settings.json"
DEFAULT_UNLOCK_TIME = 15
DEFAULT_LOCK_TIME = 5
DEFAULT_FACE_COOLDOWN = 0

# Globals
monitoring = False
cooldown_active = False
camera_thread = None
ui_controller = None
latest_frame = None
camera = None

def set_camera(cam):
    global camera
    camera = cam

def get_camera_instance():
    return camera

def set_ui_controller(ui_ref):
    global ui_controller
    ui_controller = ui_ref

def update_latest_frame(frame):
    global latest_frame
    latest_frame = frame

def set_cooldown_active(state):
    global cooldown_active
    cooldown_active = state

def is_cooldown_active():
    return cooldown_active

def load_known_faces():
    known_encodings = []
    known_names = []

    for filename in os.listdir(FACES_DIR):
        if filename.endswith(".npy"):
            encoding = np.load(os.path.join(FACES_DIR, filename))
            name = os.path.splitext(filename)[0]
            known_encodings.append(encoding)
            known_names.append(name)

    return known_encodings, known_names

def load_unlock_lock_times():
    if not os.path.exists(SETTINGS_PATH):
        return DEFAULT_UNLOCK_TIME, DEFAULT_LOCK_TIME
    try:
        with open(SETTINGS_PATH, "r") as f:
            settings = json.load(f)
            unlock_time = settings.get("unlock_time", DEFAULT_UNLOCK_TIME)
            lock_time = settings.get("lock_time", DEFAULT_LOCK_TIME)
            return unlock_time, lock_time
    except Exception as e:
        print(f"[Warning] Failed to load unlock/lock times: {e}")
        return DEFAULT_UNLOCK_TIME, DEFAULT_LOCK_TIME

def load_face_cooldown():
    if not os.path.exists(SETTINGS_PATH):
        return DEFAULT_FACE_COOLDOWN
    try:
        with open(SETTINGS_PATH, "r") as f:
            settings = json.load(f)
            return settings.get("face_cooldown", DEFAULT_FACE_COOLDOWN)
    except Exception as e:
        print(f"[Warning] Failed to load face_cooldown: {e}")
        return DEFAULT_FACE_COOLDOWN

def start_monitoring():
    global monitoring, camera_thread
    if monitoring:
        return
    if cooldown_active:
        return
    monitoring = True
    camera_thread = Thread(target=camera_loop, daemon=True)
    camera_thread.start()

def stop_monitoring():
    global monitoring
    monitoring = False

def pause_monitoring():
    stop_monitoring()

def camera_loop():
    global monitoring
    lock = get_camera_lock()
    with lock:
        known_encodings, known_names = load_known_faces()
        last_reload_time = time.time()
        reload_interval = 10  # seconds

        while monitoring:
            if not ui_controller or not ui_controller.monitoring_enabled:
                time.sleep(0.1)
                continue
            if latest_frame is None or cooldown_active:
                time.sleep(0.05)
                continue
            if time.time() - last_reload_time > reload_interval:
                known_encodings, known_names = load_known_faces()
                last_reload_time = time.time()

            frame = latest_frame.copy()

            if frame.shape[2] == 1:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            elif frame.shape[2] == 4:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
            else:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_frame, model="hog")
            if not face_locations:
                continue

            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)

                name = "Unknown"
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_names[best_match_index]

                if name == "Unknown":
                    print("[INFO] Unrecognized face detected.")
                    if ui_controller:
                        try:
                            if ui_controller.face_detected_label and ui_controller.face_detected_label.winfo_exists():
                                ui_controller.show_face_detected()
                        except Exception as e:
                            print(f"[UI] Warning during face detected indicator: {e}")
                else:
                    print(f"[INFO] Recognized face: {name}")
                    access_log.log_access("Face", name)
                    unlock_time, _ = load_unlock_lock_times()
                    door_lock.unlock_door(unlock_time)
                    ui_controller.show_unlock_screen(name)
                    time.sleep(unlock_time)
                    ui_controller.show_lock_screen()
                    time.sleep(5)
                    break

    #Restart logic after unlock
    if ui_controller and ui_controller.monitoring_enabled:
        cooldown = load_face_cooldown()
        pause_monitoring()
        set_cooldown_active(True)

        def delayed_restart():
            if ui_controller and ui_controller.monitoring_enabled:
                set_cooldown_active(False)
                start_monitoring()
            else:
                print("[DEBUG] Cooldown complete, but monitoring disabled")

        try:
            ui_controller.root.after(cooldown * 1000, delayed_restart)
        except Exception:
            time.sleep(cooldown)
            delayed_restart()
    else:
        pause_monitoring()
        set_cooldown_active(False)
