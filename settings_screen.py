# settings_screen.py
import tkinter as tk
import system_settings_screen
import pin_management_screen
import face_management_screen
import log_menu_screen
import reboot_control_screen
import factory_reset_screen
import system_info_screen
import main_ui
from factory_reset_state import get_toggles
import facial_recognition_screen as fr

def show_screen(root, go_back_callback, return_to_settings_callback):
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="black")

    title = tk.Label(root, text="Settings Screen", font=("Helvetica", 32, "bold"), fg="white", bg="black")
    title.pack(pady=20)

    button_frame = tk.Frame(root, bg="black")
    button_frame.pack()

    #Grid Configuration: 4 rows x 2 columns
    for i in range(4):
        button_frame.grid_rowconfigure(i, weight=1)
    for j in range(2):
        button_frame.grid_columnconfigure(j, weight=1)

    #Button List
    buttons = [
        ("System Settings", lambda: system_settings_screen.show_screen(root, return_to_settings_callback)),
        ("PIN Management", lambda: pin_management_screen.show_screen(root, return_to_settings_callback)),
        ("Face Management", lambda: face_management_screen.show_screen(root, return_to_settings_callback, fr.get_camera_instance())),
        ("View Logs", lambda: log_menu_screen.show_screen(root, return_to_settings_callback)),
        ("Reboot Control", lambda: reboot_control_screen.show_screen(root, return_to_settings_callback)),
        ("Factory Reset", lambda: factory_reset_screen.show_page_1(root, return_to_settings_callback, get_toggles())),
        ("System Information", lambda: system_info_screen.show_screen(root, return_to_settings_callback)),
        ("Return to Home Screen", go_back_callback), # The green home button
    ]

    #Create Buttons Dynamically
    for idx, (label, cmd) in enumerate(buttons):
        row, col = divmod(idx, 2)
        bg_color = "#33cc33" if label == "Return to Home Screen" else "#0099ff"
        active_bg = "#66ff66" if label == "Return to Home Screen" else "#33bbff"
        
        btn = tk.Button(
            button_frame,
            text=label,
            font=("Helvetica", 16, "bold"),
            fg="white",
            bg=bg_color,
            activebackground=active_bg,
            bd=0,
            width=26,
            height=2,
            command=cmd
        )
        btn.grid(row=row, column=col, padx=15, pady=15)
