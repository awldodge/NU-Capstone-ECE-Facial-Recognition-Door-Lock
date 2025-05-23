#log_settings_reboot
import csv
import os
from datetime import datetime, timedelta

SETTINGS_LOG_FILE = "settings_log.csv"

def purge_old_entries():
    cutoff_date = datetime.now() - timedelta(days=182)  # 6 months
    if not os.path.exists(SETTINGS_LOG_FILE):
        return

    with open(SETTINGS_LOG_FILE, "r") as infile:
        rows = list(csv.reader(infile))

    header = rows[0] if rows else []
    filtered = [row for row in rows[1:] if datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") >= cutoff_date]

    with open(SETTINGS_LOG_FILE, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        if header:
            writer.writerow(header)
        writer.writerows(filtered)
