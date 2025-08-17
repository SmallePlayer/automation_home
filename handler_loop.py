from datetime import datetime
from db import *




def update_status_device(device_id):
    last_time = get_datatime_by_id(device_id)
    if last_time:
        time_diff = datetime.now() - last_time
        seconds_diff = time_diff.total_seconds()
        print(f"Устройство {device_id}: прошло {seconds_diff:.2f} секунд")
        if seconds_diff < 3: update_condition(device_id, "on")
        else: update_condition(device_id, "off")


if __name__ == "__main__":
    while True:
        # Получаем список всех устройств
        devices = get_all_device_id()

        # Извлекаем только device_id из каждого словаря
        device_ids = [device["device_id"] for device in devices]

        print("Найдены устройства:", device_ids)

        # Обновляем статус для каждого устройства по очереди
        for device_id in device_ids:
            update_status_device(device_id)
