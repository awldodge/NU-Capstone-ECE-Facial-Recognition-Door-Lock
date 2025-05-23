# pin_management_screen.py 
import tkinter as tk
from tkinter import messagebox
import hashlib
import os
import json
from datetime import datetime

DOOR_PIN_PATH = "/home/awldodge/.config/doorlock/door_pin.txt"
ADMIN_PIN_PATH = "/home/awldodge/.config/doorlock/admin_pin.txt"
SETTINGS_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen/settings.json"
LOG_FILE = "settings_log.csv"

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def save_hashed_pin(path, hashed):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(hashed)

def log_settings_change(action, detail):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp},{action},{detail}\n")

def show_screen(root, go_back_callback):
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="black")
    tk.Label(root, text="PIN Management Screen", font=("Helvetica", 26, "bold"),
             fg="white", bg="black").pack(pady=20)

    main_frame = tk.Frame(root, bg="black")
    main_frame.pack()

    pin_frame = tk.Frame(main_frame, bg="black")
    pin_frame.grid(row=0, column=1, padx=40, pady=10)

    door_pin_var = tk.StringVar()
    door_confirm_var = tk.StringVar()
    admin_pin_var = tk.StringVar()
    admin_confirm_var = tk.StringVar()
    pin_entries = []

    e1 = tk.Entry(pin_frame, font=("Helvetica", 14), textvariable=door_pin_var, show="*", width=7)
    e2 = tk.Entry(pin_frame, font=("Helvetica", 14), textvariable=door_confirm_var, show="*", width=7)
    e3 = tk.Entry(pin_frame, font=("Helvetica", 14), textvariable=admin_pin_var, show="*", width=7)
    e4 = tk.Entry(pin_frame, font=("Helvetica", 14), textvariable=admin_confirm_var, show="*", width=7)
    pin_entries.extend([e1, e2, e3, e4])

    tk.Label(pin_frame, text="New Door PIN (4–6 digits):", font=("Helvetica", 14), fg="white", bg="black").grid(row=0, column=0, sticky="e")
    e1.grid(row=0, column=1, pady=5)

    tk.Label(pin_frame, text="Confirm Door PIN:", font=("Helvetica", 14), fg="white", bg="black").grid(row=1, column=0, sticky="e")
    e2.grid(row=1, column=1, pady=5)

    tk.Label(pin_frame, text="New Admin PIN (6 digits):", font=("Helvetica", 14), fg="white", bg="black").grid(row=2, column=0, sticky="e", pady=(10, 0))
    e3.grid(row=2, column=1, pady=5)

    tk.Label(pin_frame, text="Confirm Admin PIN:", font=("Helvetica", 14), fg="white", bg="black").grid(row=3, column=0, sticky="e")
    e4.grid(row=3, column=1, pady=5)

    show_pin_var = tk.BooleanVar(value=False)
    def toggle_pin_visibility():
        char = "" if show_pin_var.get() else "*"
        for entry in pin_entries:
            entry.config(show=char)

    tk.Checkbutton(pin_frame, text="Show PIN", variable=show_pin_var, command=toggle_pin_visibility,
                   font=("Helvetica", 12), bg="black", fg="white", activebackground="black",
                   activeforeground="white", selectcolor="black").grid(row=4, column=1, sticky="w", pady=(10, 0))

    keypad_frame = tk.Frame(main_frame, bg="black")
    keypad_frame.grid(row=0, column=0, padx=20)

    def insert_digit(digit):
        widget = root.focus_get()
        if isinstance(widget, tk.Entry):
            widget.insert(tk.END, str(digit))

    def backspace():
        widget = root.focus_get()
        if isinstance(widget, tk.Entry):
            widget.delete(0, tk.END)

    def clear_entry():
        widget = root.focus_get()
        if isinstance(widget, tk.Entry):
            widget.delete(0, tk.END)

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

    tk.Button(keypad_frame, text="Return to Settings Screen", command=go_back_callback,
              font=("Helvetica", 14, "bold"), bg="green", fg="white", width=24).grid(row=5, column=0, columnspan=3, pady=(20, 0))

    def update_door_pin():
        new, confirm = door_pin_var.get(), door_confirm_var.get()
        if new != confirm:
            messagebox.showerror("Error", "Door PINs do not match.")
        elif not new.isdigit() or not (4 <= len(new) <= 6):
            messagebox.showerror("Error", "Door PIN must be 4–6 digits.")
        else:
            save_hashed_pin(DOOR_PIN_PATH, hash_pin(new))
            try:
                with open(SETTINGS_PATH, "r") as f:
                    settings_data = json.load(f)
            except:
                settings_data = {}
            settings_data["door_pin"] = new
            with open(SETTINGS_PATH, "w") as f:
                json.dump(settings_data, f, indent=4)
            log_settings_change("Door PIN Update", f"Changed manually to {new}")
            messagebox.showinfo("Success", "Door PIN successfully changed.")

    def update_admin_pin():
        new, confirm = admin_pin_var.get(), admin_confirm_var.get()
        if new != confirm:
            messagebox.showerror("Error", "Admin PINs do not match.")
        elif not new.isdigit() or len(new) != 6:
            messagebox.showerror("Error", "Admin PIN must be exactly 6 digits.")
        else:
            save_hashed_pin(ADMIN_PIN_PATH, hash_pin(new))
            try:
                with open(SETTINGS_PATH, "r") as f:
                    settings_data = json.load(f)
            except:
                settings_data = {}
            settings_data["admin_pin"] = new
            with open(SETTINGS_PATH, "w") as f:
                json.dump(settings_data, f, indent=4)
            log_settings_change("Admin PIN Update", f"Changed manually to {new}")
            messagebox.showinfo("Success", "Admin PIN successfully changed.")

    action_frame = tk.Frame(root, bg="black")
    action_frame.pack(pady=20)

    tk.Button(action_frame, text="Update Door PIN", command=update_door_pin,
              font=("Helvetica", 14, "bold"), bg="blue", fg="white", width=18).grid(row=0, column=0, padx=10)

    tk.Button(action_frame, text="Update Admin PIN", command=update_admin_pin,
              font=("Helvetica", 14, "bold"), bg="blue", fg="white", width=18).grid(row=0, column=1, padx=10)
