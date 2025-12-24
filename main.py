import os
import random
import shutil
import sqlite3
from datetime import datetime, time
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Operación Nochebuena Simple")

# Permitir llamadas desde frontend local (ajusta si haces deploy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carpeta para guardar fotos
FOTOS_DIR = "./fotos"
os.makedirs(FOTOS_DIR, exist_ok=True)

DB_PATH = os.getenv("DB_PATH", "nochebuena.db")

# Clave simple para modo anfitrión (sin autenticación real)
HOST_CODE = os.getenv("HOST_CODE", "NAVIDAD")

# Listas de retos/misiones
MISIONS = [
    "Haz que el abuelo te cuente el chiste del caballo",
    "Que la abuela cuente por que el abuelo no se comia la sopa",
    "Comparte un recuerdo gracioso de una Navidad pasada",
    "Haz que el abuelo te cuente una anécdota",
    "Toma una foto grupal sin que se den cuenta",
    "Regala un abrazo sorpresa a alguien",
    "Que la abuela cuente cuando salió el porrón por el balcón",
]

RETOS_COLECTIVOS = [
    "Selfie grupal ",
    "Foto del brindis justo antes de chocar las copas",
    "Todos diciendo 'Nochebuena' al mismo tiempo ",
    "Todos nos levantamos de la silla, damos una vuelta y nos sentamos",
    "Todos gritamos goooooll",
    "Todos encima de la silla",
    "Todos corremos alrededor de la mesa y volvemos a nuestro sitio",
    "Unos dicen Jose Antonio y otros Jamón"
    
]

RETOS_INDIVIDUALES = [
    "Foto con tu postre favorito",
    "Selfie con el árbol de Navidad",
    "Captura a la persona más sonriente",
    "Foto con el plato que más te gustó",
     "Haz que el abuelo te cuente el chiste del caballo",
    "Que la abuela cuente por que el abuelo no se comia la sopa",
    "Comparte un recuerdo gracioso de una Navidad pasada",
    "Haz que el abuelo te cuente una anécdota",
    "Toma una foto grupal sin que se den cuenta",
    "Regala un abrazo sorpresa a alguien",
    "Que la abuela cuente cuando salió el porrón por el balcón",
]


def _normaliza_codigo(cadena: Optional[str]) -> str:
    return (cadena or "").strip().upper()


# --- DB helpers ---
def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    conn = _get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS capsula (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            alias TEXT NOT NULL,
            texto TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def _insert_entry(filename: str, alias: str, texto: str, timestamp: str):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO capsula (filename, alias, texto, timestamp) VALUES (?, ?, ?, ?)",
        (filename, alias, texto, timestamp),
    )
    conn.commit()
    conn.close()


def _listar_entries():
    conn = _get_conn()
    rows = conn.execute(
        "SELECT filename, alias, texto, timestamp FROM capsula ORDER BY timestamp ASC"
    ).fetchall()
    conn.close()
    return [
        {
            "filename": r["filename"],
            "alias": r["alias"],
            "texto": r["texto"],
            "timestamp": r["timestamp"],
        }
        for r in rows
    ]

# Endpoint para obtener misión aleatoria
@app.get("/mision")
def get_mision():
    return {"mision": random.choice(MISIONS)}

# Endpoints de retos
@app.get("/reto/sorpresa")
def reto_sorpresa():
    todos = RETOS_COLECTIVOS + RETOS_INDIVIDUALES
    return {"reto": random.choice(todos)}


# Endpoint para subir foto y texto para la cápsula
@app.post("/capsula")
async def subir_capsula(
    alias: str = Form("Misterio Festivo"),
    texto: str = Form(...),
    file: UploadFile = File(...)
):
    now = datetime.now()
    filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    filepath = os.path.join(FOTOS_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    entry = {
        "filename": filename,
        "alias": alias,
        "texto": texto,
        "timestamp": now.isoformat()
    }
    _insert_entry(entry["filename"], entry["alias"], entry["texto"], entry["timestamp"])
    return {"mensaje": "Foto guardada, ¡gracias!", "entry": entry}

# Endpoint para ver cápsula desbloqueada solo después de medianoche
@app.get("/capsula")
def ver_capsula(
    vista: str = "jugador",
    code: Optional[str] = None
):
    now = datetime.now()
    unlock_time = time(23, 59)  # cambia si quieres otro horario

    es_anfitrion = vista == "anfitrion" and _normaliza_codigo(code) == _normaliza_codigo(HOST_CODE)
    if now.time() < unlock_time and not es_anfitrion:
        raise HTTPException(
            status_code=403,
            detail="🔒 Aún no se puede abrir. Espera a la medianoche."
        )

    entries = _listar_entries()
    fotos_info = [
        {
            "url": f"/fotos/{e['filename']}",
            "alias": e["alias"],
            "texto": e["texto"],
            "timestamp": e["timestamp"]
        }
        for e in entries
    ]
    return fotos_info

# Servir fotos estáticas
app.mount("/fotos", StaticFiles(directory=FOTOS_DIR), name="fotos")

# Servir frontend estático (index.html, css, js, etc)
app.mount("/static", StaticFiles(directory="static"), name="static")

_init_db()

# Servir frontend también en raíz para GitHub Pages / estático
app.mount("/", StaticFiles(directory="static", html=True), name="static_root")
