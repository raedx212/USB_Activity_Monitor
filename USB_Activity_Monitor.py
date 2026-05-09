import logging
import wmi
import winsound
import colorama
import threading
import time
import getpass
import pyfiglet
from datetime import datetime
import json

# Track displayed devices during runtime
displayed_devices_ids = set()

first_run = True

TRUSTED_FILE = "trusted_devices.json"
trusted_devices = []

from colorama import init, Fore, Style
init(autoreset=True)

# Logging setup
logging.basicConfig(
    filename="usb_activity.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# System devices to ignore (not real external USB)
SYSTEM_IGNORE = [
    "ROOT_HUB",
    "Host Controller",
    "Generic USB",
    "Intel",
    "USB Root Hub",
    "xHCI",
]


# Load trusted devices from file
def load_trusted_devices():
    try:
        with open(TRUSTED_FILE, "r") as f:
            return json.load(f)
    except:
        return []


# Save trusted devices to file
def save_trusted_devices(devices):
    with open(TRUSTED_FILE, "w") as f:
        json.dump(devices, f)


# Setup menu (add/remove trusted devices)
def setup_menu():
    devices = load_trusted_devices()

    while True:
        print("\n--- SETUP MENU ---")
        print("1 - Start Program")
        print("2 - Manage Trusted Devices")
        print("3 - View Trusted Devices")  # NEW

        choice = input("Choose: ")

        if choice == "1":
            return devices

        elif choice == "2":
            print("\n1 - Add Device")
            print("2 - Remove Device")
            sub = input("Choose: ")

            if sub == "1":
                new_id = input("Enter Device ID: ")
                devices.append(new_id)
                save_trusted_devices(devices)
                print("Device added.")

            elif sub == "2":
                print(devices)
                del_id = input("Enter Device ID to remove: ")

                if del_id in devices:
                    devices.remove(del_id)
                    save_trusted_devices(devices)
                    print("Device removed.")
                else:
                    print("Not found.")

        elif choice == "3":
            print("\n--- Trusted Devices List ---")
            if len(devices) == 0:
                print("No trusted devices yet.")
            else:
                for i, dev in enumerate(devices, 1):
                    print(f"{i}. {dev}")


# Show banner
def show_banner():
    ascii_banner = pyfiglet.figlet_format("USB Monitor", font="slant")
    print(Fore.BLUE + ascii_banner)
    print(Fore.RED + "\nConnected USB Devices:\n")


# Get USB devices
def get_connected_usb_devices():
    wmi_conn = wmi.WMI()
    return wmi_conn.Win32_PnPEntity()


# Print device info
def print_usb_devices(devices):
    current_user = getpass.getuser()

    for device, is_system in devices:

        name = device.Name or "Unknown"
        manufacturer = getattr(device, 'Manufacturer', 'Unknown') or "Unknown"
        pnp_id = getattr(device, 'PNPDeviceID', 'Unknown') or "Unknown"

        print(f"Device Name     : {name}")
        print(f"Manufacturer    : {manufacturer}")
        print(f"Device ID       : {pnp_id}")
        print(f"User            : {current_user}")
        print(f"Detected At     : {datetime.now()}")
        print(Fore.GREEN + "-" * 60)

        # Only alert for real external devices
        if not is_system and pnp_id not in trusted_devices:
            print(Fore.RED + "[ALERT] Unknown External USB Device Detected!")
            winsound.Beep(1000, 200)

        # Log everything
        logging.info(
            f"USB Event | Name: {name} | System: {is_system} | Device ID: {pnp_id} | User: {current_user}"
        )


def main_loop():
    global first_run

    while True:
        devices = get_connected_usb_devices()
        new_devices = []

        for device in devices:

            name = device.Name or ""

            if "USB" in name:

                pnp_id = getattr(device, 'DeviceID', 'Unknown') or "Unknown"

                # Check if system device
                is_system = any(x in name for x in SYSTEM_IGNORE)

                if pnp_id not in displayed_devices_ids:
                    displayed_devices_ids.add(pnp_id)
                    new_devices.append((device, is_system))

        if new_devices:
            winsound.Beep(523, 150)
            print_usb_devices(new_devices)

        if first_run:
            print(Fore.RED + "\n[!] Press Enter to exit...\n")
            first_run = False

        time.sleep(3)


# Start monitoring
def start_monitoring():
    monitor_thread = threading.Thread(target=main_loop, daemon=True)
    monitor_thread.start()

    input()
    print(Fore.RED + "[✔] Program exited successfully.")


# Entry point
if __name__ == "__main__":
    show_banner()
    trusted_devices = setup_menu()
    start_monitoring()
