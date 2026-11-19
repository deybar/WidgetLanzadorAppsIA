"""
Burbuja y Solapa Flotante de Acceso Rápido para la Suite de IA Local (PyQt6).
Se adhiere al borde de la pantalla de forma discreta y al hacer clic o interactuar
se despliega mostrando las 3 aplicaciones con su estado en vivo (Activo / Inactivo).
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from PyQt6.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGraphicsDropShadowEffect, QApplication
)
from PyQt6.QtGui import QColor, QFont, QCursor, QMouseEvent
from PyQt6.QtNetwork import QLocalSocket

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(APP_DIR)
CONFIG_PATH = os.path.join(APP_DIR, "config.json")

APPS_CONFIG = [
    {
        "id": "traductor_local",
        "title": "Traductor de Texto",
        "subtitle": "Selección con ratón (EN ↔ ES)",
        "icon": "文A",
        "icon_bg": "#2563eb",
        "socket": "TraductorLocal_SingleInstance_2026",
        "vbs_path": os.path.join(PARENT_DIR, "08_TraductorLocal", "iniciar.vbs"),
        "dir": os.path.join(PARENT_DIR, "08_TraductorLocal")
    },
    {
        "id": "traductor_audio",
        "title": "Traductor de Audio",
        "subtitle": "Subtítulos en tiempo real EN ➔ ES",
        "icon": "💬",
        "icon_bg": "#0284c7",
        "socket": "TraductorAudio_SingleInstance_2026",
        "vbs_path": os.path.join(PARENT_DIR, "09_TraductorAudio", "iniciar.vbs"),
        "dir": os.path.join(PARENT_DIR, "09_TraductorAudio")
    },
    {
        "id": "asistente_reunion",
        "title": "Asistente de Reunión",
        "subtitle": "Transcripción, notas y minuta",
        "icon": "🎙️",
        "icon_bg": "#10b981",
        "socket": "AsistenteReunion_SingleInstance_2026",
        "vbs_path": os.path.join(PARENT_DIR, "10_Asistente-de-reunion", "iniciar.vbs"),
        "dir": os.path.join(PARENT_DIR, "10_Asistente-de-reunion")
    }
]

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
    """Verifica si la aplicación está en ejecución conectando a su socket local."""
    sock = QLocalSocket()
    sock.connectToServer(socket_name)
    connected = sock.waitForConnected(70)
    if connected:
        sock.disconnectFromServer()
    return connected

def activate_app_by_socket(socket_name: str) -> bool:
    """Envía la señal ACTIVATE a una aplicación ya en ejecución para traerla al frente."""
    sock = QLocalSocket()
    sock.connectToServer(socket_name)
    if sock.waitForConnected(150):
        sock.write(b"ACTIVATE")
        sock.waitForBytesWritten(150)
        sock.disconnectFromServer()
        return True
    return False

def launch_or_activate(app_info: Dict[str, Any]):
    """Si la app está corriendo, la enfoca; si no, la inicia silenciosamente."""
    socket_name = app_info.get("socket", "")
    if socket_name and activate_app_by_socket(socket_name):
        return

    vbs_path = app_info.get("vbs_path", "")
    if os.path.exists(vbs_path):
        try:
            os.startfile(vbs_path)
        except Exception as e:
            print(f"[ERROR] Error al iniciar {vbs_path}: {e}")

class AppCardWidget(QFrame):
    """Tarjeta interactiva para cada una de las 3 aplicaciones."""
    def __init__(self, app_info: Dict[str, Any], on_clicked_callback, parent=None):
        super().__init__(parent)
        self.app_info = app_info
        self.on_clicked_callback = on_clicked_callback
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

        # Indicador de estado (Activo / Inactivo)
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

    def update_status(self, is_running: bool):
        if is_running:
            self.status_dot.setText("●")
            self.status_dot.setStyleSheet("color: #10b981; font-size: 14px;")
            self.status_dot.setToolTip("Estado: En ejecución (Clic para enfocar)")
        else:
            self.status_dot.setText("○")
            self.status_dot.setStyleSheet("color: #52525b; font-size: 13px;")
            self.status_dot.setToolTip("Estado: Inactivo (Clic para iniciar)")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_clicked_callback(self.app_info)
        super().mousePressEvent(event)

class QuickLauncherWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.dock_side = self.config.get("dock_side", "right")
        self.pos_y = self.config.get("pos_y", 320)
        self.is_expanded = False

        self._press_pos = QPoint(0, 0)
        self._drag_offset = QPoint(0, 0)
        self._is_dragging_flap = False
        self._has_dragged = False

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
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow
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
        self.flap.setFixedSize(36, 36)
        self.flap.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.flap.setToolTip("⚡ Suite IA Local\n• Clic: Abrir menú\n• Arrastrar: Mover libremente por el borde")

        flap_layout = QVBoxLayout(self.flap)
        flap_layout.setContentsMargins(0, 0, 0, 0)
        flap_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono central minimalista
        self.lbl_flap_icon = QLabel("⚡", self.flap)
        self.lbl_flap_icon.setStyleSheet("color: #38bdf8; font-size: 17px; font-weight: bold;")
        self.lbl_flap_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flap_layout.addWidget(self.lbl_flap_icon)

        # Eventos del ratón para arrastre libre y clic
        self.flap.mousePressEvent = self._on_flap_mouse_press
        self.flap.mouseMoveEvent = self._on_flap_mouse_move
        self.flap.mouseReleaseEvent = self._on_flap_mouse_release

        main_layout.addWidget(self.flap)

        # -------------------------------------------------------------
        # 2. PANEL DESPLEGADO (EXPANDED) - Con las 3 aplicaciones
        # -------------------------------------------------------------
        self.panel = QFrame(self)
        self.panel.setObjectName("panel")
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(12, 10, 12, 10)
        panel_layout.setSpacing(8)

        # Sombra exterior suave para el panel
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(24)
        self.shadow.setColor(QColor(0, 0, 0, 180))
        self.shadow.setOffset(0, 4)
        self.panel.setGraphicsEffect(self.shadow)

        # Sombra exterior suave para el icono
        self.flap_shadow = QGraphicsDropShadowEffect(self)
        self.flap_shadow.setBlurRadius(14)
        self.flap_shadow.setColor(QColor(0, 0, 0, 170))
        self.flap_shadow.setOffset(-1 if self.dock_side == "right" else 1, 2)
        self.flap.setGraphicsEffect(self.flap_shadow)

        # Header del panel
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 2)
        header_layout.setSpacing(6)

        title_lbl = QLabel("🚀 Suite IA Local", self.panel)
        title_lbl.setStyleSheet("color: #38bdf8; font-size: 13px; font-weight: 800;")
        header_layout.addWidget(title_lbl)

        header_layout.addStretch()

        # Botón para plegar panel
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

        # Tarjetas de las 3 Apps
        self.card_widgets = []
        for app_info in APPS_CONFIG:
            card = AppCardWidget(app_info, self._on_app_card_clicked, self.panel)
            self.card_widgets.append(card)
            panel_layout.addWidget(card)

        # Footer con opciones: Cambiar lado y Salir
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
            flap_radius = "border-top-left-radius: 12px; border-bottom-left-radius: 12px; border-top-right-radius: 2px; border-bottom-right-radius: 2px;"
            panel_radius = "border-top-left-radius: 14px; border-bottom-left-radius: 14px; border-top-right-radius: 0px; border-bottom-right-radius: 0px;"
            shadow_offset = -1
        else:
            flap_radius = "border-top-right-radius: 12px; border-bottom-right-radius: 12px; border-top-left-radius: 2px; border-bottom-left-radius: 2px;"
            panel_radius = "border-top-right-radius: 14px; border-bottom-right-radius: 14px; border-top-left-radius: 0px; border-bottom-left-radius: 0px;"
            shadow_offset = 1

        self.flap_shadow.setOffset(shadow_offset, 2)

        self.flap.setStyleSheet(f"""
            QFrame#flap {{
                background-color: rgba(24, 24, 27, 0.82);
                border: 1.5px solid rgba(56, 189, 248, 0.65);
                {flap_radius}
            }}
            QFrame#flap:hover {{
                background-color: rgba(39, 39, 42, 0.96);
                border: 1.5px solid #38bdf8;
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
        screen_h = screen.height()

        # Asegurar que pos_y esté dentro de la pantalla visible
        self.pos_y = max(screen.top() + 8, min(screen.bottom() - 44, self.pos_y))

        if not self.is_expanded:
            # Modo Icono Flotante Minimalista
            w = 36
            h = 36
            x = (screen.right() - w + 1) if self.dock_side == "right" else screen.left()
            y = self.pos_y
            self.setGeometry(x, y, w, h)
            self.setWindowOpacity(0.60)
        else:
            # Modo Panel Desplegado
            w = 285
            h = 325
            x = (screen.right() - w + 1) if self.dock_side == "right" else screen.left()
            ideal_y = self.pos_y - (h // 2) + 18
            y = max(screen.top() + 8, min(screen.bottom() - h - 8, ideal_y))
            self.setGeometry(x, y, w, h)
            self.setWindowOpacity(0.96)

    def expand_panel(self):
        """Despliega el panel con las 3 aplicaciones."""
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
        """Ejecuta o enfoca la aplicación y pliega el lanzador."""
        launch_or_activate(app_info)
        self.collapse_panel()

    def refresh_app_statuses(self):
        """Consulta si las 3 aplicaciones están activas en segundo plano."""
        for card in self.card_widgets:
            sock_name = card.app_info.get("socket", "")
            is_running = check_socket_status(sock_name)
            card.update_status(is_running)

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
                # Mover libremente la ventana siguiendo al ratón en X y Y
                new_pos = cur_pos - self._drag_offset
                self.move(new_pos)

    def _on_flap_mouse_release(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging_flap = False
            if self._has_dragged:
                # Snap al borde de pantalla más cercano (izq o der)
                screen = QApplication.primaryScreen().availableGeometry()
                cur_center_x = self.x() + self.width() // 2
                screen_center_x = screen.left() + screen.width() // 2

                if cur_center_x < screen_center_x:
                    self.dock_side = "left"
                else:
                    self.dock_side = "right"

                # Posicionar a la altura donde lo soltó el usuario
                new_y = self.y()
                self.pos_y = max(screen.top() + 8, min(screen.bottom() - 44, new_y))

                self.config["dock_side"] = self.dock_side
                self.config["pos_y"] = self.pos_y
                save_config(self.config)

                self._update_styles()
                self._apply_geometry()
                self.setWindowOpacity(0.60)
            else:
                # Clic sin arrastre -> abrir/desplegar panel
                self.expand_panel()

    def enterEvent(self, event):
        if not self.is_expanded:
            # Al pasar el cursor, resaltar con opacidad completa
            self.setWindowOpacity(1.0)
        else:
            # Si está expandido, renovar temporizador de inactividad
            if self.config.get("auto_collapse", True):
                self.auto_hide_timer.start(8000)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.is_expanded and not self._is_dragging_flap:
            # Al retirar el cursor, volver a semi-opaco
            self.setWindowOpacity(0.60)
        super().leaveEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.is_expanded:
                self.collapse_panel()
        super().keyPressEvent(event)
