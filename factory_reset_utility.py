#factory_reset_utility.py

import os
import json
import hashlib
from datetime import datetime

SETTINGS_LOG = "settings_log.csv"
SETTINGS_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen/settings.json"

DOOR_PIN_PATH = "/home/awldodge/.config/doorlock/door_pin.txt"
ADMIN_PIN_PATH = "/home/awldodge/.config/doorlock/admin_pin.txt"

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def log_settings_change(action, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SETTINGS_LOG, "a") as f:
        f.write(f"{timestamp},{action},{message}\n")

def delete_registered_faces():
    try:
        folder = "known_faces"
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            log_settings_change("Face Reset", "Deleted all registered faces")
    except Exception as e:
        log_settings_change("Face Reset", f"Error deleting faces: {e}")

def reset_door_pin():
    try:
        factory_pin = "1234"
        hashed = hash_pin(factory_pin)

        os.makedirs(os.path.dirname(DOOR_PIN_PATH), exist_ok=True)
        with open(DOOR_PIN_PATH, "w") as f:
            f.write(hashed)

        # Ensure settings.json is updated safely
        settings = {}
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                try:
                    settings = json.load(f)
                except:
                    settings = {}

        settings["door_pin"] = factory_pin

        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=4)

        log_settings_change("Door PIN Reset", f"Reset to factory PIN: {factory_pin}")
    except Exception as e:
        log_settings_change("Door PIN Reset", f"Error: {e}")

def reset_admin_pin():
    try:
        factory_pin = "654321"
        hashed = hash_pin(factory_pin)

        os.makedirs(os.path.dirname(ADMIN_PIN_PATH), exist_ok=True)
        with open(ADMIN_PIN_PATH, "w") as f:
            f.write(hashed)

        # Ensure settings.json is updated safely
        settings = {}
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                try:
                    settings = json.load(f)
                except:
                    settings = {}

        settings["admin_pin"] = factory_pin

        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=4)

        log_settings_change("Admin PIN Reset", f"Reset to factory PIN: {factory_pin}")
    except Exception as e:
        log_settings_change("Admin PIN Reset", f"Error: {e}")

def clear_log(file_path, label):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        log_settings_change(f"{label} Reset", "Cleared log")
    except Exception as e:
        log_settings_change(f"{label} Reset", f"Error: {e}")
