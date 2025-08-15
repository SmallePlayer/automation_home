from db import update_status
import requests
import customtkinter as ctk

serverUrl = "http://192.168.0.109:8000/all_device/"



def get_all_device():
    response = requests.get(serverUrl)
    response.raise_for_status()
    return response.json()


stats = get_all_device()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Создаем главное окно
window = ctk.CTk()
window.title("Device Control Panel")
window.geometry("400x600")

# Главный скроллируемый фрейм для устройств
main_frame = ctk.CTkScrollableFrame(window)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)


# Функция для переключения состояния конкретного устройства
def toggle_device(device_id, button):
    current_text = button.cget("text")
    if current_text == "ON":
        new_text = "OFF"
        new_fg_color = "#FF6347"  # Красный
        new_hover_color = "#FF4500"  # Темно-красный
        new_status = "off"
    else:
        new_text = "ON"
        new_fg_color = "#2E8B57"  # Зеленый
        new_hover_color = "#3CB371"  # Светло-зеленый
        new_status = "on"

    button.configure(text=new_text, fg_color=new_fg_color, hover_color=new_hover_color)
    update_status(device_id, new_status)


# Создаем элементы интерфейса для каждого устройства
for device in stats:
    # Фрейм для отдельного устройства
    device_frame = ctk.CTkFrame(main_frame)
    device_frame.pack(fill="x", pady=10, padx=5)

    # Метка с именем устройства
    label = ctk.CTkLabel(
        device_frame,
        text=device['device_id'],
        font=("Arial", 14, "bold"),
        width=120,
        anchor="w"
    )
    label.pack(side="left", padx=(10, 20), pady=10)

    # Определяем начальное состояние кнопки
    initial_status = device['status']
    if initial_status == "on":
        btn_text = "ON"
        btn_fg_color = "#2E8B57"
        btn_hover_color = "#3CB371"
    else:
        btn_text = "OFF"
        btn_fg_color = "#FF6347"
        btn_hover_color = "#FF4500"

    # Кнопка переключения состояния
    button = ctk.CTkButton(
        device_frame,
        text=btn_text,
        width=100,
        height=40,
        font=("Arial", 12, "bold"),
        fg_color=btn_fg_color,
        hover_color=btn_hover_color,
        corner_radius=8
    )
    # Привязываем команду с конкретным device_id
    button.configure(
        command=lambda dev_id=device['device_id'], btn=button: toggle_device(dev_id, btn)
    )
    button.pack(side="right", padx=10, pady=10)

# Запускаем главный цикл
window.mainloop()