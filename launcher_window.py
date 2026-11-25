"""
Burbuja y Solapa Flotante de Acceso Rápido para la Suite de IA Local (PyQt6).
Se adhiere al borde de la pantalla de forma discreta y al hacer clic o interactuar
se despliega mostrando las aplicaciones configuradas en apps.json con su estado en vivo.
"""

import os
import sys
import json
import time
import threading
import subprocess
from typing import Dict, Any, List, Optional
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGraphicsDropShadowEffect, QApplication, QMenu
)
from PyQt6.QtGui import QColor, QCursor, QMouseEvent
from PyQt6.QtNetwork import QLocalSocket

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(APP_DIR)
CONFIG_PATH = os.path.join(APP_DIR, "config.json")
APPS_JSON_PATH = os.path.join(APP_DIR, "apps.json")

DEFAULT_APPS_SPEC: List[Dict[str, Any]] = [
    {
        "id": "traductor_local",
        "title": "Traductor de Texto",
        "subtitle": "Selección con ratón (EN ↔ ES)",
        "icon": "文A",
        "icon_bg": "#2563eb",
        "socket": "TraductorLocal_SingleInstance_2026",
        "folder_candidates": ["1_TraductorLocal", "08_TraductorLocal"],
        "entry_script": "main.py",
        "vbs_script": "iniciar.vbs"
    },
    {
        "id": "traductor_audio",
        "title": "Traductor de Audio",
        "subtitle": "Subtítulos en tiempo real EN ➔ ES",
        "icon": "💬",
        "icon_bg": "#0284c7",
        "socket": "TraductorAudio_SingleInstance_2026",
        "folder_candidates": ["2_TraductorAudio", "09_TraductorAudio"],
        "entry_script": "main.py",
        "vbs_script": "iniciar.vbs"
    },
    {
        "id": "asistente_reunion",
        "title": "Asistente de Reunión",
        "subtitle": "Transcripción, notas y minuta",
        "icon": "🎙️",
        "icon_bg": "#10b981",
        "socket": "AsistenteReunion_SingleInstance_2026",
        "folder_candidates": ["3_Asistente-de-reunion", "10_Asistente-de-reunion"],
        "entry_script": "main.py",
        "vbs_script": "iniciar.vbs"
    }
]


def _resolve_app_dir(candidates: List[str]) -> str:
    """Resuelve la carpeta real de la app buscando candidatos y sufijos en PARENT_DIR."""
    for folder_name in candidates:
        candidate_path = os.path.join(PARENT_DIR, folder_name)
        if os.path.isdir(candidate_path):
            return candidate_path

    # Búsqueda flexible por sufijo (ej. "TraductorLocal", "TraductorAudio", "Asistente-de-reunion")
    try:
        subdirs = [d for d in os.listdir(PARENT_DIR) if os.path.isdir(os.path.join(PARENT_DIR, d))]
        for folder_name in candidates:
            suffix = folder_name.split("_", 1)[-1].lower()
            for sub in subdirs:
                if suffix and suffix in sub.lower():
                    return os.path.join(PARENT_DIR, sub)
    except Exception:
        pass

    return os.path.join(PARENT_DIR, candidates[0] if candidates else "")


def load_apps_config() -> List[Dict[str, Any]]:
    """Carga las aplicaciones desde apps.json y resuelve sus rutas ejecutables."""
    raw_specs = DEFAULT_APPS_SPEC
    if os.path.exists(APPS_JSON_PATH):
        try:
            with open(APPS_JSON_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, list) and loaded:
                    raw_specs = loaded
        except Exception:
            pass

    resolved: List[Dict[str, Any]] = []
    for spec in raw_specs:
        entry = dict(spec)
        candidates = entry.get("folder_candidates") or []
        if not candidates and entry.get("dir"):
            candidates = [os.path.basename(entry["dir"])]

        app_dir = entry.get("dir")
        if not app_dir or not os.path.isdir(app_dir):
            app_dir = _resolve_app_dir(candidates)

        entry_script = entry.get("entry_script", "main.py")
        vbs_script = entry.get("vbs_script", "iniciar.vbs")

        entry["dir"] = app_dir
        entry["main_py"] = os.path.join(app_dir, entry_script)
        entry["vbs_path"] = os.path.join(app_dir, vbs_script)
        resolved.append(entry)

    return resolved


