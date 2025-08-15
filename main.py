from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pydantic import BaseModel
import uvicorn

from db import *
app = FastAPI()


# Настройка CORS для доступа с любых источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RunStatus(BaseModel):
    device_id: str

class RegNewDev(BaseModel):
    device_id: str
    mac: str
    ipAddress: str


'''
    Сделать так что если устроство не зарегестированно,
    то оно не будет принимать и получать запросы.

    Проверить задержки и сделать так что бы они были настраиваемыми через /reg.
    Обратная отправка команды которая будет настраивать время запросов.
'''

'''
    Написать код для чтения температуры и выводить хотя бы в консоль.
    Добиться стабильного подключения.
'''

@app.post("/reg")
async def handle_button(status: RegNewDev):
    print(f"Received registration:")
    print(f"  Device ID: {status.device_id}")
    print(f"  MAC: {status.mac}")
    print(f"  IP: {status.ipAddress}")
    add_item(status.device_id, status.mac, status.ipAddress)
    return {"status": "success", "state": "ok"}

@app.post("/run_status")
async def status_esp(status: RunStatus):
    update_time(status.device_id, datetime.now())
    return {"run_status": "run"}



'''
    Сделать эту функция как индикатор подключения к серверу
'''

@app.get("/led_control/{device_id}")
async def get_status(device_id: str):
    #update_time(device_id, datetime.now())
    status_command = get_status_by_id(device_id)
    return {
        "status": status_command
    }

@app.get("/all_device")
def get_all_device_statuses_endpoint():
    return get_all_device_statuses()




if __name__ == "__main__":
    create_database()
    uvicorn.run(app, host="0.0.0.0", port=8000)