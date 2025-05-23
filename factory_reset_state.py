#factory_reset_state
import tkinter as tk

# Shared toggle state between pages
_toggles = None

def get_toggles():
    global _toggles
    if _toggles is None:
        _toggles = {
            "faces": tk.BooleanVar(value=False),
            "door_pin": tk.BooleanVar(value=False),
            "admin_pin": tk.BooleanVar(value=False),
            "access_log": tk.BooleanVar(value=False),
            "settings_log": tk.BooleanVar(value=False),
            "unlock_time": tk.BooleanVar(value=False),
            "lockout_time": tk.BooleanVar(value=False),
            "face_cooldown": tk.BooleanVar(value=False),
            "touch_timeout": tk.BooleanVar(value=False),
            "reboot_day_time": tk.BooleanVar(value=False),
        }
    return _toggles

