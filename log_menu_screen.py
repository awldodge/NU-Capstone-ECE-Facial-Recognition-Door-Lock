# log_menu_screen.py
import tkinter as tk
import access_log_screen
import settings_log_screen

def show_screen(root, go_back_callback):
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="black")

    title = tk.Label(root, text="View Logs Screen", font=("Helvetica", 32, "bold"), fg="white", bg="black")
    title.pack(pady=20)

    button_frame = tk.Frame(root, bg="black")
    button_frame.pack(pady=40)

    def go_to_access_logs():
        access_log_screen.show_screen(root, show_screen_callback, go_to_settings_logs)

    def go_to_settings_logs():
        settings_log_screen.show_screen(root, show_screen_callback, go_to_access_logs)

    def show_screen_callback():
        show_screen(root, go_back_callback)

    tk.Button(button_frame, text="Access Logs", font=("Helvetica", 18, "bold"),
              width=25, height=2, bg="#1e90ff", fg="white",
              activebackground="#3399ff", command=go_to_access_logs).pack(pady=10)

    tk.Button(button_frame, text="Settings Logs", font=("Helvetica", 18, "bold"),
              width=25, height=2, bg="#1e90ff", fg="white",
              activebackground="#3399ff", command=go_to_settings_logs).pack(pady=10)

    tk.Button(button_frame, text="Return to Settings Screen", font=("Helvetica", 18, "bold"),
              width=25, height=2, bg="#00cc44", fg="white",
              activebackground="#009933", command=go_back_callback).pack(pady=30)
