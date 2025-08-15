import sqlite3
from datetime import datetime

def create_database():
    conn = sqlite3.connect('devices.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS devices (
                 device_id TEXT PRIMARY KEY,
                 mac TEXT NOT NULL UNIQUE,
                 ip TEXT NOT NULL UNIQUE,
                 status TEXT NOT NULL DEFAULT 'off',
                 condition TEXT NOT NULL DEFAULT 'off',
                 last_work_time TEXT)''')
    conn.commit()
    conn.close()

def add_item(device_id, mac_address, ip_address):
    create_database()
    try:
        conn = sqlite3.connect('devices.db')
        c = conn.cursor()
        c.execute("INSERT INTO devices (device_id, mac, ip, status, condition) VALUES (?, ?, ?, 'off', 'off')",
                 (device_id, mac_address, ip_address))
        conn.commit()
        print(f"Устройство {mac_address} ({ip_address}) успешно добавлено")
    except sqlite3.IntegrityError as e:
        print(f"Ошибка добавления: {e}")
    finally:
        conn.close()


def update_status(device_id, status):
    try:
        conn = sqlite3.connect('devices.db')
        c = conn.cursor()

        # Обновляем статус по MAC-адресу
        c.execute("UPDATE devices SET status = ? WHERE device_id = ?",
                  (status, device_id))

        if c.rowcount == 0:
            print(f"Устройство с device_id {device_id} не найдено")
            conn.close()
            return False

        conn.commit()
        print(f"Статус устройства {device_id} обновлен на '{status}'")
        return True
    except sqlite3.Error as e:
        print(f"Ошибка обновления статуса: {e}")
        return False
    finally:
        conn.close()

def update_time(device_id, dataTime):
    try:
        conn = sqlite3.connect('devices.db')
        c = conn.cursor()

        timestamp_str = dataTime.strftime("%Y-%m-%d %H:%M:%S")
        # Используем UPSERT для обновления или создания записи
        c.execute("UPDATE devices SET last_work_time = ? WHERE device_id = ?", (timestamp_str, device_id))

        if c.rowcount == 0:
            print(f"Устройство с device_id {device_id} не найдено")
            conn.close()
            return False

        conn.commit()
        print(f"Время устройства {device_id} обновлен на '{dataTime}'")
        return True
    except sqlite3.Error as e:
        print(f"Ошибка обновления времени: {e}")
        return False
    finally:
        conn.close()

def update_condition(device_id, condit):
    try:
        conn = sqlite3.connect('devices.db')
        c = conn.cursor()

        # Используем UPSERT для обновления или создания записи
        c.execute("UPDATE devices SET condition = ? WHERE device_id = ?", (condit, device_id))

        if c.rowcount == 0:
            print(f"Устройство с device_id {device_id} не найдено")
            conn.close()
            return False

        conn.commit()
        print(f"Состояние устройства {device_id} обновлен на '{condit}'")
        return True
    except sqlite3.Error as e:
        print(f"Ошибка обновления состояния: {e}")
        return False
    finally:
        conn.close()


def get_status_by_id(device_id):
    try:
        conn = sqlite3.connect('devices.db')
        c = conn.cursor()

        # Выполняем запрос к базе данных
        c.execute("SELECT status FROM devices WHERE device_id = ?", (device_id,))
        result = c.fetchone()

        if result:
            return result[0]  # Возвращаем статус (первый элемент кортежа)
        else:
            print(f"Устройство с ID {device_id} не найдено")
            return None

    except sqlite3.Error as e:
        print(f"Ошибка при получении статуса: {e}")
        return None
    finally:
        conn.close()

def get_datatime_by_id(device_id):
    try:
        conn = sqlite3.connect('devices.db')
        c = conn.cursor()

        # Выполняем запрос к базе данных
        c.execute("SELECT last_work_time FROM devices WHERE device_id = ?", (device_id,))
        result = c.fetchone()

        if result and result[0] is not None:
            # Проверяем тип данных - если это уже datetime, возвращаем как есть
            if isinstance(result[0], datetime):
                return result[0]

            # Если это строка, преобразуем в datetime
            if isinstance(result[0], str):
                try:
                    return datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # Попробуем альтернативный формат
                    return datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S.%f")

            # Если это timestamp (число)
            if isinstance(result[0], (int, float)):
                return datetime.fromtimestamp(result[0])

            # Если значение отсутствует или не распознано
        return None

    except sqlite3.Error as e:
        print(f"Ошибка при получении статуса: {e}")
        return None
    finally:
        conn.close()


def get_all_device_statuses():
    try:
        conn = sqlite3.connect('devices.db')
        cursor = conn.cursor()

        # Выбираем только нужные поля
        cursor.execute("SELECT device_id, status FROM devices")
        rows = cursor.fetchall()

        # Форматируем результат в требуемый вид
        result = [
            {"device_id": row[0], "status": row[1]}
            for row in rows
        ]
        return result

    except sqlite3.Error as e:
        print(f"Ошибка при получении статусов устройств: {e}")
        return []
    finally:
        conn.close()


'''
    Проверить работу этой функции
'''

def get_all_device_id():
    try:
        conn = sqlite3.connect('devices.db')
        cursor = conn.cursor()

        # Выбираем только нужные поля
        cursor.execute("SELECT device_id FROM devices")
        rows = cursor.fetchall()

        # Форматируем результат в требуемый вид
        result = [
            {"device_id": row[0]}  for row in rows
        ]
        return result

    except sqlite3.Error as e:
        print(f"Ошибка при получении статусов устройств: {e}")
        return []
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()
