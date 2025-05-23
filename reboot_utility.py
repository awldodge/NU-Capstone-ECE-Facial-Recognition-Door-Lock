#reboot_utility
import os
import csv
import subprocess
from datetime import datetime, timedelta

SETTINGS_LOG_FILE = "settings_log.csv"
LOG_FILES = ["access_log.csv", "settings_log.csv"]
PURGE_DAYS = 182  # 6 months

def purge_old_log_entries():
    cutoff = datetime.now() - timedelta(days=PURGE_DAYS)
    for log_file in LOG_FILES:
        if not os.path.exists(log_file):
            continue

        temp_rows = []
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as infile:
                reader = csv.reader((line.replace('\x00', '') for line in infile))
                for row in reader:
                    try:
                        timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                        if timestamp >= cutoff:
                            temp_rows.append(row)
                    except (IndexError, ValueError):
                        temp_rows.append(row)  # keep malformed rows
        except Exception as e:
            print(f"Error processing {log_file}: {e}")
            continue

        with open(log_file, "w", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerows(temp_rows)

def clean_journal_logs():
    subprocess.call(["sudo", "journalctl", "--vacuum-time=7d"])
    subprocess.call(["sudo", "journalctl", "--vacuum-size=100M"])

def log_reboot(source="Manual"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SETTINGS_LOG_FILE, "a", newline="") as log:
        writer = csv.writer(log)
        writer.writerow([timestamp, "System", f"{source} reboot with log cleanup"])

def reboot_system():
    subprocess.call(["sudo", "reboot"])

def perform_full_reboot(source="Manual"):
    clean_journal_logs()
    purge_old_log_entries()
    log_reboot(source)
    reboot_system()
