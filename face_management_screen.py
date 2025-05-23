#face_management_screen.py
import tkinter as tk
import os
import csv
from datetime import datetime
from tkinter import messagebox
import face_capture_screen
import facial_recognition_screen as fr

FACES_DIR = "/home/awldodge/known_faces"
SETTINGS_LOG = "settings_log.csv"

def log_face_change(action, name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SETTINGS_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, "Face Management", f"{action} face: {name}"])

def show_screen(root, go_back_callback, camera):
    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg="black")

    def add_face():
        fr.pause_monitoring()
        face_capture_screen.show_capture_screen(
            root, lambda: show_screen(root, go_back_callback, camera), camera
        )

    def delete_face():
        selected = selected_name.get()
        if not selected or selected == "Select a face":
            messagebox.showerror("Error", "Please select a face to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Delete face data for '{selected}'?")
        if not confirm:
            return

        try:
            os.remove(os.path.join(FACES_DIR, f"{selected}.npy"))
            log_face_change("Deleted", selected)
            messagebox.showinfo("Deleted", f"Face data for '{selected}' deleted.")
            show_screen(root, go_back_callback, camera)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")

    # Title
    tk.Label(root, text="Face Management Screen", font=("Helvetica", 24, "bold"),
             fg="white", bg="black").pack(pady=(30, 20))

    # Main content frame with 2x2 grid layout
    grid_frame = tk.Frame(root, bg="black")
    grid_frame.pack(pady=10)

    # Dropdown setup
    face_files = [f.replace(".npy", "") for f in os.listdir(FACES_DIR) if f.endswith(".npy")]
    selected_name = tk.StringVar(value="Select a face")
    if not face_files:
        face_files = ["No faces found"]
        selected_name.set("No faces found")

    dropdown = tk.OptionMenu(grid_frame, selected_name, *face_files)
    dropdown.config(font=("Helvetica", 16), bg="white", width=24)
    dropdown["menu"].config(font=("Helvetica", 14))

    # Buttons
    btn_add = tk.Button(grid_frame, text="Add Face", font=("Helvetica", 16, "bold"),
                        bg="#1e90ff", fg="white", width=24, height=2, command=add_face)

    btn_delete = tk.Button(grid_frame, text="Delete Selected Face", font=("Helvetica", 16, "bold"),
                           bg="red", fg="white", width=24, height=2, command=delete_face)

    btn_back = tk.Button(grid_frame, text="Return to Settings Screen", font=("Helvetica", 16, "bold"),
                         bg="green", fg="white", width=24, height=2, command=go_back_callback)

    # Grid placement
    btn_add.grid(row=0, column=0, padx=20, pady=10)
    btn_delete.grid(row=0, column=1, padx=20, pady=10)
    btn_back.grid(row=1, column=0, padx=20, pady=10)
    dropdown.grid(row=1, column=1, padx=20, pady=10)
