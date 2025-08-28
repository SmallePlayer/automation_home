import requests
import time
from datetime import datetime
import sqlite3

def get_printer_status(PRINTER_IP):
    url = f"http://{PRINTER_IP}:{PORT}/printer/objects/query?print_stats&display_status&extruder&heater_bed"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Извлекаем данные из ответа
        print_stats = data['result']['status']['print_stats']
        display_status = data['result']['status']['display_status']
        extruder = data['result']['status']['extruder']
        heater_bed = data['result']['status']['heater_bed']
        
        # Форматируем вывод
        status_message = f"""
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Состояние: {print_stats['state']}
Файл: {print_stats.get('filename', 'N/A')}
Прогресс: {display_status['progress']*100:.1f}%
Температура сопла: {extruder['temperature']:.1f}°C / {extruder['target']:.1f}°C
Температура стола: {heater_bed['temperature']:.1f}°C / {heater_bed['target']:.1f}°C
"""
        print(status_message)
        
        return PRINTER_IP, PORT, print_stats['state'], extruder['temperature'], heater_bed['temperature']

    except Exception as e:
        print(f"Ошибка подключения: {e}")

def create_database():
    conn = sqlite3.connect('printers3D.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS printers3D (
                 ip TEXT NOT NULL,
                 port TEXT NOT NULL,
                 status TEXT NOT NULL,
                 temp_extruder INTEGER,
                 temp_header_bed INTEGER)''')
    conn.commit()
    conn.close()

def add_printer(ip, port, status, temp_extruder, temp_header_bed):
    create_database()
    try:
        conn = sqlite3.connect('printers3D.db')
        c = conn.cursor()
        c.execute("INSERT INTO printers3D  (ip, port, status, temp_extruder, temp_header_bed) VALUES ( ?, ?, ?, ?, ?)",
                 ( ip, port, status, temp_extruder, temp_header_bed))
        conn.commit()
        print(f"Устройство {ip} ({port}) успешно добавлено")
    except sqlite3.IntegrityError as e:
        print(f"Ошибка добавления: {e}")
    finally:
        conn.close()

def update_db(ip, port, status, temp_extruder, temp_header_bed):
    try:
        conn = sqlite3.connect('printers3D.db')
        c = conn.cursor()
        c.execute("UPDATE printers3D SET status = ?, temp_extruder = ?, temp_header_bed = ? WHERE ip = ?",
                  (status, temp_extruder, temp_header_bed, ip))

        if c.rowcount == 0:
            print(f"Принтер не найден")
            conn.close()
            return False

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"Ошибка обновления: {e}")
        return False

if __name__ == "__main__":
    print("Мониторинг состояния принтера (Ctrl+C для остановки)")
    while True:
        for i in range(69,71):
            PRINTER_IP = "192.168.1."   # Замените на IP-адрес вашего принтера
            PORT = 80                   # Стандартный порт Moonraker
            PRINTER_IP = PRINTER_IP + str(i)

            ip, port, status, temp_extruder, temp_header_bed = get_printer_status(PRINTER_IP)
            add_printer(ip, port, status, temp_extruder, temp_header_bed) 
            _ = update_db(ip, port, status, temp_extruder, temp_header_bed)
            
            time.sleep(3)  # Интервал опроса в секундах