APPS_CONFIG = load_apps_config()


def load_config() -> Dict[str, Any]:
    defaults = {
        "dock_side": "right",
        "pos_y": 320,
        "theme": "dark_carbon",
        "opacity": 94,
        "auto_collapse": True
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
    return defaults


def save_config(cfg: Dict[str, Any]):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
    except Exception:
        pass


def check_socket_status(socket_name: str) -> bool:
    """Verifica si la aplicación está en ejecución sin crear sockets Qt en hilos secundarios."""
    if not socket_name:
        return False
    if os.name == "nt":
        try:
            import ctypes
            pipe_path = rf"\\.\pipe\{socket_name}"
            res = ctypes.windll.kernel32.WaitNamedPipeW(pipe_path, 30)
            if res != 0:
                return True
            err = ctypes.windll.kernel32.GetLastError()
            return err == 121  # ERROR_SEM_TIMEOUT -> pipe existe aunque ocupado
        except Exception:
            return False

    try:
        sock = QLocalSocket()
        sock.connectToServer(socket_name)
        connected = sock.waitForConnected(80)
        if connected:
            sock.write(b"PING")
            sock.waitForBytesWritten(50)
            sock.disconnectFromServer()
        return connected
    except RuntimeError:
        return False


def activate_app_by_socket(socket_name: str) -> bool:
    """Envía la señal ACTIVATE a una aplicación ya en ejecución para traerla al frente."""
    if not socket_name:
        return False
    sock = QLocalSocket()
    sock.connectToServer(socket_name)
    if sock.waitForConnected(200):
        sock.write(b"ACTIVATE")
        sock.waitForBytesWritten(200)
        sock.disconnectFromServer()
        return True
    return False


def stop_app_by_socket(socket_name: str) -> bool:
    """Envía la señal QUIT a una aplicación en ejecución para cerrarla limpiamente."""
    if not socket_name:
        return False
    sock = QLocalSocket()
    sock.connectToServer(socket_name)
    if sock.waitForConnected(200):
        sock.write(b"QUIT")
        sock.waitForBytesWritten(150)
        sock.disconnectFromServer()
        return True
    return False


def _resolve_python_executable(app_dir: str) -> Optional[str]:
    """Busca el ejecutable pythonw.exe / python.exe más adecuado para lanzar una app."""
    user_profile = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    candidates = [
        os.path.join(user_profile, ".audio_translator_venv", "Scripts", "pythonw.exe"),
        os.path.join(user_profile, ".audio_translator_venv", "Scripts", "python.exe"),
        os.path.join(user_profile, ".local_translator_venv", "Scripts", "pythonw.exe"),
        os.path.join(user_profile, ".local_translator_venv", "Scripts", "python.exe"),
        os.path.join(app_dir, ".venv", "Scripts", "pythonw.exe"),
        os.path.join(app_dir, ".venv", "Scripts", "python.exe"),
    ]
    if sys.executable:
        exe_dir = os.path.dirname(sys.executable)
        pythonw_sibling = os.path.join(exe_dir, "pythonw.exe")
        if os.path.exists(pythonw_sibling):
            candidates.append(pythonw_sibling)
        candidates.append(sys.executable)

    for path in candidates:
        if path and os.path.exists(path):
            return path
    return None


def launch_or_activate(app_info: Dict[str, Any]) -> str:
    """Si la app está corriendo, la enfoca; si no, la inicia directamente en segundo plano."""
    socket_name = app_info.get("socket", "")
    if socket_name and activate_app_by_socket(socket_name):
        return "activated"

    app_dir = app_info.get("dir", "")
    main_py = app_info.get("main_py") or os.path.join(app_dir, "main.py")
    vbs_path = app_info.get("vbs_path") or os.path.join(app_dir, "iniciar.vbs")

    python_exe = _resolve_python_executable(app_dir)
    if python_exe and os.path.exists(main_py):
        try:
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            subprocess.Popen(
                [python_exe, main_py],
                cwd=app_dir,
                creationflags=creation_flags,
                close_fds=True
            )
            return "launched"
        except Exception as e:
            print(f"[ERROR] Fallo lanzando {main_py} con {python_exe}: {e}")

    if os.path.exists(vbs_path):
        try:
            os.startfile(vbs_path)
            return "launched"
        except Exception as e:
            print(f"[ERROR] Error al iniciar {vbs_path}: {e}")

    print(f"[ERROR] No se encontró ejecutable ni script de inicio para {app_info.get('title', 'App')} en {app_dir}")
    return "error"


class AppCardWidget(QFrame):
    """Tarjeta interactiva para cada aplicación registrada."""
    def __init__(self, app_info: Dict[str, Any], on_clicked_callback, on_action_callback=None, parent=None):
        super().__init__(parent)
        self.app_info = app_info
        self.on_clicked_callback = on_clicked_callback
        self.on_action_callback = on_action_callback
        self._is_running = False
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setObjectName("app_card")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        # Icono con fondo distintivo
        self.icon_badge = QLabel(app_info["icon"], self)
        self.icon_badge.setFixedSize(36, 36)
        self.icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_badge.setStyleSheet(f"""
            background-color: {app_info.get('icon_bg', '#2563eb')};
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            border-radius: 8px;
        """)
        layout.addWidget(self.icon_badge)

        # Textos: Título y Subtítulo
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        self.lbl_title = QLabel(app_info["title"], self)
        self.lbl_title.setStyleSheet("color: #f4f4f5; font-size: 12px; font-weight: 700;")
        text_layout.addWidget(self.lbl_title)

        self.lbl_sub = QLabel(app_info["subtitle"], self)
        self.lbl_sub.setStyleSheet("color: #a1a1aa; font-size: 10px;")
        text_layout.addWidget(self.lbl_sub)

        layout.addLayout(text_layout)
        layout.addStretch()

        # Indicador de estado (Activo / Iniciando / Inactivo)
        self.status_dot = QLabel("○", self)
        self.status_dot.setStyleSheet("color: #71717a; font-size: 13px;")
        self.status_dot.setToolTip("Estado: No iniciado")
        layout.addWidget(self.status_dot)

        self.setStyleSheet("""
            QFrame#app_card {
                background-color: #18181b;
                border: 1px solid #27272a;
                border-radius: 9px;
            }
            QFrame#app_card:hover {
                background-color: #27272a;
                border: 1px solid #3f3f46;
            }
        """)

    def update_status(self, is_running: bool, is_starting: bool = False):
        self._is_running = is_running
        if is_running:
            self.status_dot.setText("●")
            self.status_dot.setStyleSheet("color: #10b981; font-size: 14px;")
            self.status_dot.setToolTip("Estado: En ejecución (Clic para enfocar | Clic derecho para opciones)")
        elif is_starting:
            self.status_dot.setText("⏳")
            self.status_dot.setStyleSheet("color: #f59e0b; font-size: 12px;")
            self.status_dot.setToolTip("Estado: Iniciando aplicación...")
        else:
            self.status_dot.setText("○")
            self.status_dot.setStyleSheet("color: #52525b; font-size: 13px;")
            self.status_dot.setToolTip("Estado: Inactivo (Clic para iniciar | Clic derecho para opciones)")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_clicked_callback(self.app_info)
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
        super().mousePressEvent(event)

    def _show_context_menu(self, global_pos: QPoint):
        if self.on_action_callback:
            self.on_action_callback("menu_open", self.app_info)

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #18181b;
                color: #f4f4f5;
                border: 1px solid #3f3f46;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 5px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #27272a;
                color: #38bdf8;
            }
        """)

        act_launch = menu.addAction("🚀 Traer al frente" if self._is_running else "🚀 Iniciar aplicación")
        act_stop = menu.addAction("⏹️ Detener aplicación")
        act_stop.setEnabled(self._is_running)
        menu.addSeparator()
        act_folder = menu.addAction("📂 Abrir carpeta en Explorador")

        chosen = menu.exec(global_pos)
        if chosen == act_launch:
            self.on_clicked_callback(self.app_info)
        elif chosen == act_stop:
            if self.on_action_callback:
                self.on_action_callback("stop", self.app_info)
        elif chosen == act_folder:
            if self.on_action_callback:
                self.on_action_callback("open_folder", self.app_info)


class QuickLauncherWidget(QWidget):
    statuses_ready = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.apps_config = load_apps_config()
        self.dock_side = self.config.get("dock_side", "right")
        self.pos_y = self.config.get("pos_y", 320)
        self.is_expanded = False

        self._press_pos = QPoint(0, 0)
        self._drag_offset = QPoint(0, 0)
        self._is_dragging_flap = False
        self._has_dragged = False

        self._starting_apps: Dict[str, float] = {}
        self._status_check_in_flight = False
        self.statuses_ready.connect(self._apply_app_statuses)

        # Temporizadores inicializados ANTES de la UI
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.refresh_app_statuses)

        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.collapse_panel)

        self._init_ui()
        self._apply_geometry()

        self.status_timer.start(2000)
        self.refresh_app_statuses()

        self.collapse_panel()

    def _init_ui(self):
        self.setWindowTitle("Lanzador Suite IA Local")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # -------------------------------------------------------------
        # 1. ICONO FLOTANTE MINIMALISTA (Visible cuando está colapsado)
        # -------------------------------------------------------------
        self.flap = QFrame(self)
        self.flap.setObjectName("flap")
        self.flap.setFixedSize(20, 20)
        self.flap.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.flap.setToolTip("⚡ Suite IA Local\n• Clic: Abrir menú\n• Arrastrar: Mover libremente por el borde")

        flap_layout = QVBoxLayout(self.flap)
        flap_layout.setContentsMargins(0, 0, 0, 0)
        flap_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_flap_icon = QLabel("⚡", self.flap)
        self.lbl_flap_icon.setStyleSheet("color: #38bdf8; font-size: 11px; font-weight: bold;")
        self.lbl_flap_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flap_layout.addWidget(self.lbl_flap_icon)

        self.flap.mousePressEvent = self._on_flap_mouse_press
        self.flap.mouseMoveEvent = self._on_flap_mouse_move
        self.flap.mouseReleaseEvent = self._on_flap_mouse_release

        main_layout.addWidget(self.flap)

        # -------------------------------------------------------------
        # 2. PANEL DESPLEGADO (EXPANDED) - Con las aplicaciones
        # -------------------------------------------------------------
        self.panel = QFrame(self)
        self.panel.setObjectName("panel")
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(12, 10, 12, 10)
        panel_layout.setSpacing(8)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(24)
        self.shadow.setColor(QColor(0, 0, 0, 180))
        self.shadow.setOffset(0, 4)
        self.panel.setGraphicsEffect(self.shadow)

        self.flap_shadow = QGraphicsDropShadowEffect(self)
        self.flap_shadow.setBlurRadius(8)
        self.flap_shadow.setColor(QColor(0, 0, 0, 160))
        self.flap_shadow.setOffset(-1 if self.dock_side == "right" else 1, 1)
        self.flap.setGraphicsEffect(self.flap_shadow)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 2)
        header_layout.setSpacing(6)

        title_lbl = QLabel("🚀 Suite IA Local", self.panel)
        title_lbl.setStyleSheet("color: #38bdf8; font-size: 13px; font-weight: 800;")
        header_layout.addWidget(title_lbl)

        header_layout.addStretch()

        self.btn_collapse = QPushButton("▶" if self.dock_side == "right" else "◀", self.panel)
        self.btn_collapse.setToolTip("Plegar al icono flotante")
        self.btn_collapse.setFixedSize(22, 22)
        self.btn_collapse.setStyleSheet("""
            background-color: #18181b;
            color: #a1a1aa;
            border: 1px solid #27272a;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
        """)
        self.btn_collapse.clicked.connect(self.collapse_panel)
        header_layout.addWidget(self.btn_collapse)

        panel_layout.addLayout(header_layout)

        self.card_widgets: List[AppCardWidget] = []
        for app_info in self.apps_config:
            card = AppCardWidget(app_info, self._on_app_card_clicked, self._on_app_context_action, self.panel)
            self.card_widgets.append(card)
            panel_layout.addWidget(card)

        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 4, 0, 0)
        footer_layout.setSpacing(6)

        self.btn_side = QPushButton("⇋ Cambiar Lado", self.panel)
        self.btn_side.setToolTip("Mover icono al otro extremo de la pantalla")
        self.btn_side.setFixedHeight(22)
        self.btn_side.setStyleSheet("""
            background-color: #18181b;
            color: #a1a1aa;
            border: 1px solid #27272a;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            padding: 2px 8px;
        """)
        self.btn_side.clicked.connect(self.toggle_dock_side)
        footer_layout.addWidget(self.btn_side)

        footer_layout.addStretch()

        self.btn_close = QPushButton("✕ Salir", self.panel)
        self.btn_close.setToolTip("Cerrar lanzador")
        self.btn_close.setFixedHeight(22)
        self.btn_close.setStyleSheet("""
            background-color: #18181b;
            color: #ef4444;
            border: 1px solid #27272a;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            padding: 2px 8px;
        """)
        self.btn_close.clicked.connect(QApplication.instance().quit)
        footer_layout.addWidget(self.btn_close)

        panel_layout.addLayout(footer_layout)
        main_layout.addWidget(self.panel)

        self._update_styles()
        self.collapse_panel()

    def _update_styles(self):
        """Aplica estilos con bordes redondeados orientados al borde de pantalla."""
        if self.dock_side == "right":
            flap_radius = "border-top-left-radius: 6px; border-bottom-left-radius: 6px; border-top-right-radius: 0px; border-bottom-right-radius: 0px;"
            panel_radius = "border-top-left-radius: 14px; border-bottom-left-radius: 14px; border-top-right-radius: 0px; border-bottom-right-radius: 0px;"
            shadow_offset = -1
        else:
            flap_radius = "border-top-right-radius: 6px; border-bottom-right-radius: 6px; border-top-left-radius: 0px; border-bottom-left-radius: 0px;"
            panel_radius = "border-top-right-radius: 14px; border-bottom-right-radius: 14px; border-top-left-radius: 0px; border-bottom-left-radius: 0px;"
            shadow_offset = 1

        self.flap_shadow.setOffset(shadow_offset, 1)

        self.flap.setStyleSheet(f"""
            QFrame#flap {{
                background-color: rgba(24, 24, 27, 0.85);
                border: 1px solid rgba(56, 189, 248, 0.70);
                {flap_radius}
            }}
            QFrame#flap:hover {{
                background-color: rgba(39, 39, 42, 0.98);
                border: 1px solid #38bdf8;
            }}
        """)

        self.panel.setStyleSheet(f"""
            QFrame#panel {{
                background-color: rgba(18, 18, 20, 0.96);
                border: 1px solid #27272a;
                {panel_radius}
            }}
        """)

    def _apply_geometry(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.pos_y = max(screen.top() + 4, min(screen.bottom() - 26, self.pos_y))

        if not self.is_expanded:
            w = 20
            h = 20
            x = (screen.right() - w + 1) if self.dock_side == "right" else screen.left()
            y = self.pos_y
            self.setGeometry(x, y, w, h)
            self.setWindowOpacity(0.72)
        else:
            w = 285
            h = 115 + max(1, len(self.card_widgets)) * 70
            x = (screen.right() - w + 1) if self.dock_side == "right" else screen.left()
            ideal_y = self.pos_y - (h // 2) + 10
            y = max(screen.top() + 8, min(screen.bottom() - h - 8, ideal_y))
            self.setGeometry(x, y, w, h)
            self.setWindowOpacity(0.96)

    def expand_panel(self):
        """Despliega el panel con las aplicaciones."""
        self.is_expanded = True
        self.flap.hide()
        self.panel.show()
        self.btn_collapse.setText("▶" if self.dock_side == "right" else "◀")
        self._apply_geometry()
        self.refresh_app_statuses()

        if self.config.get("auto_collapse", True):
            self.auto_hide_timer.start(8000)

    def collapse_panel(self):
        """Pliega el panel de vuelta al icono minimalista semi-opaco en el borde."""
        self.is_expanded = False
        self.panel.hide()
        self.flap.show()
        self._apply_geometry()
        self.auto_hide_timer.stop()

    def toggle_dock_side(self):
        """Alterna el lado de adhesión de la pantalla (Izquierda / Derecha)."""
        self.dock_side = "left" if self.dock_side == "right" else "right"
        self.config["dock_side"] = self.dock_side
        save_config(self.config)
        self._update_styles()
        self._apply_geometry()
        self.btn_collapse.setText("▶" if self.dock_side == "right" else "◀")

    def _on_app_card_clicked(self, app_info: Dict[str, Any]):
        """Ejecuta o enfoca la aplicación y actualiza indicador visual."""
        result = launch_or_activate(app_info)
        if result == "launched":
            app_id = app_info.get("id", "")
            if app_id:
                self._starting_apps[app_id] = time.time()
            for card in self.card_widgets:
                if card.app_info.get("id") == app_id:
                    card.update_status(False, is_starting=True)
        self.collapse_panel()

    def _on_app_context_action(self, action: str, app_info: Dict[str, Any]):
        if action == "menu_open":
            self.auto_hide_timer.stop()
            return

        if action == "stop":
            sock_name = app_info.get("socket", "")
            app_id = app_info.get("id", "")
            self._starting_apps.pop(app_id, None)
            stop_app_by_socket(sock_name)
            QTimer.singleShot(350, self.refresh_app_statuses)
        elif action == "open_folder":
            app_dir = app_info.get("dir", "")
            if app_dir and os.path.isdir(app_dir):
                try:
                    os.startfile(app_dir)
                except Exception:
                    pass

        if self.is_expanded and self.config.get("auto_collapse", True):
            self.auto_hide_timer.start(8000)

    def refresh_app_statuses(self):
        """Consulta en segundo plano si las aplicaciones están activas."""
        if self._status_check_in_flight:
            return
        self._status_check_in_flight = True

        cards_snapshot = [(card.app_info.get("id", ""), card.app_info.get("socket", "")) for card in self.card_widgets]

        def _worker():
            results: Dict[str, bool] = {}
            try:
                for app_id, sock_name in cards_snapshot:
                    results[app_id] = check_socket_status(sock_name)
            finally:
                self._status_check_in_flight = False
            try:
                self.statuses_ready.emit(results)
            except RuntimeError:
                pass

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_app_statuses(self, statuses: Dict[str, bool]):
        now = time.time()
        for card in self.card_widgets:
            app_id = card.app_info.get("id", "")
            is_running = bool(statuses.get(app_id, False))
            if is_running:
                self._starting_apps.pop(app_id, None)
                card.update_status(True, is_starting=False)
            else:
                started_at = self._starting_apps.get(app_id)
                is_starting = False
                if started_at is not None:
                    if now - started_at < 8.0:
                        is_starting = True
                    else:
                        self._starting_apps.pop(app_id, None)
                card.update_status(False, is_starting=is_starting)

    # -------------------------------------------------------------
    # Gestión de Clic y Arrastre libre con el ratón
    # -------------------------------------------------------------
    def _on_flap_mouse_press(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging_flap = True
            self._press_pos = event.globalPosition().toPoint()
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
            self._has_dragged = False
            self.setWindowOpacity(0.95)

    def _on_flap_mouse_move(self, event: QMouseEvent):
        if self._is_dragging_flap:
            cur_pos = event.globalPosition().toPoint()
            if (cur_pos - self._press_pos).manhattanLength() > 4:
                self._has_dragged = True
                new_pos = cur_pos - self._drag_offset
                self.move(new_pos)

    def _on_flap_mouse_release(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging_flap = False
            if self._has_dragged:
                screen = QApplication.primaryScreen().availableGeometry()
                cur_center_x = self.x() + self.width() // 2
                screen_center_x = screen.left() + screen.width() // 2

                if cur_center_x < screen_center_x:
                    self.dock_side = "left"
                else:
                    self.dock_side = "right"

                new_y = self.y()
                self.pos_y = max(screen.top() + 4, min(screen.bottom() - 26, new_y))

                self.config["dock_side"] = self.dock_side
                self.config["pos_y"] = self.pos_y
                save_config(self.config)

                self._update_styles()
                self._apply_geometry()
                self.setWindowOpacity(0.72)
            else:
                self.expand_panel()

    def enterEvent(self, event):
        if not self.is_expanded:
            self.setWindowOpacity(1.0)
        else:
            if self.config.get("auto_collapse", True):
                self.auto_hide_timer.start(8000)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.is_expanded and not self._is_dragging_flap:
            self.setWindowOpacity(0.72)
        super().leaveEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.is_expanded:
                self.collapse_panel()
        super().keyPressEvent(event)
