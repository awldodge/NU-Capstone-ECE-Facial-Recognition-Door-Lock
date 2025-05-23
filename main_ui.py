# main_ui.py
import tkinter as tk
import pin_screen
import admin_pin_screen
import atexit
import power_manager
import facial_recognition_screen as fr
from facial_recognition_screen import load_unlock_lock_times, load_face_cooldown
from PIL import Image, ImageTk
import cv2
from picamera2 import Picamera2
import time
import json
import face_management_screen
import door_lock  

SETTINGS_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen/settings.json"

atexit.register(door_lock.cleanup)

class TouchscreenUI:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")
        self.unlock_countdown_id = None
        self.monitoring_enabled = True
        self.cooldown_running = False
        self.face_detected_label = None

        self.root.bind_all("<Any-KeyPress>", lambda e: power_manager.reset_idle_timer())
        self.root.bind_all("<Button>", lambda e: power_manager.reset_idle_timer())
        power_manager.reset_idle_timer()

        fr.set_ui_controller(self)
        fr.pause_monitoring()

        self.camera = Picamera2()
        self.camera.start()
        fr.set_camera(self.camera)
        time.sleep(1.5)

        self.show_main_menu()
        self.update_preview()

    def toggle_monitoring(self):
        if self.cooldown_running:
            self.cooldown_running = False

        self.monitoring_enabled = not self.monitoring_enabled

        if self.monitoring_enabled:
            self.start_face_recognition()
        else:
            fr.pause_monitoring()
            fr.set_cooldown_active(True)

        self.show_main_menu()

    def start_face_recognition(self):
        if not self.monitoring_enabled or self.cooldown_running:
            return

        face_cooldown = load_face_cooldown()
        if face_cooldown > 0:
            self.cooldown_running = True
            fr.set_cooldown_active(True)

            def update_cooldown(count):
                if not self.monitoring_enabled:
                    self.cooldown_running = False
                    return

                if self.face_detected_label and self.face_detected_label.winfo_exists():
                    self.face_detected_label.config(text=f"Face scan starting in {count} seconds...")

                if count > 0:
                    self.root.after(1000, update_cooldown, count - 1)
                else:
                    if self.face_detected_label and self.face_detected_label.winfo_exists():
                        self.face_detected_label.config(text="")
                    self.cooldown_running = False
                    fr.set_cooldown_active(False)
                    fr.start_monitoring()

            update_cooldown(face_cooldown)
        else:
            fr.set_cooldown_active(False)
            fr.start_monitoring()

    def show_main_menu(self):
        if not self.monitoring_enabled:
            fr.pause_monitoring()

        self.root.configure(bg="black") 
        for widget in self.root.winfo_children():
            try:
                widget.destroy()
            except:
                pass

        title_frame = tk.Frame(self.root, bg="black")
        title_frame.pack(pady=30)
        title = tk.Label(title_frame, text="Access System Home Screen",
                         font=("Helvetica", 32, "bold"), fg="white", bg="black")
        title.pack()
        status_color = "green" if self.monitoring_enabled else "red"
        status_text = "Monitoring Active" if self.monitoring_enabled else "Monitoring Paused"
        status_container = tk.Frame(self.root, bg="black")
        status_container.pack()
        status_dot = tk.Canvas(status_container, width=16, height=16, bg="black", highlightthickness=0)
        status_dot.create_oval(2, 2, 14, 14, fill=status_color)
        status_dot.pack(side="left", padx=(0, 6))
        tk.Label(status_container, text=status_text, font=("Helvetica", 12),
                 fg="white", bg="black").pack(side="left")

        self.face_detected_label = tk.Label(self.root, text="", font=("Helvetica", 14, "bold"),
                                            fg="yellow", bg="black")
        self.face_detected_label.pack(pady=(5, 5))

        button_frame = tk.Frame(self.root, bg="black")
        button_frame.pack(expand=True)

        pin_btn = tk.Button(button_frame, text="Enter Door Access PIN", font=("Helvetica", 20, "bold"),
                            bg="#1e90ff", fg="white", activebackground="#3399ff",
                            width=24, height=2, relief="flat", bd=0,
                            command=self.go_to_pin_screen)
        pin_btn.pack(pady=(40, 20))

        settings_btn = tk.Button(button_frame, text="Settings", font=("Helvetica", 20, "bold"),
                                 bg="#1e90ff", fg="white", activebackground="#3399ff",
                                 width=24, height=2, relief="flat", bd=0,
                                 command=self.go_to_settings)
        settings_btn.pack(pady=20)

        toggle_text = "Disable Monitoring" if self.monitoring_enabled else "Enable Monitoring"
        toggle_color = "green" if self.monitoring_enabled else "red"
        toggle_btn = tk.Button(button_frame, text=toggle_text, font=("Helvetica", 18, "bold"),
                               bg=toggle_color, fg="white", activebackground="gray",
                               width=24, height=3, relief="flat", bd=0,
                               command=self.toggle_monitoring)
        toggle_btn.pack(pady=10)

        side_frame = tk.Frame(self.root, bg="black")
        side_frame.place(relx=0.0, rely=0.5, anchor="w", x=20)
        exit_btn = tk.Button(side_frame, text="Exit to Desktop", font=("Helvetica", 16, "bold"),
                             command=self.exit_to_desktop, bg="#cc0000", fg="white",
                             activebackground="#ff3333", width=12, height=2)
        exit_btn.pack()

        # Always restart monitoring (with cooldown) on home screen load
        if self.monitoring_enabled:
            self.start_face_recognition()

    def go_to_settings(self):
        fr.pause_monitoring()
        self.monitoring_enabled = False
        import admin_pin_screen
        admin_pin_screen.show_screen(self.root, on_success=self.show_settings_screen, on_cancel=self.restore_and_show_main_menu)

    def show_settings_screen(self):
        import settings_screen
        fr.pause_monitoring()
        self.monitoring_enabled = False
        settings_screen.show_screen(
            self.root,
            go_back_callback=self.restore_and_show_main_menu,
            return_to_settings_callback=self.show_settings_screen)

    def go_to_pin_screen(self):
        fr.pause_monitoring()
        self.monitoring_enabled = False
        pin_screen.show_screen(self.root, self.restore_and_show_main_menu)

    def show_face_detected(self):
        if self.face_detected_label and self.face_detected_label.winfo_exists():
            self.face_detected_label.config(text="Face Detected")
            self.root.after(2000, self.hide_face_detected)

    def hide_face_detected(self):
        if self.face_detected_label and self.face_detected_label.winfo_exists():
            self.face_detected_label.config(text="")
    
    def update_preview(self):
        try:
            frame = self.camera.capture_array()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rotated = cv2.rotate(frame_rgb, cv2.ROTATE_90_CLOCKWISE)
            fr.update_latest_frame(rotated)
        except Exception as e:
            print(f"[Preview Error] {e}")
        self.root.after(100, self.update_preview)
        
    def restore_and_show_main_menu(self):
        self.monitoring_enabled = True
        self.show_main_menu()

    def show_unlock_screen(self, name):
        power_manager.turn_screen_on()
        fr.pause_monitoring()
        self.monitoring_enabled = False

        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="green")

        tk.Label(self.root, text=f"Welcome {name}", font=("Helvetica", 40, "bold"),
                 fg="white", bg="green").pack(pady=(50, 10))
        tk.Label(self.root, text="Door Unlocked", font=("Helvetica", 32),
                 fg="white", bg="green").pack(pady=(0, 20))

        countdown_label = tk.Label(self.root, text="", font=("Helvetica", 24),
                                   fg="white", bg="green")
        countdown_label.pack()

        if self.unlock_countdown_id:
            self.root.after_cancel(self.unlock_countdown_id)
            self.unlock_countdown_id = None

        def update_countdown(count):
            if not countdown_label.winfo_exists():
                return
            countdown_label.config(text=f"Locking in {count} seconds...")
            if count > 0:
                self.root.after(1000, update_countdown, count - 1)
            else:
                self.show_lock_screen()

        unlock_time, _ = load_unlock_lock_times()
        update_countdown(unlock_time)

    def show_lock_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="red")

        tk.Label(self.root, text="Door Locked", font=("Helvetica", 40, "bold"),
                 fg="white", bg="red").pack(pady=(80, 20))

        countdown_label = tk.Label(self.root, text="", font=("Helvetica", 24),
                                   fg="white", bg="red")
        countdown_label.pack()

        def update_countdown(count):
            if not countdown_label.winfo_exists():
                return
            countdown_label.config(text=f"Returning in {count} seconds...")
            if count > 0:
                self.root.after(1000, update_countdown, count - 1)
            else:
                self.restore_and_show_main_menu()

        update_countdown(5)

    def exit_to_desktop(self):
        print("Exiting to Desktop...")
        power_manager.stop_idle_timer()
        power_manager.turn_screen_on()
        self.camera.stop()
        door_lock.cleanup()
        self.root.destroy()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = TouchscreenUI(root)
    root.mainloop()