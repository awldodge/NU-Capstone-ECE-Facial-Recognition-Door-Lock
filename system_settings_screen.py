# system_settings_screen.py
import tkinter as tk
from tkinter import messagebox
import json
import os
import csv
from datetime import datetime

SETTINGS_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen/settings.json"
SETTINGS_LOG = "settings_log.csv"

def load_settings():
    try:
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    except:
        return {}

def save_settings(data):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(data, f, indent=4)

def show_screen(root, go_home_callback):
    for widget in root.winfo_children():
        widget.destroy()

    settings = load_settings()

    root.configure(bg="black")
    tk.Label(root, text="System Settings", font=("Helvetica", 26, "bold"),
             fg="white", bg="black").pack(pady=20)

    main_frame = tk.Frame(root, bg="black")
    main_frame.pack()

    # Entry Variables
    unlock_time_var = tk.StringVar(value=str(settings.get("unlock_time", 15)))
    lockout_time_var = tk.StringVar(value=str(settings.get("lockout_time", 30)))
    face_cooldown_var = tk.StringVar(value=str(settings.get("face_cooldown", 10)))
    screen_timeout_var = tk.StringVar(value=str(settings.get("screen_timeout", 60)))

    input_frame = tk.Frame(main_frame, bg="black")
    input_frame.grid(row=0, column=1, padx=40, pady=10)

    entry_style = {"font": ("Helvetica", 14), "width": 7, "justify": "center"}

    unlock_entry = tk.Entry(input_frame, textvariable=unlock_time_var, **entry_style)
    lockout_entry = tk.Entry(input_frame, textvariable=lockout_time_var, **entry_style)
    cooldown_entry = tk.Entry(input_frame, textvariable=face_cooldown_var, **entry_style)
    timeout_entry = tk.Entry(input_frame, textvariable=screen_timeout_var, **entry_style)

    input_fields = [
        ("Unlock Time (1-60 sec):", unlock_entry),
        ("Incorrect PIN Lockout Time (5-300 sec):", lockout_entry),
        ("Face Cooldown Time (1-60 sec):", cooldown_entry),
        ("Screen Timeout (10-600 sec):", timeout_entry),
    ]

    for i, (label_text, entry_widget) in enumerate(input_fields):
        tk.Label(input_frame, text=label_text, font=("Helvetica", 14),
                 fg="white", bg="black").grid(row=i, column=0, sticky="e", pady=5)
        entry_widget.grid(row=i, column=1, pady=5)

    focused_entry = {"widget": None}

    def set_focus(widget):
        focused_entry["widget"] = widget

    for _, entry in input_fields:
        entry.bind("<FocusIn>", lambda e, widget=entry: set_focus(widget))

    # Keypad
    keypad_frame = tk.Frame(main_frame, bg="black")
    keypad_frame.grid(row=0, column=0, padx=20)

    def insert_digit(digit):
        widget = focused_entry.get("widget")
        if widget and isinstance(widget, tk.Entry):
            widget.insert(tk.END, str(digit))

    def clear_entry():
        widget = focused_entry.get("widget")
        if widget and isinstance(widget, tk.Entry):
            widget.delete(0, tk.END)

    def backspace():
        widget = focused_entry.get("widget")
        if widget and isinstance(widget, tk.Entry):
            widget.delete(len(widget.get())-1, tk.END)

    btn_style = {"width": 5, "height": 2, "font": ("Helvetica", 16, "bold"), "bg": "blue", "fg": "white"}
    buttons = [
        ('1', lambda: insert_digit(1)), ('2', lambda: insert_digit(2)), ('3', lambda: insert_digit(3)),
        ('4', lambda: insert_digit(4)), ('5', lambda: insert_digit(5)), ('6', lambda: insert_digit(6)),
        ('7', lambda: insert_digit(7)), ('8', lambda: insert_digit(8)), ('9', lambda: insert_digit(9)),
        ('Clear', clear_entry), ('0', lambda: insert_digit(0)), ('⌫', backspace)
    ]

    for i, (label, command) in enumerate(buttons):
        row, col = divmod(i, 3)
        tk.Button(keypad_frame, text=label, command=command, **btn_style).grid(row=row, column=col, padx=5, pady=5)
    
    def log_setting_change(setting_name, new_value):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(SETTINGS_LOG, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([timestamp, f"{setting_name}", f"Changed manually to {new_value} seconds"])
    
    # Validation and Save
    def save_changes():
        try:
            ut = int(unlock_time_var.get())
            lt = int(lockout_time_var.get())
            fc = int(face_cooldown_var.get())
            st = int(screen_timeout_var.get())

            if not (1 <= ut <= 60):
                raise ValueError("Unlock Time must be between 1 and 60 seconds.")
            if not (5 <= lt <= 300):
                raise ValueError("Lockout Time must be between 5 and 300 seconds.")
            if not (1 <= fc <= 60):
                raise ValueError("Face Cooldown must be between 1 and 60 seconds.")
            if not (10 <= st <= 600):
                raise ValueError("Screen Timeout must be between 10 and 600 seconds.")

            updated_settings = load_settings()

            if updated_settings.get("unlock_time") != ut:
                log_setting_change("Unlock Time", ut)
            if updated_settings.get("lockout_time") != lt:
                log_setting_change("Lockout Time", lt)
            if updated_settings.get("face_cooldown") != fc:
                log_setting_change("Face Cooldown", fc)
            if updated_settings.get("screen_timeout") != st:
                log_setting_change("Screen Timeout", st)

            updated_settings["unlock_time"] = ut
            updated_settings["lockout_time"] = lt
            updated_settings["face_cooldown"] = fc
            updated_settings["screen_timeout"] = st

            save_settings(updated_settings)
            messagebox.showinfo("Success", "Settings updated successfully.")
            go_home_callback()
            
        except ValueError as ve:
            messagebox.showerror("Invalid Input", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings.\n{e}")

    action_frame = tk.Frame(root, bg="black")
    action_frame.pack(pady=(10,10))

    save_button = tk.Button(action_frame,
        text="Save Settings &\nReturn to Settings Screen", command=save_changes,
        font=("Helvetica", 16, "bold"), bg="blue", fg="white", width=24, height=3, justify="center"
    )
    save_button.grid(row=0, column=0, padx=20, pady=10)

    return_button = tk.Button(action_frame,
        text="Return to\nSettings Screen", command=go_home_callback,
        font=("Helvetica", 16, "bold"), bg="green", fg="white", width=24, height=3, justify="center"
    )
    return_button.grid(row=0, column=1, padx=20, pady=10)
