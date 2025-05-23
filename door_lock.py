# door_lock.py
import RPi.GPIO as GPIO
import time
import threading

RELAY_PIN = 18  # GPIO18 = Pin 12
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)  # Ensure locked by default (HIGH = OFF)

def unlock_door(unlock_time=15):
    def _unlock_sequence():
        print("Relay ON (Unlocking door)")
        GPIO.output(RELAY_PIN, GPIO.LOW)  # Activate relay
        time.sleep(unlock_time)
        print("Relay OFF (Locking door)")
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # Deactivate relay

    threading.Thread(target=_unlock_sequence, daemon=True).start()

def cleanup():
    try:
        GPIO.setmode(GPIO.BCM) 
        GPIO.setup(RELAY_PIN, GPIO.OUT)
        GPIO.output(RELAY_PIN, GPIO.HIGH)
    except RuntimeError as e:
        print(f"[GPIO Cleanup] Warning: {e}")
    finally:
        GPIO.cleanup()

