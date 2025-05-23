#reboot_schedule_screen.py
import tkinter as tk
import json
import subprocess
from datetime import datetime
import csv

SETTINGS_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen/settings.json"
LOG_FILE = "settings_log.csv"

def log_schedule_change(day, time):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, "System", f"Auto Reboot changed to {day.capitalize()} at {time}"])

def show_screen(root, return_callback):
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="black")

    try:
        with open(SETTINGS_PATH, "r") as f:
            settings = json.load(f)
            current_day = settings.get("reboot_day", "sun")
            current_time = settings.get("reboot_time", "03:00")
    except:
        current_day = "sun"
        current_time = "03:00"

    # Title
    tk.Label(root, text="Edit Reboot Schedule Screen", font=("Helvetica", 32, "bold"),
             fg="white", bg="black").pack(pady=(25, 15))

    form_frame = tk.Frame(root, bg="black")
    form_frame.pack(pady=25)

    # Day dropdown
    tk.Label(form_frame, text="Day of Week:", font=("Helvetica", 22), fg="white", bg="black").grid(row=0, column=0, pady=20, padx=10, sticky="e")
    day_options = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    day_var = tk.StringVar(value=current_day.capitalize())
    day_menu = tk.OptionMenu(form_frame, day_var, *day_options)
    day_menu.config(font=("Helvetica", 22), width=10, bg="white", fg="black", bd=4, highlightthickness=2)
    day_menu["menu"].config(font=("Helvetica", 22))
    day_menu.grid(row=0, column=1, pady=20, padx=10)

    # Time spinboxes
    tk.Label(form_frame, text="Time (24-hour):", font=("Helvetica", 22), fg="white", bg="black").grid(row=1, column=0, pady=20, padx=10, sticky="e")
    hh, mm = current_time.split(":")
    hour_var = tk.StringVar(value=hh.zfill(2))
    minute_var = tk.StringVar(value=mm.zfill(2))

    time_frame = tk.Frame(form_frame, bg="black")
    time_frame.grid(row=1, column=1, pady=15)

    hour_spin = tk.Spinbox(time_frame, from_=0, to=23, wrap=True, textvariable=hour_var,
                           font=("Helvetica", 22), width=4, format="%02.0f", justify="center", bd=4)
    hour_spin.grid(row=0, column=0, padx=(0, 20))

    minute_spin = tk.Spinbox(time_frame, values=("00", "15", "30", "45"), textvariable=minute_var,
                             font=("Helvetica", 22), width=4, justify="center", bd=4)
    minute_spin.grid(row=0, column=1, padx=(20, 0))

    status_label = tk.Label(root, text="", font=("Helvetica", 16, "bold"), fg="red", bg="black")
    status_label.pack(pady=(5, 15))

    def save_schedule():
        day = day_var.get().strip()
        hour = hour_var.get().zfill(2)
        minute = minute_var.get().zfill(2)
        time = f"{hour}:{minute}"

        try:
            assert day.lower()[:3] in ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']

            with open(SETTINGS_PATH, "r+") as f:
                settings = json.load(f)
                settings["reboot_day"] = day.lower()
                settings["reboot_time"] = time
                f.seek(0)
                json.dump(settings, f, indent=4)
                f.truncate()
            subprocess.run(["sudo", "python3", "/home/awldodge/CEE499_Capstone/Touchscreen/update_reboot_schedule.py"])
            log_schedule_change(day, time)
            return_callback()

        except Exception as e:
            status_label.config(text=f"Error: {e}", fg="red")

    # Buttons
    button_frame = tk.Frame(root, bg="black")
    button_frame.pack(pady=(10,10))

    tk.Button(button_frame, text="Save Schedule &\nReturn to Reboot Control Screen", command=save_schedule,
              font=("Helvetica", 20, "bold"), fg="white", bg="#00cc44",
              activebackground="#009933", width=20, height=3, wraplength=300, justify="center").grid(row=0, column=0, padx=30)

    tk.Button(button_frame, text="Cancel &\nReturn to Reboot Control Screen", command=return_callback,
              font=("Helvetica", 20, "bold"), fg="white", bg="gray",
              activebackground="#555555", width=20, height=3, wraplength=300, justify="center").grid(row=0, column=1, padx=30)
