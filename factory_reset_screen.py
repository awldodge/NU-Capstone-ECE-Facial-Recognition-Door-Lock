# factory_reset_screen.py 
import tkinter as tk
from tkinter import messagebox
import json
import os

from factory_reset_utility import (
    delete_registered_faces, reset_door_pin, reset_admin_pin,
    clear_log, log_settings_change
)
from factory_reset_state import get_toggles

SETTINGS_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen/settings.json"
FACES_DIR = "/home/awldodge/known_faces"

def load_settings():
    try:
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    except:
        return {}

def save_settings(data):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(data, f, indent=4)

def clear_all_toggles(toggles):
    for var in toggles.values():
        var.set(False)

def reset_all_selected_values(root, toggles, go_back_callback):
    confirm = messagebox.askyesno("Confirm Factory Reset", 
                                  "Are you sure you want to reset all selected values to factory defaults?")
    if not confirm:
        return

    settings_data = load_settings()
    any_reset = False

    if toggles["faces"].get():
        delete_registered_faces()
        any_reset = True

    if toggles["door_pin"].get():
        reset_door_pin()
        settings_data["door_pin"] = "1234"
        any_reset = True

    if toggles["admin_pin"].get():
        reset_admin_pin()
        settings_data["admin_pin"] = "654321"
        any_reset = True

    if toggles["access_log"].get():
        clear_log("access_log.csv", "Access Log")
        any_reset = True

    if toggles["settings_log"].get():
        clear_log("settings_log.csv", "Settings Log")
        any_reset = True

    if toggles["unlock_time"].get():
        settings_data["unlock_time"] = 15
        log_settings_change("Unlock Time", "Reset to factory 15 seconds")
        any_reset = True

    if toggles["lockout_time"].get():
        settings_data["lockout_time"] = 30
        log_settings_change("Lockout Time", "Reset to factory 30 seconds")
        any_reset = True

    if toggles["face_cooldown"].get():
        settings_data["face_cooldown"] = 5
        log_settings_change("Face Cooldown", "Reset to factory 5 seconds")
        any_reset = True

    if toggles["touch_timeout"].get():
        settings_data["screen_timeout"] = 120
        log_settings_change("Screen Timeout", "Reset to factory 120 seconds")
        any_reset = True

    if toggles["reboot_day_time"].get():
        settings_data["reboot_day"] = "sun"
        settings_data["reboot_time"] = "03:00"
        settings_data["reboot_enabled"] = True
        log_settings_change("Reboot Schedule Reset", "Reset to Sunday @ 03:00")
        any_reset = True

    if any_reset:
        save_settings(settings_data)
        messagebox.showinfo("Factory Reset", "Selected values restored to factory defaults.")

    clear_all_toggles(toggles)
    root.after(100, go_back_callback)  #returns to Settings Screen

