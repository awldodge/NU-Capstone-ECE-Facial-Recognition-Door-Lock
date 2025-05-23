# system_info_screen.py
import tkinter as tk
import os
import socket
import subprocess
from datetime import datetime

SETTINGS_PATH = "/home/awldodge/CEE499_Capstone/Touchscreen/settings.json"

def get_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m"
    except:
        return "Unavailable"

def get_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Unavailable"

def get_cpu_temp():
    try:
        output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        celsius = float(output.strip().split('=')[1].replace("'C", ""))
        fahrenheit = (celsius * 9 / 5) + 32
        return f"{celsius:.1f}°C / {fahrenheit:.1f}°F"
    except:
        return "Unavailable"

def get_disk_usage():
    try:
        stat = os.statvfs('/')
        free = stat.f_bavail * stat.f_frsize / (1024 * 1024)
        total = stat.f_blocks * stat.f_frsize / (1024 * 1024)
        return f"{int(free)}MB free / {int(total)}MB total"
    except:
        return "Unavailable"

def get_last_reboot():
    try:
        output = subprocess.check_output(['uptime', '-s']).decode().strip()
        return output
    except:
        return "Unavailable"

def get_system_datetime():
    try:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Unavailable"

def show_screen(root, go_back_callback):
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="black")

    title = tk.Label(root, text="System Information", font=("Helvetica", 32, "bold"),
                     fg="white", bg="black")
    title.pack(pady=(30, 20))

    # StringVars
    cpu_var = tk.StringVar()
    uptime_var = tk.StringVar()
    time_var = tk.StringVar()

    # Static values
    disk_usage = get_disk_usage()
    ip_address = get_ip()
    last_reboot = get_last_reboot()

    # Function to center a full line
    def make_line(var, font=("Helvetica", 18)):
        return tk.Label(root, textvariable=var, font=font, fg="white", bg="black", justify="center")

    # Set initial values
    cpu_var.set(f"CPU Temp: {get_cpu_temp()}")
    uptime_var.set(f"Uptime: {get_uptime()}")
    time_var.set(f"System Time: {get_system_datetime()}")

    disk_label = tk.Label(root, text=f"Disk Usage: {disk_usage}", font=("Helvetica", 18), fg="white", bg="black")
    ip_label = tk.Label(root, text=f"IP Address: {ip_address}", font=("Helvetica", 18), fg="white", bg="black")
    reboot_label = tk.Label(root, text=f"Last Reboot: {last_reboot}", font=("Helvetica", 18), fg="white", bg="black")

    # Pack centered lines
    make_line(cpu_var).pack(pady=5)
    make_line(uptime_var).pack(pady=5)
    make_line(time_var).pack(pady=5)
    disk_label.pack(pady=5)
    ip_label.pack(pady=5)
    reboot_label.pack(pady=5)

    # Update live values
    def update():
        cpu_var.set(f"CPU Temp: {get_cpu_temp()}")
        uptime_var.set(f"Uptime: {get_uptime()}")
        time_var.set(f"System Time: {get_system_datetime()}")
        root.after(1000, update)

    update()

    # Green back button
    back_button = tk.Button(root, text="Return to Settings Screen",
                            font=("Helvetica", 16, "bold"),
                            fg="white", bg="green", activebackground="darkgreen",
                            highlightthickness=2, highlightbackground="white",
                            width=28, height=2, command=go_back_callback)
    back_button.pack(pady=30)
