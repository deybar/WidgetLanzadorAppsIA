# 🛠️ 05. Utilidades y Herramientas

En este documento se describe el catálogo de archivos de soporte, utilidades del proyecto, esquema del archivo de configuración y pautas para depuración y desarrollo.

---

## 1. Catálogo de Archivos y Responsabilidades

```
12_Lanzador-Apps-IA/
├── config.json          # Almacén persistente de preferencias del usuario
├── debug_consola.bat    # Script de arranque en consola para depuración
├── iniciar.bat          # Script de arranque en lote estándar
├── iniciar.vbs          # Script de arranque silencioso sin ventana CMD (Recomendado)
├── launcher_window.py   # Interfaz gráfica (Solapa, Panel, Tarjetas, Geometría)
├── main.py              # Punto de entrada, Socket de Instancia Única y System Tray
├── requirements.txt     # Especificación de paquetes Python
└── .gitignore           # Exclusiones de control de versiones Git
```

### Detalle por Módulo:

### A. `main.py`
- **Punto de entrada (`entrypoint`):**
  - Establece el directorio de trabajo actual (`os.chdir(APP_DIR)`).
  - Verifica la instancia única mediante `ensure_single_instance(app, on_activate_cb)`.
  - Si ya existe una instancia previa, envía `b"ACTIVATE"` por socket y finaliza.
  - Si es la primera instancia, levanta el servidor `QLocalServer(SOCKET_NAME)` y genera el icono de la bandeja del sistema (`QSystemTrayIcon`).
  - Gestiona el menú contextual de la bandeja y las notificaciones toast nativas de Windows.
  - En caso de excepción no controlada, captura el volcado con `traceback.format_exc()` y lo guarda en `launcher_crash.log`.

### B. `launcher_window.py`
- **Componentes Visuales:**
  - `QuickLauncherWidget`: Ventana principal sin bordes (`FramelessWindowHint`) y con atributo `WindowStaysOnTopHint` para mantenerse accesible sobre otras ventanas.
  - `flap` (Solapa retraída): Barra sutil con borde redondeado e icono `⚡ IA`.
  - `panel` (Panel expandido): Contenedor con encabezado, tarjetas de aplicaciones y pie con acciones.
  - `AppCardWidget`: Tarjetas individuales con icono coloreado, títulos, estados visuales y eventos de clic.
- **Gestión de Geometría y Arrastre:**
  - Métodos `_on_flap_mouse_press`, `_on_flap_mouse_move` y `_on_flap_mouse_release` que calculan el desplazamiento manhattan y actualizan `pos_y`.
- **Temporizadores:**
  - `status_timer`: Consulta periódica de sockets cada 2 segundos.
  - `auto_hide_timer`: Ocultamiento tras 8 segundos de inactividad.

---

## 2. Esquema de Configuración (`config.json`)

El archivo `config.json` se almacena en la raíz del proyecto y se actualiza automáticamente cuando el usuario arrastra la solapa o alterna el lado:

```json
{
    "dock_side": "right",
    "pos_y": 121,
    "theme": "dark_carbon",
    "opacity": 94,
    "auto_collapse": true
}
```

### Descripción de Atributos:

| Clave | Tipo | Valores Permitidos | Descripción |
|---|---|---|---|
| `dock_side` | `string` | `"right"`, `"left"` | Borde del monitor donde se ancla la solapa y se proyecta el panel. |
| `pos_y` | `int` | `40` a `(screen_h - 120)` | Posición vertical en píxeles respecto al borde superior de la pantalla. |
| `theme` | `string` | `"dark_carbon"`, `"slate"`, `"oled"` | Identificador de estilo visual (preparado para temas personalizados). |
| `opacity` | `int` | `1` a `100` | Nivel de opacidad porcentual de la ventana flotante. |
| `auto_collapse` | `bool` | `true`, `false` | Activa o desactiva el repliegue automático tras inactividad. |

---

## 3. Registro de Fallos (`launcher_crash.log`)

Si ocurre una falla crítica durante el arranque o en el bucle principal de eventos de Qt, `main.py` genera automáticamente un archivo `launcher_crash.log`:

```python
except Exception as e:
    with open(os.path.join(APP_DIR, "launcher_crash.log"), "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
```

Este archivo está excluido en el `.gitignore` para no contaminar el historial de versiones con errores de máquinas locales.

---

## 4. Guía para Agregar una Nueva Aplicación a la Suite

Actualmente, para integrar una cuarta herramienta en la suite (por ejemplo, un transcriptor OCR o un generador de imágenes local):

1. **Definir la configuración en `launcher_window.py`:**
   En la lista `APPS_CONFIG`, añadir el nuevo diccionario:
   ```python
   {
       "id": "nuevo_asistente",
       "title": "Nuevo Asistente",
       "subtitle": "Descripción breve de la tarea",
       "icon": "🧠",
       "icon_bg": "#8b5cf6",
       "socket": "NuevoAsistente_SingleInstance_2026",
       "vbs_path": os.path.join(PARENT_DIR, "13_NuevoAsistente", "iniciar.vbs"),
       "dir": os.path.join(PARENT_DIR, "13_NuevoAsistente")
   }
   ```

2. **Asegurar compatibilidad en la nueva app:**
   - Implementar un `QLocalServer` con el nombre de socket especificado (`NuevoAsistente_SingleInstance_2026`).
   - Escuchar el mensaje de texto `ACTIVATE` para restaurar y enfocar la ventana.
   - Proveer un script `iniciar.vbs` para el arranque silencioso.

> [!TIP]
> Según la [Bitácora de Desarrollo (`BITACORA.md`)](../BITACORA.md) (Tarea DT-01), en próximas versiones este catálogo se desacoplará hacia un archivo `apps.json` para que puedas registrar nuevas aplicaciones sin editar código fuente.
