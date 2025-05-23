# reboot_control_screen.py
import tkinter as tk
import json
import subprocess
import threading
import time
import reboot_schedule_screen
from reboot_utility import perform_full_reboot
from datetime import datetime
import csv

SETTINGS_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen/settings.json"

def log_reboot_toggle(enabled):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state = "ENABLED" if enabled else "DISABLED"
    with open("settings_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, "System", f"Auto Reboot {state}"])

def show_screen(root, go_back_callback):
    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg="black")

    try:
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
            current_day = settings.get("reboot_day", "Sun").capitalize()
            current_time = settings.get("reboot_time", "03:00")
            enabled = settings.get("reboot_enabled", False)
    except:
        current_day = "Sun"
        current_time = "03:00"
        enabled = False

    tk.Label(root, text="Reboot Control Screen", font=("Helvetica", 28, "bold"), fg="white", bg="black").pack(pady=10)

    schedule_label = tk.Label(root, text=f"Current Auto Reboot Schedule: {current_day} at {current_time}",
                              font=("Helvetica", 14, "bold"), fg="#00ffcc", bg="black")
    schedule_label.pack(pady=(5, 0))

    status_label = tk.Label(root, text=f"Auto Reboot is currently {'ENABLED' if enabled else 'DISABLED'}",
                            font=("Helvetica", 12, "bold"), fg="green" if enabled else "red", bg="black")
    status_label.pack(pady=(0, 10))

    countdown_label = tk.Label(root, text="", font=("Helvetica", 20, "bold"), fg="red", bg="black")
    countdown_label.pack(pady=10)

    cancel_button = tk.Button(root, text="Cancel Manual Reboot", font=("Helvetica", 16, "bold"),
                              fg="white", bg="red", width=25, height=2)
    cancel_button.pack_forget()

    cancel_flag = [False]

    def toggle_reboot():
        try:
            with open(SETTINGS_PATH, 'r+') as f:
                settings = json.load(f)
                current_state = settings.get('reboot_enabled', False)
                settings['reboot_enabled'] = not current_state
                log_reboot_toggle(settings['reboot_enabled'])
                f.seek(0)
                json.dump(settings, f, indent=4)
                f.truncate()

            subprocess.run(['sudo', 'python3', '/home/awldodge/CEE499_Capstone/Touchscreen/update_reboot_schedule.py'])

            status_label.config(text=f"Auto Reboot is currently {'ENABLED' if settings['reboot_enabled'] else 'DISABLED'}",
                                fg="green" if settings['reboot_enabled'] else "red")
            schedule_label.config(text=f"Current Auto Reboot Schedule: {settings['reboot_day'].capitalize()} at {settings['reboot_time']}")

        except Exception as e:
            status_label.config(text=f"Error: {e}", fg="red")

    def cancel_reboot():
        cancel_flag[0] = True
        cancel_button.pack_forget()
        countdown_label.config(text="")
        show_screen(root, go_back_callback)

    def reboot_now():
        def countdown_and_reboot():
            for i in range(10, 0, -1):
                if cancel_flag[0]:
                    return
                countdown_label.config(text=f"Rebooting in {i} seconds...")
                time.sleep(1)
            countdown_label.config(text="Rebooting now...", fg="red")
            root.update()
            perform_full_reboot("Manual")

        cancel_flag[0] = False
        cancel_button.pack(pady=10)
        cancel_button.config(command=cancel_reboot)
        threading.Thread(target=countdown_and_reboot, daemon=True).start()

    # Button styles
    yellow_button = {"font": ("Helvetica", 14, "bold"), "fg": "black", "bg": "yellow",
                     "activebackground": "#cccc00", "bd": 0, "highlightthickness": 0, "relief": "flat"}
    blue_button = {"font": ("Helvetica", 14, "bold"), "fg": "white", "bg": "#00aaff",
                   "activebackground": "#0077cc", "bd": 0, "highlightthickness": 0, "relief": "flat"}
    red_button = {"font": ("Helvetica", 14, "bold"), "fg": "black", "bg": "#ff3333",
                  "activebackground": "#cc0000", "bd": 0, "highlightthickness": 0, "relief": "flat"}
    green_button = {"font": ("Helvetica", 14, "bold"), "fg": "white", "bg": "#00cc44",
                    "activebackground": "#009933", "bd": 0, "highlightthickness": 0, "relief": "flat"}

    grid_frame = tk.Frame(root, bg="black")
    grid_frame.pack(pady=10)

    tk.Button(grid_frame, text="Enable / Disable Auto Reboot", command=toggle_reboot, wraplength=160, justify="center",
              width=24, height=3, **yellow_button).grid(row=0, column=0, padx=10, pady=10)
    tk.Button(grid_frame, text="Change Reboot Schedule",
              command=lambda: reboot_schedule_screen.show_screen(root, lambda: show_screen(root, go_back_callback)),
              width=24, height=3, **blue_button).grid(row=0, column=1, padx=10, pady=10)
    tk.Button(grid_frame, text="Reboot Now", command=reboot_now,
              width=24, height=3, **red_button).grid(row=1, column=0, padx=10, pady=10)
    tk.Button(grid_frame, text="Return to Settings Screen", command=go_back_callback,
              width=24, height=3, **green_button).grid(row=1, column=1, padx=10, pady=10)
