# update_reboot_schedule.py
import json
import subprocess
import os

# Absolute paths
PROJECT_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen"
SETTINGS_PATH = os.path.join(PROJECT_PATH, "settings.json")
HANDLER_PATH = os.path.join(PROJECT_PATH, "auto_reboot_handler.py")
PYTHON_PATH = "/usr/bin/python3" 

def get_cron_time(day, time):
    days_map = {
        'sun': 0, 'mon': 1, 'tue': 2,
        'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6
    }
    day = day[:3].lower()
    hour, minute = map(int, time.split(":"))
    dow = days_map.get(day, 0)
    return f"{minute} {hour} * * {dow}"

def update_crontab(enabled, cron_line):
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout.splitlines() if result.returncode == 0 else []
    except Exception:
        current_cron = []

    updated_cron = [line for line in current_cron if "auto_reboot_handler.py" not in line]

    if enabled:
        updated_cron.append(cron_line)

    new_crontab = '\n'.join(updated_cron) + '\n'
    subprocess.run(['crontab', '-'], input=new_crontab, text=True)

def main():
    if not os.path.exists(SETTINGS_PATH):
        print(f"[ERROR] Settings file not found at: {SETTINGS_PATH}")
        return

    with open(SETTINGS_PATH, "r") as f:
        settings = json.load(f)

    enabled = settings.get("reboot_enabled", False)
    day = settings.get("reboot_day", "sun")
    time = settings.get("reboot_time", "03:00")

    cron_expr = get_cron_time(day, time)
    cron_line = f"{cron_expr} {PYTHON_PATH} {HANDLER_PATH}"
    update_crontab(enabled, cron_line)

if __name__ == "__main__":
    main()
