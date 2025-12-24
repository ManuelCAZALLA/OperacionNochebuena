## Operación Nochebuena (versión ligera)

App rápida para cápsula de fotos y retos en Nochebuena:
- Alias aleatorio local (sin cuentas).
- Modo anfitrión con código simple (`HOST_CODE`) para ver antes de medianoche.
- Reto único “sorpresa”.
- Persistencia en SQLite (`nochebuena.db`) y fotos en `fotos/`.
- Frontend estático servible desde GitHub Pages; backend FastAPI aparte.

### Backend local
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Variables útiles:
- `HOST_CODE`: código anfitrión (por defecto `NAVIDAD`).
- `DB_PATH`: ruta alternativa para la base SQLite (por defecto `nochebuena.db`).
- `FOTOS_DIR`: si quieres cambiar la carpeta de fotos (por defecto `./fotos`).

### Frontend estático (GitHub Pages)
1) Sube la carpeta `static/` al repo (puedes ponerla en `docs/` si Pages apunta allí).
2) Activa GitHub Pages en `Settings > Pages` con la rama `main` y carpeta `root` o `docs`.
3) En la UI, en la tarjeta “Servidor backend”, pega la URL HTTPS del backend FastAPI y guarda.
   - El valor se guarda en `localStorage` en ese navegador.

### Backend en la nube (ej. Render)
1) Crea un servicio web, Python, repositorio conectado.
2) Comando de arranque: `uvicorn main:app --host 0.0.0.0 --port 10000`
3) Añade vars:
   - `HOST_CODE`: tu clave privada.
   - `DB_PATH`: opcional (ej. `/data/nochebuena.db` si usas disco persistente).
   - `FOTOS_DIR`: opcional (ej. `/data/fotos`).
4) Opcional: disco persistente para que fotos y db no se borren.
5) En `main.py`, CORS está abierto (`*`). Si quieres, limita `allow_origins` a tu dominio de Pages.

### Cómo funciona el desbloqueo
- Antes de la medianoche (`23:59` por defecto) solo el anfitrión con código ve todas las fotos.
- Después del horario, todos pueden ver la galería.
- Cambia la hora en `unlock_time` en `ver_capsula` si quieres otro horario.

### Notas
- Si el backend está apagado, no se pueden subir ni ver fotos.
- Las fotos y metadatos persisten en disco/db aunque reinicies el proceso.
- Para almacenamiento más robusto, cambia la subida a un bucket (S3, etc.) y guarda URLs en la base.

