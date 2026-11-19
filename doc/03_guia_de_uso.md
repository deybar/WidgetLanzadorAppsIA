# 🖥️ 03. Guía de Uso e Interacción

En esta guía se describen todas las funciones visuales, atajos de interacción y modos de ejecución del **Lanzador Flotante de Acceso Rápido**.

---

## 1. Estados de la Interfaz

La interfaz posee dos estados claramente diferenciados:

| Estado | Aspecto | Dimensiones | Función |
|---|---|---|---|
| **Colapsado (Solapa)** | Barra vertical pequeña con icono `⚡` y texto vertical `IA` | Ancho: 34 px<br>Alto: 100 px | Modo reposo. Se adhiere al borde sin obstruir el trabajo. |
| **Expandido (Panel)** | Panel flotante oscuro con sombra y tarjetas de apps | Ancho: 285 px<br>Alto: 330 px | Muestra las 3 aplicaciones, su estado y opciones de control. |

---

## 2. Acciones del Ratón y Gestos

### A. Desplegar el Panel
- **Un solo clic** sobre la solapa `⚡` en el borde de la pantalla desplegará el panel completo.

### B. Arrastre Vertical (Reposicionamiento de Altura)
- Si la solapa se encuentra sobre algún botón o barra de otra aplicación que utilices frecuentemente:
  1. Haz **clic sostenido (botón izquierdo)** sobre la solapa `⚡`.
  2. Arrastra el cursor hacia arriba o hacia abajo.
  3. Suelta el ratón.
- La nueva altura (`pos_y`) se guardará automáticamente en `config.json` para tus próximas sesiones.

### C. Alternar Lado de Pantalla (Izquierda ⇋ Derecha)
- En el pie del panel desplegado, haz clic en el botón **`⇋ Cambiar Lado`**.
- El lanzador volará instantáneamente al extremo opuesto de tu monitor (de derecha a izquierda o viceversa), adaptando la curvatura de sus bordes y sombras.

### D. Plegado Manual
- Haz clic en el botón de flecha en la esquina superior derecha del panel (`▶` si está a la derecha, `◀` si está a la izquierda).

### E. Auto-Plegado por Inactividad
- Si despliegas el panel y no realizas ninguna acción durante **8 segundos**, el panel se repliega automáticamente para no estorbar.
- Si pasas el puntero del ratón sobre el panel (*hover*), el temporizador se reinicia para permitirte leer o decidir cómodamente.

---

## 3. Tarjetas de Aplicación y Estados en Vivo

Cada tarjeta en el panel representa una herramienta de la suite:

```
+-------------------------------------------------------+
| [文A] Traductor de Texto                          ●  |
|      Selección con ratón (EN ↔ ES)                    |
+-------------------------------------------------------+
```

- **Punto Verde (`●`):** La aplicación ya está corriendo en segundo plano.
  - Al hacer clic, **no se duplica el proceso**; la ventana de la herramienta se traerá al frente y tomará el foco.
- **Punto Gris (`○`):** La aplicación está cerrada o inactiva.
  - Al hacer clic, se ejecutará silenciosamente en segundo plano sin ventanas negras de comandos.

---

## 4. Bandeja del Sistema (System Tray Icon)

En el área de notificación de Windows (junto al reloj), el lanzador ubica un icono con el símbolo `⚡`.

### Opciones con Clic Derecho sobre el Icono de la Bandeja:
1. **Mostrar Panel Suite IA:** Despliega el panel en la pantalla.
2. **Acceso Directo a Aplicaciones:**
   - `文A Traductor de Texto`
   - `💬 Traductor de Audio`
   - `🎙️ Asistente de Reunión`
3. **⇋ Cambiar Lado (Izquierda/Derecha):** Alterna el margen del dock.
4. **✕ Salir del Lanzador:** Cierra por completo el proceso del lanzador.

> [!TIP]
> Un doble clic (o clic simple) sobre el icono del rayo `⚡` en la bandeja también despliega el panel inmediatamente.

---

## 5. Modos de Ejecución Disponibles

El proyecto incluye 3 formas de iniciarse desde Windows:

### 1. `iniciar.vbs` *(Recomendado para uso diario)*
- **Comportamiento:** Inicio 100% invisible y silencioso.
- **Ventana CMD:** No aparece ninguna consola ni parpadeo.
- **Uso ideal:** Para iniciar el lanzador al encender Windows o desde accesos directos de escritorio.

### 2. `iniciar.bat` *(Lanzador por lotes estándar)*
- **Comportamiento:** Script por lotes que localiza el entorno virtual de Python y arranca el programa en segundo plano mediante `pythonw.exe`.

### 3. `debug_consola.bat` *(Para diagnóstico y desarrollo)*
- **Comportamiento:** Inicia el lanzador con una ventana de consola visible (`cmd.exe`) usando `python.exe`.
- **Uso ideal:** Cuando se realizan modificaciones en el código fuente para observar mensajes de depuración, errores de sintaxis o trazas de excepción en tiempo real.
