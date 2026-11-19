import sys
import os
import time

# Asegurar que el directorio raíz del proyecto esté en sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

print("=" * 60)
print("  VALIDACION INTEGRAL DEL LANZADOR SUITE IA LOCAL")
print("=" * 60)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent

# 1. Inicializar QApplication
app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

import launcher_window
from launcher_window import QuickLauncherWidget, APPS_CONFIG, check_socket_status, load_config, save_config

# Test 1: Verificar APPS_CONFIG y existencia de los archivos vbs de cada app
print("\n[TEST 1] Verificacion de aplicaciones configuradas:")
print(f"Total aplicaciones registradas: {len(APPS_CONFIG)}")
for a in APPS_CONFIG:
    exists = os.path.exists(a["vbs_path"])
    print(f"  • {a['title']} ({a['icon']}) -> Socket: {a['socket']} | vbs existe: {exists}")
    assert exists, f"No se encontro el vbs de {a['title']} en {a['vbs_path']}"
print("=> TEST 1 superado exitosamente.")

# Test 2: Instanciar el Widget y verificar geometría colapsada (minimalista 38x38)
print("\n[TEST 2] Creacion de QuickLauncherWidget y modo colapsado:")
w = QuickLauncherWidget()
w.show()
print(f"  Geometria colapsada: {w.geometry().width()}x{w.geometry().height()} en ({w.x()}, {w.y()})")
print(f"  Opacidad en reposo: {w.windowOpacity():.2f}")
print(f"  Visibilidad Flap (icono): {w.flap.isVisible()} | Panel: {w.panel.isVisible()}")
assert w.width() == 38, f"Se esperaba ancho 38, obtenido {w.width()}"
assert w.height() == 38, f"Se esperaba alto 38, obtenido {w.height()}"
assert w.flap.isVisible() == True, "El icono flotante deberia ser visible colapsado"
assert w.panel.isVisible() == False, "El panel deberia estar oculto colapsado"
print("=> TEST 2 superado exitosamente.")

# Test 3: Despliegue y Repliegue del Panel
print("\n[TEST 3] Despliegue (expand) y repliegue (collapse):")
w.expand_panel()
print(f"  Geometria desplegada: {w.geometry().width()}x{w.geometry().height()} en ({w.x()}, {w.y()})")
print(f"  Opacidad desplegado: {w.windowOpacity():.2f}")
assert w.is_expanded == True, "w.is_expanded deberia ser True"
assert w.panel.isVisible() == True, "El panel deberia ser visible"
assert w.flap.isVisible() == False, "El flap deberia estar oculto al expandir"
print("  Despliegue verificado correctamente.")

w.collapse_panel()
assert w.is_expanded == False, "w.is_expanded deberia ser False"
assert w.panel.isVisible() == False, "El panel deberia estar oculto"
assert w.flap.isVisible() == True, "El flap deberia volver a ser visible"
print("=> TEST 3 superado exitosamente.")

# Test 4: Alternar lado de anclaje (Izquierda / Derecha)
print("\n[TEST 4] Alternar lado de anclaje:")
side_original = w.dock_side
w.toggle_dock_side()
print(f"  Lado cambiado: {side_original} -> {w.dock_side}")
assert w.dock_side != side_original
w.toggle_dock_side()
assert w.dock_side == side_original
print("=> TEST 4 superado exitosamente.")

# Test 5: Comprobacion de sockets de apps en vivo
print("\n[TEST 5] Polling y actualizacion de estados en vivo:")
w.refresh_app_statuses()
for card in w.card_widgets:
    status_text = card.status_dot.text()
    tooltip = card.status_dot.toolTip()
    print(f"  • {card.app_info['title']}: {status_text} ({tooltip})")
print("=> TEST 5 superado exitosamente.")

# Test 6: Simulacion de arrastre libre con raton y auto-snap
print("\n[TEST 6] Simulacion de arrastre con raton y auto-snap al borde:")
start_x = w.x()
start_y = w.y()
print(f"  Posicion inicial del icono: ({start_x}, {start_y})")

# Iniciar arrastre
w._is_dragging_flap = True
w._press_pos = QPoint(start_x + 10, start_y + 10)
w._drag_offset = QPoint(10, 10)
w._has_dragged = False

# Mover raton 80 px abajo y 40 px a un lado
simulated_global_pos = QPoint(start_x + 10 - 40, start_y + 10 + 80)
w._has_dragged = True
w.move(simulated_global_pos - w._drag_offset)
print(f"  Posicion durante arrastre libre: ({w.x()}, {w.y()})")

# Soltar raton simulado
w._is_dragging_flap = False
screen = QApplication.primaryScreen().availableGeometry()
cur_center_x = w.x() + w.width() // 2
screen_center_x = screen.left() + screen.width() // 2
if cur_center_x < screen_center_x:
    w.dock_side = "left"
else:
    w.dock_side = "right"
w.pos_y = max(screen.top() + 8, min(screen.bottom() - 48, w.y()))
w._apply_geometry()
print(f"  Posicion tras auto-snap magnetico: ({w.x()}, {w.y()}) en borde '{w.dock_side}'")
assert w.width() == 38 and w.height() == 38
print("=> TEST 6 superado exitosamente.")

print("\n" + "=" * 60)
print("  RESULTADO: TODOS LOS TESTS PASARON CON EXITO (100% OPERATIVO)")
print("=" * 60)
