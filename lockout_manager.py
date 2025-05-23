# lockout_manager.py
import json
import os
import time

SETTINGS_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen/settings.json"

def load_lockout_state(pin_type):
    """Returns (failed_attempts, lockout_end_time) for the given pin_type."""
    try:
        with open(SETTINGS_PATH, "r") as f:
            settings = json.load(f)
            lockout = settings.get("lockout", {}).get(pin_type, {})
            return (
                lockout.get("failed_attempts", 0),
                lockout.get("lockout_end_time", 0)
            )
    except:
        return (0, 0)

def save_lockout_state(pin_type, failed_attempts, lockout_end_time):
    """Saves failed_attempts and lockout_end_time for the given pin_type."""
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                settings = json.load(f)
        else:
            settings = {}

        if "lockout" not in settings:
            settings["lockout"] = {}

        settings["lockout"][pin_type] = {
            "failed_attempts": failed_attempts,
            "lockout_end_time": lockout_end_time
        }

        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"[Error] Failed to save lockout state: {e}")

def clear_lockout_state(pin_type):
    """Resets the failed attempts and lockout time for the given pin_type."""
    save_lockout_state(pin_type, 0, 0)
