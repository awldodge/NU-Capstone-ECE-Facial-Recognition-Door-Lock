# simulate_logs.py
import csv
from datetime import datetime, timedelta
import random

# Paths
access_log_path = "/home/awldodge/CEE499_Capstone/Touchscreen/access_log.csv"
settings_log_path = "/home/awldodge/CEE499_Capstone/Touchscreen/settings_log.csv"

# Simulate 190 days, starting from 190 days ago to today
days_to_simulate = 190

# Sample data
users = ["Alex", "Catherine", "Unknown"]
methods = ["Face", "PIN", "Admin"]
access_actions = ["Access Granted", "Access Denied"]
settings_actions = ["Settings Changed", "PIN Updated"]

def generate_logs(log_path, is_access_log):
    with open(log_path, "a", newline="") as file:
        writer = csv.writer(file)
        for offset in range(days_to_simulate):
            day = datetime.now() - timedelta(days=offset)
            timestamp = day.replace(hour=random.randint(0, 23),
                                    minute=random.randint(0, 59),
                                    second=random.randint(0, 59))
            if is_access_log:
                writer.writerow([
                    timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    random.choice(users),
                    random.choice(methods),
                    random.choice(access_actions)
                ])
            else:
                writer.writerow([
                    timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "System",
                    random.choice(settings_actions)
                ])

# Generate logs
generate_logs(access_log_path, is_access_log=True)
generate_logs(settings_log_path, is_access_log=False)
