# power_manager.py
import threading
import os
import subprocess
import json

SETTINGS_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen/settings.json"
sleep_timer = None

# Automatically detect backlight path
def detect_backlight_path():
    base = "/sys/class/backlight"
    if not os.path.exists(base):
        return None
    for entry in os.listdir(base):
        candidate = os.path.join(base, entry, "bl_power")
        if os.path.exists(candidate):
            return candidate
    return None

BACKLIGHT_PATH = detect_backlight_path()

def write_backlight(value):
    if BACKLIGHT_PATH:
        try:
            with open(BACKLIGHT_PATH, "w") as f:
                f.write(str(value))
        except PermissionError:
            subprocess.call(['sudo', 'sh', '-c', f'echo {value} > {BACKLIGHT_PATH}'])

def turn_screen_off():
    write_backlight(1)

def turn_screen_on():
    write_backlight(0)

def load_screen_timeout():
    try:
        with open(SETTINGS_PATH, "r") as f:
            settings = json.load(f)
            return int(settings.get("screen_timeout", 120))
    except:
        return 120

def stop_idle_timer():
    global sleep_timer
    if sleep_timer:
        sleep_timer.cancel()
        sleep_timer = None

def reset_idle_timer():
    global sleep_timer
    if sleep_timer:
        sleep_timer.cancel()
    turn_screen_on()
        
    # Live-load screen timeout
    timeout = load_screen_timeout()
    sleep_timer = threading.Timer(timeout, turn_screen_off)
    sleep_timer.start()