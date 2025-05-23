# pin_screen.py
import tkinter as tk
import time
import access_log
import hashlib
import os
import json
from datetime import datetime
from door_lock import unlock_door
import facial_recognition_screen as fr
from facial_recognition_screen import load_unlock_lock_times, load_face_cooldown
from lockout_manager import load_lockout_state, save_lockout_state, clear_lockout_state

# Unlock/Lock Timing Settings
SETTINGS_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen/settings.json"
DEFAULT_UNLOCK_TIME = 15
DEFAULT_LOCK_TIME = 5

# Paths and Defaults
DOOR_PIN_PATH = "/home/awldodge/.config/doorlock/door_pin.txt"
DEFAULT_DOOR_PIN = "1234"

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def load_door_pin_hash():
    os.makedirs(os.path.dirname(DOOR_PIN_PATH), exist_ok=True)

    if not os.path.exists(DOOR_PIN_PATH):
        hashed = hash_pin(DEFAULT_DOOR_PIN)
        with open(DOOR_PIN_PATH, "w") as f:
            f.write(hashed)
        return hashed

    try:
        with open(DOOR_PIN_PATH, "r") as f:
            return f.read().strip()
    except Exception:
        return ""

def log_access_attempt(method, status):
    access_log.log_access(method, status)

def show_screen(root, go_back_callback):
    fr.pause_monitoring()
    entered_pin = ""

    FAILED_ATTEMPTS, LOCKOUT_END_TIME = load_lockout_state("door_pin")
    LOCKED_OUT = FAILED_ATTEMPTS >= 3 and time.time() < LOCKOUT_END_TIME
    remaining = int(LOCKOUT_END_TIME - time.time())

    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="black")  # Force black background when showing PIN screen

    if LOCKED_OUT and remaining > 0:
        frame = tk.Frame(root, bg="black")
        frame.pack(expand=True, fill="both")

        tk.Label(frame, text="LOCKED OUT", font=("Helvetica", 32, "bold"),
                 fg="red", bg="black").pack(pady=40)

        countdown_label = tk.Label(frame, text="", font=("Helvetica", 20, "bold"),
                                   fg="red", bg="black")
        countdown_label.pack()

        def unlock_keypad_and_show_screen():
            clear_lockout_state("door_pin")
            log_access_attempt("System", "Lockout Cleared")
            show_screen(root, go_back_callback)

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
    
    def get_lockout_time():
        try:
            with open(SETTINGS_PATH, "r") as f:
                settings = json.load(f)
                return settings.get("lockout_time", 30)
        except:
            return 30
    
    def submit_pin():
        nonlocal entered_pin
        
        # Reload state at the start of the function
        failed_attempts, lockout_end_time = load_lockout_state("door_pin")
        locked_out = failed_attempts >= 3 and time.time() < lockout_end_time

        if locked_out:
            print("Input ignored: system is currently locked out.")
            return

        if hash_pin(entered_pin) == load_door_pin_hash():
            clear_lockout_state("door_pin")
            log_access_attempt("PIN", "Success")
            info_label.config(text="")
            unlock_time, _ = load_unlock_lock_times()
            unlock_door(unlock_time)  # Unlock the door via relay
            show_unlocked_screen(root, go_back_callback)
        else:
            failed_attempts += 1
            log_access_attempt("PIN", "Failed")
            save_lockout_state("door_pin", failed_attempts, 0)
            
            if failed_attempts >= 3:       
                lockout_time = get_lockout_time()
                lockout_end_time = time.time() + lockout_time if failed_attempts >= 3 else 0
                save_lockout_state("door_pin", failed_attempts, lockout_end_time)
                lockout()
            else:
                info_label.config(text=f"Attempts: {failed_attempts} of 3", fg="white")

        clear_pin()

    def lockout():
        log_access_attempt("PIN", "Lockout Triggered")
        for btn in keypad_buttons:
            btn.config(state="disabled")
        show_screen(root, go_back_callback)

    def update_display():
        if pin_display and pin_display.winfo_exists():
            pin_display.config(text="*" * len(entered_pin))

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=3)
    root.grid_columnconfigure(1, weight=2)

    main_frame = tk.Frame(root, bg="black")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=(40, 10), pady=20)

    side_frame = tk.Frame(root, bg="black")
    side_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20))
    side_frame.grid_rowconfigure((0, 1), weight=1)
    side_frame.grid_columnconfigure(0, weight=1)

    tk.Label(main_frame, text="Enter Door Access Pin Screen", font=("Helvetica", 24, "bold"),
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

    if FAILED_ATTEMPTS > 0:
        info_label.config(text=f"Attempts: {FAILED_ATTEMPTS} of 3", fg="white")

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

    tk.Button(side_frame, text="Return to\nHome Screen", command=go_back_callback,
              bg="#66cc66", activebackground="#99e699",
              **side_btn_style).grid(row=1, column=0, pady=(10, 20))

def show_unlocked_screen(root, go_back_callback):
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="green")
    frame = tk.Frame(root, bg="green")
    frame.pack(expand=True, fill="both")

    welcome_label = tk.Label(frame, text="Door Unlocked", font=("Helvetica", 36, "bold"),
                             fg="white", bg="green")
    welcome_label.pack(pady=(50, 10))

    countdown_label = tk.Label(frame, text="", font=("Helvetica", 28, "bold"),
                               fg="white", bg="green")
    countdown_label.pack()

    def update_countdown(seconds_remaining):
        if countdown_label.winfo_exists():
            countdown_label.config(text=f"Locking in {seconds_remaining} seconds...")
            if seconds_remaining > 0:
                root.after(1000, lambda: update_countdown(seconds_remaining - 1))
            else:
                show_locked_screen(root, go_back_callback)

    unlock_time, _ = load_unlock_lock_times()
    update_countdown(unlock_time)

def show_locked_screen(root, go_back_callback):
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="red")
    frame = tk.Frame(root, bg="red")
    frame.pack(expand=True, fill="both")

    locked_label = tk.Label(frame, text="Door Locked", font=("Helvetica", 36, "bold"),
                            fg="white", bg="red")
    locked_label.pack(pady=(50, 10))

    countdown_label = tk.Label(frame, text="", font=("Helvetica", 28, "bold"),
                               fg="white", bg="red")
    countdown_label.pack()

    def update_countdown(seconds_remaining):
        if countdown_label.winfo_exists():
            countdown_label.config(text=f"Returning in {seconds_remaining} seconds...")
            if seconds_remaining > 0:
                root.after(1000, lambda: update_countdown(seconds_remaining - 1))
            else:
                show_screen(root, go_back_callback)

    update_countdown(5)
