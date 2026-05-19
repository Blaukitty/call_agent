from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time

app = FastAPI()

# Разрешаем HTML-странице делать запросы к API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение к PostgreSQL с ожиданием (пока база поднимется в Docker)
def get_db_connection():
    for _ in range(10):
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "database"),
                database=os.getenv("DB_NAME", "doctrine_db"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "secret")
            )
            return conn
        except psycopg2.OperationalError:
            time.sleep(2)
    raise Exception("Не удалось подключиться к базе данных")

# Модель данных для обновления статуса клиента
class UpdateStatus(BaseModel):
    status: str

# 1. Получить список всех клиентов
@app.get("/clients")
def get_clients():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM clients ORDER BY id;")
    clients = cur.fetchall()
    cur.close()
    conn.close()
    return clients

# 2. Получить фразы скрипта обзвона
@app.get("/script/{step_name}")
def get_script_step(step_name: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM scripts WHERE step_name = %s;", (step_name,))
    step = cur.fetchone()
    cur.close()
    conn.close()
    if not step:
        raise HTTPException(status_code=404, detail="Шаг скрипта не найден")
    return step

# 3. Изменить статус клиента
@app.put("/clients/{client_id}/status")
def update_client_status(client_id: int, data: UpdateStatus):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE clients SET status = %s WHERE id = %s;", (data.status, client_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Статус успешно обновлен"}
