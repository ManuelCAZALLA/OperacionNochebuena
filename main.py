from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import random
import os
import shutil
from datetime import datetime, time

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

# Lista fija de misiones (puedes ampliar)
MISIONS = [
    "Haz que alguien te cuente un chiste",
    "Baila un villancico durante 30 segundos",
    "Comparte un recuerdo gracioso de una Navidad pasada",
    "Haz que el abuelo te cuente una anécdota",
    "Toma una foto grupal sin que se den cuenta",
    "Regala un abrazo sorpresa a alguien",
]

# Guardamos fotos + texto en memoria simple (en producción usar DB)
capsula = []

class CapsulaEntry(BaseModel):
    filename: str
    texto: str
    timestamp: datetime

# Endpoint para obtener misión aleatoria
@app.get("/mision")
def get_mision():
    return {"mision": random.choice(MISIONS)}

# Endpoint para subir foto y texto para la cápsula
@app.post("/capsula")
async def subir_capsula(
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
        "texto": texto,
        "timestamp": now.isoformat()
    }
    capsula.append(entry)
    return {"mensaje": "Foto guardada, ¡gracias!", "entry": entry}

# Endpoint para ver cápsula desbloqueada solo después de medianoche
@app.get("/capsula")
def ver_capsula():
    now = datetime.now()
    # Cambia aquí la hora si quieres que se desbloquee después de la llegada de Papá Noel, ejemplo 23:59
    unlock_time = time(23, 59)
    if now.time() < unlock_time:
        raise HTTPException(status_code=403, detail="La cápsula estará disponible después de la llegada de Papá Noel.")
    fotos_info = [
        {
            "url": f"/fotos/{e['filename']}",
            "texto": e["texto"],
            "timestamp": e["timestamp"]
        }
        for e in capsula
    ]
    return fotos_info

# Servir fotos estáticas
app.mount("/fotos", StaticFiles(directory=FOTOS_DIR), name="fotos")

# Servir frontend estático (index.html, css, js, etc)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ruta raíz que sirve el index.html
@app.get("/")
def root():
    return FileResponse("static/index.html")
