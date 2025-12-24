// Estado en memoria simple
let aliasActual = "";
let modoAnfitrion = false;
let apiBase = "";

const backendInput = document.getElementById("backendUrl");
const backendEstado = document.getElementById("estadoBackend");

function normalizaBase(url) {
  const limpio = (url || "").trim();
  if (!limpio) return "";
  return limpio.endsWith("/") ? limpio.slice(0, -1) : limpio;
}

function cargarBackend() {
  const guardado = localStorage.getItem("apiBase") || "";
  apiBase = normalizaBase(guardado);
  backendInput.value = apiBase;
  backendEstado.innerText = apiBase
    ? `Usando backend: ${apiBase}`
    : "Usando el mismo origen (vacío).";
}

function setBackendDesdeInput() {
  apiBase = normalizaBase(backendInput.value);
  localStorage.setItem("apiBase", apiBase);
  backendEstado.innerText = apiBase
    ? `Usando backend: ${apiBase}`
    : "Usando el mismo origen (vacío).";
}

function api(path) {
  return `${apiBase}${path}`;
}

const apodos = [
  "Reno Azul", "Duende Brillante", "Estrella Fugaz", "Gorro Rojo",
  "Luz Dorada", "Campana Alegre", "Copito de Nieve", "Regalo Sorpresa",
  "Chispa Verde", "Trineo Veloz"
];

function generarAlias() {
  const elegido = apodos[Math.floor(Math.random() * apodos.length)];
  const numero = Math.floor(Math.random() * 90) + 10;
  return `${elegido} ${numero}`;
}

function cargarAlias() {
  const almacenado = localStorage.getItem("aliasNavidad");
  aliasActual = almacenado || generarAlias();
  localStorage.setItem("aliasNavidad", aliasActual);
  document.getElementById("alias").innerText = aliasActual;
}

function cambiarAlias() {
  aliasActual = generarAlias();
  localStorage.setItem("aliasNavidad", aliasActual);
  document.getElementById("alias").innerText = aliasActual;
}

// Cargar misión al inicio
async function cargarMision() {
  const res = await fetch(api("/mision"));
  const data = await res.json();
  document.getElementById("mision").innerText = data.mision;
}

async function cargarRetoSorpresa() {
  const salida = document.getElementById("retoSorpresa");
  salida.innerText = "Cargando...";
  try {
    const res = await fetch(api("/reto/sorpresa"));
    const data = await res.json();
    salida.innerText = data.reto;
  } catch {
    salida.innerText = "No se pudo cargar el reto.";
  }
}

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
  formData.append("alias", aliasActual);

  try {
    const res = await fetch(api("/capsula"), {
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
    const params = new URLSearchParams();
    params.set("vista", modoAnfitrion ? "anfitrion" : "jugador");
    if (modoAnfitrion) {
      const code = localStorage.getItem("codigoAnfitrion") || "";
      params.set("code", code);
    }

    const res = await fetch(`${api("/capsula")}?${params.toString()}`);
    if (!res.ok) {
      galeria.innerText = "🔒 Aún no se puede abrir. Espera a la medianoche 🎅";
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
      img.src = `${apiBase}${item.url}`;
      img.alt = "Foto cápsula";

      const texto = document.createElement("p");
      texto.textContent = `${item.alias}: ${item.texto}`;
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
cargarAlias();

const estadoAnfitrion = document.getElementById("estadoAnfitrion");
function actualizarEstadoAnfitrion() {
  estadoAnfitrion.innerText = modoAnfitrion
    ? "Modo anfitrión activo. Ves todo antes de medianoche."
    : "Modo jugador activo.";
}

document.getElementById("nuevoAlias").addEventListener("click", () => {
  cambiarAlias();
});

document.getElementById("nuevaMision").addEventListener("click", cargarMision);
document.getElementById("retoSorpresaBtn").addEventListener("click", cargarRetoSorpresa);
document.getElementById("guardarBackend").addEventListener("click", () => {
  setBackendDesdeInput();
  cargarMision();
  cargarRetoSorpresa();
  verCapsula();
});

document.getElementById("activarAnfitrion").addEventListener("click", () => {
  const code = document.getElementById("codigoAnfitrion").value.trim() || "";
  const normalizado = code.toUpperCase();
  localStorage.setItem("codigoAnfitrion", normalizado);
  modoAnfitrion = true;
  localStorage.setItem("modoAnfitrion", "1");
  actualizarEstadoAnfitrion();
  verCapsula();
});

document.getElementById("desactivarAnfitrion").addEventListener("click", () => {
  modoAnfitrion = false;
  localStorage.removeItem("modoAnfitrion");
  actualizarEstadoAnfitrion();
  verCapsula();
});

// Restaurar estado anfitrión si lo dejó activo
if (localStorage.getItem("modoAnfitrion") === "1") {
  modoAnfitrion = true;
  document.getElementById("codigoAnfitrion").value = localStorage.getItem("codigoAnfitrion") || "";
}

cargarBackend();
cargarMision();
cargarRetoSorpresa();
actualizarEstadoAnfitrion();
verCapsula();
