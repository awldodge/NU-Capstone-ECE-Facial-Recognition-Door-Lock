# access_log.py
import csv
import os
from datetime import datetime

LOG_FILE = "/home/awldodge/CEE499_Capstone/Touchscreen/access_log.csv"

def log_access(method, status):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, mode='a', newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, method, status])
