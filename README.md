# ⚡ Lanzador Flotante de Acceso Rápido (Suite de IA Local) 🚀

> **Acceso rápido y discreto para tus 3 herramientas de Inteligencia Artificial 100% Locales y Offline.** Se oculta en el extremo de tu pantalla en una sutil insignia semi-opaca ultra-compacta de **20x20 px** con icono `⚡`. Se puede mover libremente con el ratón por toda la pantalla acoplándose magnéticamente al borde más cercano, y al hacer clic despliega un panel flotante para iniciar o activar al instante cualquiera de las aplicaciones.

---

## 📌 Aplicaciones Integradas

1. **📝 Traductor de Texto Local (`08_TraductorLocal`):**
   - Icono: `文A`
   - Selección con el ratón en cualquier ventana activa de Windows (Chrome, Word, PDFs, etc.).
   - Traducción neuronal instantánea (EN ↔ ES) con auto-ajuste de tamaño y 100% offline.

2. **🎧 Traductor de Audio en Tiempo Real (`09_TraductorAudio`):**
   - Icono: `💬`
   - Captura directa del sonido del PC (WASAPI Loopback) para Teams, Zoom o YouTube.
   - Subtítulos flotantes cinematográficos y traducción instantánea de inglés a español.

3. **🎙️ Asistente de Reunión y Minutas (`10_Asistente-de-reunion`):**
   - Icono: `🎙️`
   - **Modo HUD Zen minimalista (52 px):** Onda de audio reactiva animada que pulsa en tiempo real según el volumen de la voz, cronómetro de sesión e indicador dinámico de interlocutor (`🎙️ Tú` / `🔊 Colegas`).
   - **Grabación Streaming a `.wav`:** Audio raw de la llamada grabado continuamente a disco con 0 overhead de RAM.
   - **Ecosistema Tri-Formato Sincronizado:** Genera simultáneamente `.wav` (audio), `.md` (minuta con Frontmatter YAML y tareas interactivas `- [ ]`) y `.json` (timeline para reproductores interactivos futuros con *click-to-seek*).
   - Diarización acústica en CPU y Agente local de IA para compromisos (*action items*) y temas clave.

---

## ✨ Características del Lanzador

- **Insignia Flotante Ultra-Compacta (20x20 px):** Diseño minimalista con semi-opacidad dinámica (72% en reposo, 100% al pasar el cursor o arrastrar).
- **Arrastre 2D Libre con Ratón:** Puedes mover el icono libremente por cualquier parte de la pantalla.
- **Auto-Snap Magnético a Bordes:** Al soltar el ratón, se acopla suavemente al borde más cercano (izquierdo o derecho) a la altura exacta deseada y persiste la posición en `config.json`.
- **Detección de Estado en Vivo (Activo / Inactivo):** Muestra un punto luminoso verde `●` si la aplicación ya se encuentra abierta en segundo plano, o un punto gris `○` si no está iniciada.
- **Single Instance Focus:** Si una aplicación ya está abierta, hacer clic sobre ella no duplica procesos; la trae inmediatamente al frente y la enfoca.
- **Auto-Plegado Inteligente:** Al hacer clic en una aplicación, pulsar `Esc` o tras unos segundos de inactividad, el panel se repliega automáticamente para no molestar.
- **Bandeja del Sistema:** Icono en la barra de tareas de Windows para abrir el panel o acceder rápidamente a las herramientas.

---

## 🚀 Cómo Iniciar

- **`iniciar.vbs`** *(Recomendado)*: Inicio 100% silencioso e invisible en segundo plano.
- **`iniciar.bat`**: Lanzador por lotes estándar.
- **`debug_consola.bat`**: Lanzador con ventana de depuración visible.

---

## 📖 Documentación y Bitácora

- **[Documentación Técnica Completa](doc/README.md):** Manuales de arquitectura, IPC, dependencias, uso y herramientas.
- **[Bitácora de Desarrollo y Roadmap](BITACORA.md):** Diagnóstico, deudas técnicas identificadas, backlog priorizado y control de versiones.

