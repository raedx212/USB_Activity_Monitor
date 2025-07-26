import wmi
import winsound
import colorama
import threading
import time
import getpass
import pyfiglet
from datetime import datetime

displayed_devices_ids = set() # لتتبع الأجهزة اللي تم عرضها

first_run = True

from colorama import init, Fore, Style
init(autoreset=True)


#تظهراسم البرنامج بشكل كبير وجذاب أول ما يشتغل البرنامج
def show_banner():
    ascii_banner = pyfiglet.figlet_format("Connected USB Devices", font="slant")
    print(Fore.BLUE + ascii_banner)
    print(Fore.RED + f"\nConnected USB Devices:\n")


# دالة تسحب الأجهزة المتصلة من النظام باستخدام WMI
def get_connected_usb_devices():
     wmi_conn = wmi.WMI()
     return wmi_conn.Win32_PnPEntity()
    

# دالة تطبع معلومات كل جهاز بشكل مرتب
def print_usb_devices(devices):
    current_user = getpass.getuser()
    

    for device in devices:

        # هذي السطور تتأكد إذا المعلومة موجودة، وإذا لا تطبع "Unknown"
        name = device.Name or "Unknown"
        manufacturer = getattr(device, 'Manufacturer', 'Unknown') or "Unknown"
        pnp_id = getattr(device, 'PNPDeviceID', 'Unknown') or "Unknown"

        # هذي السطور تطبع المعلومات بصيغة واضحة وسطر سطر
        print(f"Device Name     : {name}")
        print(f"Manufacturer    : {manufacturer}")
        print(f"Device ID       : {pnp_id}")
        print(f"User            : {current_user}")
        print(f"Detected At     : {datetime.now()}")
        print(Fore.GREEN + "-" * 60)


# هذا هو مدخل البرنامج: ما يشتغل إلا إذا شغلت الملف مباشرة
def main_loop():

    global first_run

    while True:
            devices = get_connected_usb_devices()
            new_devices = []

            for device in devices:
                if "USB" in (device.Name or ""):
                    pnp_id = getattr(device, 'DeviceID', 'Unknown') or "Unknown"
                    if pnp_id not in displayed_devices_ids:
                        displayed_devices_ids.add(pnp_id)
                        new_devices.append(device)
            if new_devices:
                winsound.Beep(523, 150) # تنبيه صوتي
                print_usb_devices(new_devices)

            if first_run:
                print(Fore.RED + "\n[!]Press Enter to exit...\n")
            first_run = False
            
            

            time.sleep(3)


# نشغل المراقبة في خيط منفصل       
def start_monitoring():
    monitor_thread = threading.Thread(target=main_loop, daemon=True)
    monitor_thread.start()

    # نطبع الرسالة للمستخدم
    input()
    print(Fore.RED + "[✔] Program exited successfully.")



if __name__ == "__main__":
    show_banner()
    start_monitoring()
    



