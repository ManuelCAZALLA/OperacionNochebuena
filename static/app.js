const API = "http://127.0.0.1:8000"; // Cambia por la URL de tu backend si está en otro lado

// Cargar misión al inicio
async function cargarMision() {
  const res = await fetch(`${API}/mision`);
  const data = await res.json();
  document.getElementById("mision").innerText = data.mision;
}

// Nueva misión al botón
document.getElementById("nuevaMision").addEventListener("click", cargarMision);

// Subir foto y texto
document.getElementById("formCapsula").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById("file");
  const textoInput = document.getElementById("texto");
  const mensaje = document.getElementById("mensaje");

  if (!fileInput.files[0]) {
    mensaje.innerText = "Por favor selecciona una foto.";
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  formData.append("texto", textoInput.value);

  try {
    const res = await fetch(`${API}/capsula`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    if (res.ok) {
      mensaje.style.color = "green";
      mensaje.innerText = "¡Foto guardada con éxito!";
      fileInput.value = "";
      textoInput.value = "";
      verCapsula(); // Actualiza la galería
    } else {
      mensaje.style.color = "red";
      mensaje.innerText = data.detail || "Error al subir la foto.";
    }
  } catch (err) {
    mensaje.style.color = "red";
    mensaje.innerText = "Error al comunicarse con el servidor.";
  }
});

// Mostrar cápsula desbloqueada
async function verCapsula() {
  const galeria = document.getElementById("galeria");
  galeria.innerHTML = "";

  try {
    const res = await fetch(`${API}/capsula`);
    if (!res.ok) {
      galeria.innerText = "🔒 Aún no se puede abrir. Espera a la llegada de Papá Noel 🎅";
      return;
    }

    const data = await res.json();
    if (data.length === 0) {
      galeria.innerText = "No hay fotos aún.";
      return;
    }

    data.forEach(item => {
      const contenedor = document.createElement("div");
      contenedor.style.marginBottom = "20px";

      const img = document.createElement("img");
      img.src = `${API}${item.url}`;
      img.alt = "Foto cápsula";

      const texto = document.createElement("p");
      texto.textContent = item.texto;
      texto.style.marginTop = "6px";
      texto.style.fontWeight = "600";
      texto.style.color = "#333";

      contenedor.appendChild(img);
      contenedor.appendChild(texto);
      galeria.appendChild(contenedor);
    });
  } catch {
    galeria.innerText = "Error al cargar la galería.";
  }
}

// Inicializar app
cargarMision();
verCapsula();