def show_page_1(root, go_back_callback, toggles):
    settings_data = load_settings()
    door_pin = settings_data.get("door_pin", "1234")
    admin_pin = settings_data.get("admin_pin", "654321")
    try:
        face_count = len([f for f in os.listdir(FACES_DIR) if f.lower().endswith(('.npy', '.jpg', '.png'))])
    except:
        face_count = 0
    face_display = f"{face_count} Registered Face{'s' if face_count != 1 else ''}"

    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg="black")

    def go_back_and_clear():
        clear_all_toggles(toggles)
        go_back_callback()

    def create_title():
        tk.Label(root, text="Factory Reset Screen Pg: 1",
                 font=("Helvetica", 20, "bold"), fg="white", bg="black").pack(pady=(15, 5))
        tk.Label(root, text="Tap RESET box to select items for factory reset",
                 font=("Helvetica", 12, "bold"), fg="green", bg="black").pack(pady=(0, 10))

    def create_column_headers(frame):
        header = tk.Frame(frame, bg="black")
        header.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        tk.Label(header, text="Current Setting", font=("Helvetica", 16, "bold"),
                 fg="white", bg="black", width=24, anchor="e").grid(row=0, column=0, padx=(10, 5))
        tk.Label(header, text="RESET", font=("Helvetica", 16, "bold"),
                 fg="white", bg="black", width=8, anchor="center").grid(row=0, column=1, padx=5)
        tk.Label(header, text="Factory Setting", font=("Helvetica", 16, "bold"),
                 fg="red", bg="black", width=24, anchor="w").grid(row=0, column=2, padx=(5, 10))

    def create_row(frame, row_num, left, toggle_var, right):
        tk.Label(frame, text=left, font=("Helvetica", 14, "bold"),
                 fg="white", bg="black", width=30, anchor="e").grid(row=row_num, column=0, padx=(5, 5), pady=3)
        tk.Checkbutton(frame, variable=toggle_var, text="RESET",
                       activebackground="white", activeforeground="black",
                       font=("Helvetica", 12, "bold"), fg="black", bg="white",
                       selectcolor="red", indicatoron=False, width=8, relief="raised").grid(row=row_num, column=1, padx=5)
        tk.Label(frame, text=right, font=("Helvetica", 14, "bold"),
                 fg="red", bg="black", width=30, anchor="w").grid(row=row_num, column=2, padx=(5, 5), pady=3)

    def create_rows(frame):
        create_row(frame, 1, face_display, toggles["faces"], "No Registered Faces")
        create_row(frame, 2, f"Door Access PIN: {door_pin}", toggles["door_pin"], "Door Access PIN: 1234")
        create_row(frame, 3, f"Admin Access PIN: {admin_pin}", toggles["admin_pin"], "Admin Access PIN: 654321")
        create_row(frame, 4, "Access Log", toggles["access_log"], "Clear Access Log")
        create_row(frame, 5, "Settings Log", toggles["settings_log"], "Clear Settings Log")

    def create_footer():
        footer = tk.Frame(root, bg="black")
        footer.pack(pady=(40, 25))
        tk.Button(footer, text="Cancel & Return\n to Settings Screen", font=("Helvetica", 12, "bold"),
                  fg="white", bg="gray", activebackground="gray", activeforeground="white",
                  width=24, height=3, command=go_back_and_clear).grid(row=0, column=0, padx=5)
        tk.Button(footer, text="Go to Pg 2", font=("Helvetica", 12, "bold"),
                  fg="white", bg="#0099ff", activebackground="#007acc", activeforeground="white",
                  width=8, height=3, command=lambda: show_page_2(root, go_back_callback, toggles)).grid(row=0, column=1, padx=5)
        tk.Button(footer, text="Reset Selected Values &\n Return to Settings Screen", font=("Helvetica", 12, "bold"),
                  fg="white", bg="green", activebackground="#007733", activeforeground="white",
                  width=24, height=3, command=lambda: reset_all_selected_values(root, toggles, go_back_callback)).grid(row=0, column=2, padx=5)

    create_title()
    table = tk.Frame(root, bg="black")
    table.pack(pady=(40, 0))
    create_column_headers(table)
    create_rows(table)
    create_footer()

