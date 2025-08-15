import sqlite3
import customtkinter as ctk
import requests

# Настройки внешнего вида
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Конфигурация сетки
COLUMNS = 4
TILE_WIDTH = 200
TILE_HEIGHT = 180
PADDING = 15
HEADER_COLOR = "#2a3b4c"
TILE_COLOR = "#1a1a2e"
TEXT_COLOR = "#61dafb"

# Настройки сервера
SERVER_URL = "http://192.168.0.109:8000"  # Базовый URL сервера
HEADERS = {'Content-Type': 'application/json'}


def get_devices():
    """Получение списка устройств из базы данных"""
    try:
        conn = sqlite3.connect('devices.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, mac, ip FROM devices")
        devices = cursor.fetchall()
        conn.close()
        return devices
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return []


def send_command_to_server(command):
    """Отправка команды на центральный сервер"""
    try:
        endpoint = f"{SERVER_URL}/led_status"
        data = {
            "flag_current": command
        }

        response = requests.post(endpoint, json=data, headers=HEADERS, timeout=2)

        if response.status_code == 200:
            print(f"Команда {command} успешно отправлена")
            return True
        else:
            print(f"Ошибка! Статус-код: {response.status_code}")
            print("Текст ответа:", response.text)
            return False
    except requests.exceptions.RequestException as e:
        print(f"Ошибка соединения с сервером: {e}")
        return False


def create_device_tile(container, device, row, col):
    """Создание плитки для устройства с кнопкой ON/OFF"""
    device_id, mac, ip = device

    # Создаем фрейм плитки
    tile_frame = ctk.CTkFrame(
        container,
        width=TILE_WIDTH,
        height=TILE_HEIGHT,
        corner_radius=15,
        fg_color=TILE_COLOR,
        border_width=1,
        border_color="#444"
    )
    tile_frame.grid_propagate(False)
    tile_frame.grid(row=row, column=col, padx=PADDING, pady=PADDING)

    # Заголовок с ID
    header_frame = ctk.CTkFrame(tile_frame, fg_color=HEADER_COLOR, corner_radius=8)
    header_frame.pack(fill="x", padx=5, pady=(5, 0))

    id_label = ctk.CTkLabel(
        header_frame,
        text=f"ID: {device_id}",
        font=("Arial", 14, "bold"),
        text_color=TEXT_COLOR
    )
    id_label.pack(side="left", padx=5, pady=2)

    # Информация об устройстве
    info_frame = ctk.CTkFrame(tile_frame, fg_color="transparent")
    info_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # MAC-адрес
    mac_label = ctk.CTkLabel(
        info_frame,
        text=f"MAC: {mac}",
        font=("Arial", 11),
        anchor="w",
        justify="left"
    )
    mac_label.pack(fill="x", pady=(5, 0))

    # IP-адрес
    ip_label = ctk.CTkLabel(
        info_frame,
        text=f"IP: {ip}",
        font=("Arial", 11),
        anchor="w",
        justify="left"
    )
    ip_label.pack(fill="x", pady=(5, 0))

    # Фрейм для кнопки ON/OFF
    button_frame = ctk.CTkFrame(tile_frame, fg_color="transparent")
    button_frame.pack(fill="x", padx=10, pady=(0, 10))

    # Переменная состояния для кнопки (False = OFF, True = ON)
    button_state = False

    def toggle_button():
        """Функция переключения состояния и отправки команды на сервер"""
        nonlocal button_state
        button_state = not button_state

        # Определяем команду для сервера
        command = "on" if button_state else "off"

        # Отправляем команду на сервер
        success = send_command_to_server(command)

        if success:
            # Обновляем вид кнопки только при успешной отправке
            if button_state:
                action_btn.configure(text="ON", fg_color="#2E8B57", hover_color="#3CB371")
            else:
                action_btn.configure(text="OFF", fg_color="#FF6347", hover_color="#FF4500")
        else:
            # Возвращаем предыдущее состояние при ошибке
            button_state = not button_state

    # Создаем кнопку ON/OFF
    action_btn = ctk.CTkButton(
        button_frame,
        text="OFF",
        width=100,
        height=30,
        corner_radius=10,
        font=("Arial", 11),
        fg_color="#FF6347",  # Начальный цвет - красный (OFF)
        hover_color="#FF4500",
        command=toggle_button
    )
    action_btn.pack(side="right", padx=5)

    return tile_frame


def main():
    """Основная функция приложения"""
    # Создаем главное окно
    app = ctk.CTk()
    app.title("Управление устройствами через сервер")
    app.geometry("950x700")

    # Заголовок приложения
    header_frame = ctk.CTkFrame(app, fg_color="#1e3c5a")
    header_frame.pack(fill="x", padx=10, pady=10)

    header_label = ctk.CTkLabel(
        header_frame,
        text="УПРАВЛЕНИЕ УСТРОЙСТВАМИ ЧЕРЕЗ СЕРВЕР",
        font=("Arial", 22, "bold"),
        text_color="#61dafb"
    )
    header_label.pack(pady=15)

    # Информация о сервере
    server_info = ctk.CTkLabel(
        header_frame,
        text=f"Сервер управления: {SERVER_URL}",
        font=("Arial", 14),
        text_color="#90EE90"
    )
    server_info.pack(pady=(0, 10))

    # Получаем устройства из БД
    devices = get_devices()

    if not devices:
        # Сообщение если нет устройств
        empty_frame = ctk.CTkFrame(app, fg_color="transparent")
        empty_frame.pack(fill="both", expand=True)

        empty_label = ctk.CTkLabel(
            empty_frame,
            text="В базе данных нет устройств",
            font=("Arial", 18),
            text_color="#FF6347"
        )
        empty_label.pack(pady=50)
    else:
        # Создаем скроллируемую область
        scroll_frame = ctk.CTkScrollableFrame(app)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Контейнер для сетки
        grid_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        grid_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Создаем плитки для каждого устройства
        for i, device in enumerate(devices):
            row = i // COLUMNS
            col = i % COLUMNS
            create_device_tile(grid_container, device, row, col)

    # Запускаем приложение
    app.mainloop()


if __name__ == "__main__":
    main()