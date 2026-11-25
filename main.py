"""
Lanzador Flotante de Acceso Rápido para la Suite de IA Local.
Orquestador principal y bandeja del sistema con control de instancia única.
"""

import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_DIR)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

from launcher_window import QuickLauncherWidget, APPS_CONFIG, launch_or_activate

SOCKET_NAME = "LanzadorSuiteIA_SingleInstance_2026"

def ensure_single_instance(app, on_activate_cb, on_quit_cb=None) -> bool:
    test_socket = QLocalSocket()
    test_socket.connectToServer(SOCKET_NAME)
    if test_socket.waitForConnected(800):
        test_socket.write(b"ACTIVATE")
        test_socket.waitForBytesWritten(300)
        test_socket.disconnectFromServer()
        return False

    QLocalServer.removeServer(SOCKET_NAME)
    server = QLocalServer()
    if server.listen(SOCKET_NAME):
        def handle_conn():
            client = server.nextPendingConnection()
            if client:
                if client.bytesAvailable() > 0 or client.waitForReadyRead(300):
                    data = client.readAll().data().decode("utf-8", errors="ignore")
                    if "QUIT" in data:
                        if on_quit_cb:
                            on_quit_cb()
                        else:
                            app.quit()
                    elif "ACTIVATE" in data:
                        on_activate_cb()
                client.disconnectFromServer()
        server.newConnection.connect(handle_conn)
        app._server = server
        return True
    return True

def create_tray_pixmap() -> QPixmap:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QColor("#18181b"))
    painter.setPen(QColor("#38bdf8"))
    painter.drawRoundedRect(2, 2, 28, 28, 8, 8)

    painter.setFont(QFont("Segoe UI Emoji", 13, QFont.Weight.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "⚡")
    painter.end()
    return pixmap

def main():
    import traceback
    try:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)

        widget = QuickLauncherWidget()

        def on_activate():
            widget.show()
            widget.setWindowState(widget.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
            widget.raise_()
            widget.activateWindow()
            widget.expand_panel()

        if not ensure_single_instance(app, on_activate):
            sys.exit(0)

        # Bandeja del sistema
        tray_icon = QSystemTrayIcon()
        tray_icon.setIcon(QIcon(create_tray_pixmap()))
        tray_icon.setToolTip("Lanzador Suite IA Local (Acceso Rápido)")

        menu = QMenu()
        act_show = menu.addAction("Mostrar Panel Suite IA")
        act_show.triggered.connect(on_activate)

        menu.addSeparator()

        for app_info in APPS_CONFIG:
            act = menu.addAction(f"{app_info['icon']} {app_info['title']}")
            act.triggered.connect(lambda checked, info=app_info: launch_or_activate(info))

        menu.addSeparator()

        act_side = menu.addAction("⇋ Cambiar Lado (Izquierda/Derecha)")
        act_side.triggered.connect(widget.toggle_dock_side)

        act_exit = menu.addAction("✕ Salir del Lanzador")
        act_exit.triggered.connect(app.quit)

        tray_icon.setContextMenu(menu)
        tray_icon.activated.connect(lambda r: on_activate() if r in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick) else None)
        tray_icon.show()

        widget.show()
        widget.raise_()
        widget.activateWindow()
        widget.expand_panel()

        # Notificación informativa en la bandeja de Windows
        try:
            tray_icon.showMessage(
                "⚡ Suite IA Local Activa",
                "El lanzador está listo en el borde de tu pantalla. Haz clic en ⚡ para desplegar o arrástralo libremente.",
                QSystemTrayIcon.MessageIcon.Information,
                3500
            )
        except Exception:
            pass

        sys.exit(app.exec())
    except Exception as e:
        with open(os.path.join(APP_DIR, "launcher_crash.log"), "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())

if __name__ == "__main__":
    main()