def show_page_2(root, go_back_callback, toggles):
    settings_data = load_settings()

    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg="black")

    def go_back_and_clear():
        clear_all_toggles(toggles)
        go_back_callback()

    def create_title():
        tk.Label(root, text="Factory Reset Screen Pg: 2",
                 font=("Helvetica", 20, "bold"), fg="white", bg="black").pack(pady=(15, 5))
        tk.Label(root, text="Tap RESET box to select items for factory reset",
                 font=("Helvetica", 12, "bold"), fg="green", bg="black").pack(pady=(0, 10))

    def create_column_headers(frame):
        header = tk.Frame(frame, bg="black")
        header.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        tk.Label(header, text="Current Setting", font=("Helvetica", 16, "bold"),
                 fg="white", bg="black", width=24, anchor="e").grid(row=0, column=0, padx=(10, 5))
        tk.Label(header, text="RESET", font=("Helvetica", 16, "bold"),
                 fg="white", bg="black", width=8, anchor="center").grid(row=0, column=1, padx=5)
        tk.Label(header, text="Factory Setting", font=("Helvetica", 16, "bold"),
                 fg="red", bg="black", width=24, anchor="w").grid(row=0, column=2, padx=(5, 10))

    def create_row(frame, row_num, left, toggle_var, right):
        tk.Label(frame, text=left, font=("Helvetica", 14, "bold"),
                 fg="white", bg="black", width=30, anchor="e").grid(row=row_num, column=0, padx=(10, 5), pady=3)
        tk.Checkbutton(frame, variable=toggle_var, text="RESET",
                       activebackground="white", activeforeground="black",
                       font=("Helvetica", 12, "bold"), fg="black", bg="white",
                       selectcolor="red", indicatoron=False, width=8, relief="raised").grid(row=row_num, column=1, padx=5)
        tk.Label(frame, text=right, font=("Helvetica", 14, "bold"),
                 fg="red", bg="black", width=30, anchor="w").grid(row=row_num, column=2, padx=(5, 5), pady=3)

    def create_rows(frame):
        unlock = settings_data.get('unlock_time')
        lockout = settings_data.get('lockout_time')
        cooldown = settings_data.get('face_cooldown')
        timeout = settings_data.get('screen_timeout')
        reboot_day = settings_data.get('reboot_day')
        reboot_time = settings_data.get('reboot_time')

        unlock_display = f"Unlock Time: {unlock} Sec." if unlock is not None else "Unlock Time: Not Set"
        lockout_display = f"Wrong PIN Lockout: {lockout} Sec." if lockout is not None else "Wrong PIN Lockout: Not Set"
        cooldown_display = f"Face Unlock Cooldown: {cooldown} Sec." if cooldown is not None else "Face Unlock Cooldown: Not Set"
        timeout_display = f"Screen Timeout: {timeout} Sec." if timeout is not None else "Screen Timeout: Not Set"

        if reboot_day and reboot_time:
            reboot_display = f"Auto Reboot: {reboot_day.capitalize()} @ {reboot_time}"
        else:
            reboot_display = "Auto Reboot: Not Set"

        create_row(frame, 1, unlock_display, toggles["unlock_time"], "Unlock Time: 15 Sec.")
        create_row(frame, 2, lockout_display, toggles["lockout_time"], "Wrong PIN Lockout: 30 Sec.")
        create_row(frame, 3, cooldown_display, toggles["face_cooldown"], "Face Unlock Cooldown: 5 Sec.")
        create_row(frame, 4, timeout_display, toggles["touch_timeout"], "Screen Timeout: 120 Sec.")
        create_row(frame, 5, reboot_display, toggles["reboot_day_time"], "Auto Reboot: Sun @ 03:00")

    def create_footer():
        footer = tk.Frame(root, bg="black")
        footer.pack(pady=(40, 25))
        tk.Button(footer, text="Cancel & Return\n to Settings Screen", font=("Helvetica", 12, "bold"),
                  fg="white", bg="gray", activebackground="gray", activeforeground="white",
                  width=24, height=2, command=go_back_and_clear).grid(row=0, column=0, padx=5)
        tk.Button(footer, text="Go to Pg 1", font=("Helvetica", 12, "bold"),
                  fg="white", bg="#0099ff", activebackground="#007acc", activeforeground="white",
                  width=8, height=2, command=lambda: show_page_1(root, go_back_callback, toggles)).grid(row=0, column=1, padx=5)
        tk.Button(footer, text="Reset Selected Values &\n Return to Settings Screen", font=("Helvetica", 12, "bold"),
                  fg="white", bg="green", activebackground="#007733", activeforeground="white",
                  width=24, height=2, command=lambda: reset_all_selected_values(root, toggles, go_back_callback)).grid(row=0, column=2, padx=5)

    create_title()
    table = tk.Frame(root, bg="black")
    table.pack(pady=(40, 0))
    create_column_headers(table)
    create_rows(table)
    create_footer()
