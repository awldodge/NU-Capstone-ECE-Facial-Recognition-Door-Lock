#settings_log_screen.py
import tkinter as tk
import csv
from datetime import datetime, timedelta

LOG_FILE = "settings_log.csv"

ROW_HEIGHT = 34
HEADER_HEIGHT = 40
VISIBLE_ROWS = 8

def show_screen(root, go_back_callback, go_to_access_log_callback):
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="#000000")
    frame = tk.Frame(root, bg="#000000")
    frame.pack(fill=tk.BOTH, expand=True)

    # Title
    title = tk.Label(frame, text="Settings Logs (Last 2 Weeks)", font=("Helvetica", 20, "bold"),
                     fg="white", bg="#000000")
    title.pack(pady=10)

    showing_six_months = [False]
    log_data = []

    # Table container
    center_container = tk.Frame(frame, bg="#000000")
    center_container.pack()

    table_frame = tk.Frame(center_container, bg="white", bd=2, relief="solid")
    table_frame.pack(pady=10, padx=20)

    # Column layout settings
    headers = ["Timestamp", "Action", "Details"]
    col_widths = [180, 150, 300]  # in pixels
    header_font = ("Helvetica", 14, "bold")
    row_font = ("Helvetica", 12)
    total_width = sum(col_widths)

    # Fixed header canvas (always visible)
    header_canvas = tk.Canvas(table_frame, bg="white", width=total_width, height=HEADER_HEIGHT, highlightthickness=0)
    header_canvas.pack(side="top", fill="x")

    def draw_static_headers():
        header_canvas.delete("all")
        x = 0
        for i, header in enumerate(headers):
            w = col_widths[i]
            header_canvas.create_rectangle(x, 0, x + w, HEADER_HEIGHT, fill="#333333", outline="black")
            anchor = "w" if i == 2 else "center"
            tx = x + 10 if i == 2 else x + w // 2
            header_canvas.create_text(tx, HEADER_HEIGHT // 2, text=header, font=header_font,
                                      fill="white", anchor=anchor)
            x += w

    # Canvas and scrollbar
    canvas_height = ROW_HEIGHT * VISIBLE_ROWS
    canvas = tk.Canvas(table_frame, bg="white", highlightthickness=0, width=total_width, height=canvas_height)
    v_scrollbar = tk.Scrollbar(table_frame, orient="vertical")
    canvas.configure(yscrollcommand=v_scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    v_scrollbar.pack(side="right", fill="y")

    scroll_position = [0]

    def on_scroll(*args):
        canvas.yview(*args)
        current = int(canvas.yview()[0] * len(log_data))
        if abs(current - scroll_position[0]) >= 1:
            scroll_position[0] = current
            render_visible_rows()

    canvas.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.config(command=on_scroll)
    canvas.bind("<MouseWheel>", lambda e: on_scroll("scroll", int(-1 * (e.delta / 120)), "units"))

    def load_filtered_logs(days):
        try:
            with open(LOG_FILE, newline='') as csvfile:
                reader = csv.reader(csvfile)
                cutoff = datetime.now() - timedelta(days=days)
                filtered = []
                for row in reader:
                    if len(row) < 1:
                        continue
                    try:
                        timestamp = row[0]
                        if timestamp[0:4].isdigit():
                            ts = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                            if ts >= cutoff:
                                filtered.append(row)
                    except Exception:
                        continue
                return filtered
        except FileNotFoundError:
            return []

    def render_visible_rows():
        canvas.delete("row")
        if not log_data:
            return
        view_start_frac, _ = canvas.yview()
        total_height = len(log_data) * ROW_HEIGHT
        start_pixel = view_start_frac * total_height
        start_row = int(start_pixel // ROW_HEIGHT)
        end_row = min(start_row + VISIBLE_ROWS + 2, len(log_data))

        for draw_index, i in enumerate(range(start_row, end_row)):
            row = log_data[i]
            bg_color = "#f0f0f0" if i % 2 == 0 else "#ffffff"
            y = (start_row + draw_index) * ROW_HEIGHT
            x = 0
            for j in range(3):
                text = row[j] if j < len(row) else ""
                w = col_widths[j]
                canvas.create_rectangle(x, y, x + w, y + ROW_HEIGHT, fill=bg_color, outline="gray", tags="row")
                anchor = "w" if j == 2 else "center"
                tx = x + 10 if j == 2 else x + w // 2
                canvas.create_text(tx, y + ROW_HEIGHT // 2, text=text,
                                   font=row_font, fill="black", anchor=anchor,
                                   width=w - 20 if j == 2 else None, tags="row")
                x += w
            
        print(f"Rendering rows {start_row} to {end_row} of {len(log_data)}")
        print(f"y={y} for row {i} of {len(log_data)}")
        
    def refresh_display():
        nonlocal log_data
        days = 182 if showing_six_months[0] else 14
        log_data = load_filtered_logs(days)
        log_data.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d %H:%M:%S"), reverse=True)
        total_height = len(log_data) * ROW_HEIGHT
        canvas.configure(scrollregion=(0, 0, total_width, total_height))
        draw_static_headers()
        render_visible_rows()
        title.config(text="Settings Logs (Last 6 Months)" if showing_six_months[0]
                     else "Settings Logs (Last 2 Weeks)")

    refresh_display()

    # Button bar22
    button_frame = tk.Frame(frame, bg="#000000")
    button_frame.pack(pady=(5,15))
    inner_frame = tk.Frame(button_frame, bg="#000000")
    inner_frame.pack()

    tk.Button(button_frame, text="Return to View Logs Screen", command=go_back_callback,
              font=("Helvetica", 14), width=24, bg="#66cc66", fg="white",
              activebackground="#99e699").pack(side="left", padx=15)

    def toggle_log_range():
        showing_six_months[0] = not showing_six_months[0]
        refresh_display()

    tk.Button(button_frame, text="Toggle 2wks / 6mos", command=toggle_log_range,
              font=("Helvetica", 14), width=24, bg="#ffcc00", fg="black",
              activebackground="#ffe066").pack(side="right", padx=15)