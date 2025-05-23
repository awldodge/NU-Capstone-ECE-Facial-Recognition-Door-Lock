#face_capture_screen.py
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import os
import cv2
import face_recognition
import numpy as np
import json
import csv
from datetime import datetime
from tkinter import messagebox
from camera_manager import safe_reset_camera, get_camera_lock

FACES_DIR = "/home/awldodge/known_faces"
SETTINGS_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen/settings.json"
SETTINGS_LOG = "settings_log.csv"
MAX_NAME_LENGTH = 10

def log_face_change(action, name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SETTINGS_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, "Face Management", f"{action} face: {name}"])

def show_capture_screen(root, go_back_callback, camera):
    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg="black")

    name_var = tk.StringVar()
    preview_running = [True]
    is_shift = [False]

    tk.Label(root, text="Face Capture & Registration", font=("Helvetica", 24, "bold"),
             fg="white", bg="black").pack(pady=(10, 0))
    tk.Label(root, text="Enter name and tap Capture to register face.",
             font=("Helvetica", 16), fg="lime", bg="black").pack(pady=(0, 10))

    content_frame = tk.Frame(root, bg="black")
    content_frame.pack(padx=10, pady=10, fill="both", expand=True)

    preview_column = tk.Frame(content_frame, bg="black")
    preview_column.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

    preview_label = tk.Label(preview_column, bg="black", width=240, height=180)
    preview_label.pack()

    preview_buttons = tk.Frame(preview_column, bg="black")
    preview_buttons.pack(pady=(10, 0))

    def update_display():
        name_display.config(text=name_var.get())

    def add_char(c):
        if len(name_var.get()) < MAX_NAME_LENGTH:
            name_var.set(name_var.get() + c)
            update_display()

    def delete_char():
        name_var.set(name_var.get()[:-1])
        update_display()

    def clear_name():
        name_var.set("")
        update_display()

    keyboard_frame = tk.Frame(content_frame, bg="black")
    keyboard_frame.grid(row=0, column=1, sticky="ne", padx=10, pady=10)

    name_display = tk.Label(keyboard_frame, text="", font=("Helvetica", 28), fg="cyan", bg="black")
    name_display.grid(row=0, column=0, columnspan=7, pady=(0, 10))

    def build_keyboard():
        for widget in keyboard_frame.winfo_children():
            if widget != name_display:
                widget.destroy()

        rows = [
            list("abcdef"),
            list("ghijkl"),
            list("mnopqr"),
            list("stuvwx"),
            list("yz") + ["Shift", "Space", "Delete", "Clear"]
        ]

        def shift_char(char):
            return char.upper() if is_shift[0] else char.lower()

        for r, row_keys in enumerate(rows):
            for c, key in enumerate(row_keys):
                if key == "Space":
                    cmd = lambda: add_char(" ")
                    txt = "Space"
                elif key == "Delete":
                    cmd = delete_char
                    txt = "Del"
                elif key == "Clear":
                    cmd = clear_name
                    txt = "Clear"
                elif key == "Shift":
                    def toggle_shift():
                        is_shift[0] = True
                        build_keyboard()
                    cmd = toggle_shift
                    txt = "Shift"
                else:
                    display_char = shift_char(key)
                    def add(k=display_char):
                        add_char(k)
                        if is_shift[0]:
                            is_shift[0] = False
                            build_keyboard()
                    cmd = add
                    txt = display_char

                tk.Button(keyboard_frame, text=txt, font=("Helvetica", 14),
                          width=4, height=2, command=cmd).grid(row=r + 1, column=c, padx=2, pady=2, sticky="w")

    build_keyboard()

    def flash_effect():
        flash = tk.Label(root, bg="white")
        flash.place(relx=0, rely=0, relwidth=1, relheight=1)
        root.after(100, flash.destroy)

    def capture_and_save():
        preview_running[0] = False
        name = name_var.get().strip()
        if not name or len(name) > MAX_NAME_LENGTH or not all(c.isalnum() or c == ' ' for c in name):
            messagebox.showerror("Invalid Name", "Use 1–10 letters/spaces only.")
            preview_running[0] = True
            update_preview()
            return
        try:
            with get_camera_lock():
                frame = camera.capture_array()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = cv2.rotate(rgb, cv2.ROTATE_90_CLOCKWISE)
            boxes = face_recognition.face_locations(rgb)
            if not boxes:
                messagebox.showerror("No Face", "No face detected. Try again.")
                preview_running[0] = True
                update_preview()
                return
            encodings = face_recognition.face_encodings(rgb, boxes)
            if not encodings:
                messagebox.showerror("Encoding Error", "Failed to encode face.")
                preview_running[0] = True
                update_preview()
                return
            flash_effect()
            encoding = encodings[0]
            np.save(os.path.join(FACES_DIR, f"{name}.npy"), encoding)
            with open(SETTINGS_PATH, "r") as f:
                settings = json.load(f)
            settings["face_count"] = len([f for f in os.listdir(FACES_DIR) if f.endswith(".npy")])
            with open(SETTINGS_PATH, "w") as f:
                json.dump(settings, f, indent=4)
            messagebox.showinfo("Success", f"Face saved for '{name}'")
            log_face_change("Added", name)
            name_var.set("")
            update_display()
            preview_running[0] = True
            update_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Camera capture failed: {e}")
            preview_running[0] = True
            update_preview()

    def cancel_and_return():
        preview_running[0] = False
        name_var.set("")
        update_display()
        go_back_callback()

    tk.Button(preview_buttons, text="Capture & Save", font=("Helvetica", 14, "bold"),
              bg="#1e90ff", fg="white", width=20, height=2, command=capture_and_save).pack(pady=(10, 10))
    tk.Button(preview_buttons, text="Return to Face Management Screen", font=("Helvetica", 14),
              bg="green", fg="white", width=30, height=2, command=cancel_and_return).pack()
    
    def update_preview():
        if not preview_running[0]:
            return
        try:
            with get_camera_lock():
                frame = camera.capture_array()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rotated = cv2.rotate(rgb, cv2.ROTATE_90_CLOCKWISE)
            boxes = face_recognition.face_locations(rotated)
            img = Image.fromarray(rotated.astype('uint8'), 'RGB').resize((240, 180))
            draw = ImageDraw.Draw(img)
            scale_x = 240 / rotated.shape[1]
            scale_y = 180 / rotated.shape[0]
            for top, right, bottom, left in boxes:
                draw.rectangle([(left * scale_x, top * scale_y), (right * scale_x, bottom * scale_y)],
                               outline="green", width=2)
            imgtk = ImageTk.PhotoImage(image=img)
            preview_label.imgtk = imgtk
            preview_label.configure(image=imgtk)
        except Exception as e:
            print(f"[ERROR] Failed to update preview: {e}")
            return
        root.after(100, update_preview)

    update_preview()
