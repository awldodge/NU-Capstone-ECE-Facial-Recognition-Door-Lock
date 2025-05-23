#admin_pin_screen.py
import tkinter as tk
import time
import csv
import hashlib
import os
import json
from datetime import datetime
import settings_screen
import facial_recognition_screen as fr
from lockout_manager import load_lockout_state, save_lockout_state, clear_lockout_state

SETTINGS_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen/settings.json"

def load_lockout_time():
    try:
        with open(SETTINGS_PATH, "r") as f:
            settings = json.load(f)
            return settings.get("lockout_time", 30)
    except Exception:
        return 30

def log_settings_access(method, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("settings_log.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, method, status])

ADMIN_PIN_PATH = "/home/awldodge/.config/doorlock/admin_pin.txt"
DEFAULT_ADMIN_PIN = "654321"

def load_admin_pin_hash():
    os.makedirs(os.path.dirname(ADMIN_PIN_PATH), exist_ok=True)
    if not os.path.exists(ADMIN_PIN_PATH):
        hashed = hashlib.sha256(DEFAULT_ADMIN_PIN.encode()).hexdigest()
        with open(ADMIN_PIN_PATH, "w") as f:
            f.write(hashed)
        return hashed
    try:
        with open(ADMIN_PIN_PATH, "r") as f:
            return f.read().strip()
    except Exception:
        return ""

def save_admin_pin_hash(new_pin):
    hashed = hashlib.sha256(new_pin.encode()).hexdigest()
    with open(ADMIN_PIN_PATH, "w") as f:
        f.write(hashed)

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def show_screen(root, on_success, on_cancel):
    import facial_recognition_screen as fr
    fr.pause_monitoring()
    entered_pin = ""
    
    failed_attempts, lockout_end_time = load_lockout_state("admin_pin")
    locked_out = failed_attempts >= 3 and time.time() < lockout_end_time
    remaining = int(lockout_end_time - time.time())

    if locked_out and remaining > 0:
        for widget in root.winfo_children():
            widget.destroy()

        frame = tk.Frame(root, bg="black")
        frame.pack(expand=True, fill="both")

        tk.Label(frame, text="LOCKED OUT", font=("Helvetica", 32, "bold"),
                 fg="red", bg="black").pack(pady=40)

        countdown_label = tk.Label(frame, text="", font=("Helvetica", 20, "bold"),
                                   fg="red", bg="black")
        countdown_label.pack()

        def unlock_keypad_and_show_screen():
            clear_lockout_state("admin_pin")
            log_settings_access("Admin System", "Lockout Cleared")
            show_screen(root, on_success, on_cancel)
            
        def update_screen_countdown(t):
            countdown_label.config(text=f"Try again in {t} seconds...")
            if t > 0:
                root.after(1000, lambda: update_screen_countdown(t - 1))
            else:
                unlock_keypad_and_show_screen()

        update_screen_countdown(remaining)
        return

    keypad_buttons = []

    def on_digit_press(digit):
        nonlocal entered_pin
        if len(entered_pin) < 6:
            entered_pin += digit
            update_display()

    def clear_pin():
        nonlocal entered_pin
        entered_pin = ""
        update_display()

    def submit_pin():
        nonlocal entered_pin

        failed_attempts, lockout_end_time = load_lockout_state("admin_pin")
        locked_out = failed_attempts >= 3 and time.time() < lockout_end_time

        if locked_out:
            print("Input ignored: system is currently locked out.")
            return

        if hash_pin(entered_pin) == load_admin_pin_hash():
            clear_lockout_state("admin_pin")
            log_settings_access("Admin PIN", "Success")
            info_label.config(text="")
            on_success()
        else:
            failed_attempts += 1
            log_settings_access("Admin PIN", "Failed")
            save_lockout_state("admin_pin", failed_attempts, 0)

            if failed_attempts >= 3:
                lockout_time = load_lockout_time()
                lockout_end_time = time.time() + lockout_time
                save_lockout_state("admin_pin", failed_attempts, lockout_end_time)
                lockout()
            else:
                info_label.config(text=f"Attempts: {failed_attempts} of 3", fg="white")

        clear_pin()

    def lockout():
        lockout_time = load_lockout_time()
        lockout_end_time = time.time() + lockout_time
        failed_attempts, _ = load_lockout_state("admin_pin")
        save_lockout_state("admin_pin", failed_attempts, lockout_end_time)
        log_settings_access("Admin PIN", "Lockout Triggered")
        for btn in keypad_buttons:
            btn.config(state="disabled")
        show_screen(root, on_success, on_cancel)
        
    def update_display():
        try:
            pin_display.config(text="*" * len(entered_pin))
        except tk.TclError:
            pass

    for widget in root.winfo_children():
        widget.destroy()

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=3)
    root.grid_columnconfigure(1, weight=2)

    main_frame = tk.Frame(root, bg="black")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=(40, 10), pady=20)

    side_frame = tk.Frame(root, bg="black")
    side_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20))
    side_frame.grid_rowconfigure((0, 1), weight=1)
    side_frame.grid_columnconfigure(0, weight=1)

    tk.Label(main_frame, text="Admin PIN Required", font=("Helvetica", 24, "bold"),
             fg="white", bg="black").pack(pady=(0, 10))

    pin_box = tk.Frame(main_frame, bg="white", width=240, height=35)
    pin_box.pack(pady=(10, 10))
    pin_box.pack_propagate(False)

    pin_display = tk.Label(pin_box, text="", font=("Helvetica", 24, "bold"),
                           fg="black", bg="white", anchor="center", justify="center")
    pin_display.place(relx=0.5, rely=0.5, anchor="center")

    info_label = tk.Label(main_frame, text="", font=("Helvetica", 16, "bold"),
                          fg="white", bg="black")
    info_label.pack(pady=(5, 0))

    if failed_attempts > 0:
        info_label.config(text=f"Attempts: {failed_attempts} of 3", fg="white")

    keypad_frame = tk.Frame(main_frame, bg="black")
    keypad_frame.pack(pady=(10, 20))

    button_style = {
        "font": ("Helvetica", 16, "bold"),
        "bg": "#0099ff",
        "fg": "white",
        "activebackground": "#33bbff",
        "width": 5,
        "height": 2,
    }

    buttons = [
        ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
        ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
        ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
        ('Clear', 3, 0), ('0', 3, 1), ('Enter', 3, 2),
    ]

    for (label, r, c) in buttons:
        if label == "Clear":
            cmd = clear_pin
        elif label == "Enter":
            cmd = submit_pin
        else:
            cmd = lambda d=label: on_digit_press(d)

        btn = tk.Button(keypad_frame, text=label, command=cmd, **button_style)
        btn.grid(row=r, column=c, padx=8, pady=8)
        keypad_buttons.append(btn)

    tk.Label(side_frame, bg="black").grid(row=0, column=0, pady=(10, 0))

    side_btn_style = {
        "font": ("Helvetica", 18, "bold"),
        "fg": "white",
        "width": 18,
        "height": 4
    }

    tk.Button(side_frame, text="Return to\nHome Screen", command=on_cancel,
              bg="#66cc66", activebackground="#99e699",
              **side_btn_style).grid(row=1, column=0, pady=(10, 20))
