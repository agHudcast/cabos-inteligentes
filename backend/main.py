from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "cabos")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "1234")
DB_PORT = os.getenv("DB_PORT", "5432")

data_log = []

class SensorData(BaseModel):
    dispositivo_id: str
    tensao: float
    corrente: float
    temperatura: float
    status: Optional[str] = "ok"
    timestamp: Optional[datetime] = datetime.now()

class Comando(BaseModel):
    dispositivo_id: str
    acao: str

def salvar_dados_banco(dado: SensorData):
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            sslmode='disable'
        )
        cur = conn.cursor()
        cur.execute(
            '''
            INSERT INTO sensores (dispositivo_id, tensao, corrente, temperatura, status, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''',
            (dado.dispositivo_id, dado.tensao, dado.corrente, dado.temperatura, dado.status, dado.timestamp)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar no banco: {e}")

@app.post("/dados")
async def receber_dados(sensor: SensorData):
    salvar_dados_banco(sensor)
    data_log.append(sensor)
    return {"status": "dados recebidos"}

@app.get("/status")
async def listar_dados():
    return data_log[-10:]

@app.post("/comando")
async def enviar_comando(cmd: Comando):
    print(f"Comando enviado para {cmd.dispositivo_id}: {cmd.acao}")
    return {"status": "comando enviado", "comando": cmd}