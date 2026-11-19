# 📚 Documentación Técnica del Lanzador Suite IA Local

Bienvenido a la documentación oficial del **Lanzador Flotante de Acceso Rápido**. Este repositorio contiene la interfaz de usuario, orquestador y centro de mando para las aplicaciones locales de inteligencia artificial en Windows.

---

## 🗂️ Índice de Contenidos

1. [**01. Propósito y Visión General**](01_proposito_y_vision.md)
   - Objetivo del lanzador y contexto en la suite de IA offline.
   - Propuesta de valor y principios de diseño (no invasivo, veloz, local).
   - Componentes que integran la suite completa.

2. [**02. Gestión de Aplicaciones y Comunicación IPC**](02_gestion_de_apps_e_ipc.md)
   - Arquitectura de comunicación entre procesos (IPC) con `QLocalSocket` y `QLocalServer`.
   - Protocolo de activación (`ACTIVATE`) y control de instancia única.
   - Sondeo de estado en vivo (*polling*) y verificación de salud de cada app.
   - Ejecución desatendida y silenciosa vía `os.startfile` y VBScript.
   - Topología de directorios y resolución de rutas relativas.

3. [**03. Guía de Uso e Interacción**](03_guia_de_uso.md)
   - Cómo interactuar con la solapa retraíble (`⚡ IA`).
   - Arrastre vertical a lo largo del margen de pantalla.
   - Alternancia de borde (Izquierda ⇋ Derecha).
   - Comportamiento de auto-plegado (*auto-collapse*).
   - Uso de la bandeja del sistema (*System Tray*).
   - Modos de ejecución disponibles (`iniciar.vbs`, `iniciar.bat`, `debug_consola.bat`).

4. [**04. Dependencias y Entorno de Ejecución**](04_dependencias_y_entorno.md)
   - Requisitos de software y sistema operativo.
   - Librerías necesarias (`PyQt6`).
   - Jerarquía de detección del intérprete de Python y entornos virtuales (`.venv`).
   - Consideraciones para pantallas High-DPI y permisos de Windows.

5. [**05. Utilidades y Herramientas**](05_utilidades_y_herramientas.md)
   - Catálogo de scripts del proyecto y sus responsabilidades.
   - Estructura y esquema del archivo `config.json`.
   - Mecanismo de captura de errores y depuración (`launcher_crash.log`).
   - Herramientas recomendadas para desarrollo y extensión.

---

> Para consultar el estado de avance, deudas técnicas identificadas y la hoja de ruta de desarrollo, revisa la [**Bitácora de Desarrollo (`BITACORA.md`)**](../BITACORA.md).
