from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class UpdateStatus(BaseModel):
    status: str
    
@app.get("/clients")
def get_clients():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM clients ORDER BY id;")
    clients = cur.fetchall()
    cur.close()
    conn.close()
    return clients

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

@app.put("/clients/{client_id}/status")
def update_client_status(client_id: int, data: UpdateStatus):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE clients SET status = %s WHERE id = %s;", (data.status, client_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Статус успешно обновлен"}
