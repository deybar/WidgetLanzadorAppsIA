# 🖥️ 03. Guía de Uso e Interacción

En esta guía se describen todas las funciones visuales, atajos de interacción y modos de ejecución del **Lanzador Flotante de Acceso Rápido**.

---

## 1. Estados de la Interfaz

La interfaz posee dos estados claramente diferenciados:

| Estado | Aspecto | Dimensiones | Función |
|---|---|---|---|
| **Colapsado (Icono Minimalista)** | Burbuja ultra-compacta semi-opaca con icono `⚡` | Ancho: 20 px<br>Alto: 20 px | Modo reposo discreto (72% opacidad). Se ilumina al 100% al pasar el cursor. |
| **Expandido (Panel)** | Panel flotante oscuro con sombra y tarjetas de apps | Ancho: 285 px<br>Alto: 325 px | Muestra las 3 aplicaciones con su estado y opciones de control. |

---

## 2. Acciones del Ratón y Gestos

### A. Desplegar el Panel
- **Un solo clic** sobre el icono flotante `⚡` en el borde de la pantalla desplegará el panel completo.

### B. Movimiento Libre con el Ratón (Arrastre y Snap al Borde)
- Puedes mover el icono a cualquier altura y a cualquier lado de tu pantalla libremente:
  1. Haz **clic sostenido (botón izquierdo)** sobre el icono `⚡`.
  2. Arrástralo libremente con el ratón por la pantalla a donde desees.
  3. Al soltar el ratón, el icono se acopla magnéticamente (*snap*) de forma automática al borde de pantalla más cercano (izquierdo o derecho) a la altura exacta que elegiste.
- La posición y el lado quedan guardados automáticamente en `config.json`.

### C. Alternar Lado de Pantalla (Izquierda ⇋ Derecha)
- Además del arrastre libre, en el pie del panel desplegado puedes hacer clic en el botón **`⇋ Cambiar Lado`**.
- El lanzador volará instantáneamente al extremo opuesto de tu monitor, adaptando su orientación y sombras.

### D. Plegado Manual y Atajo Escape
- Haz clic en el botón de flecha en la esquina superior derecha del panel (`▶` si está a la derecha, `◀` si está a la izquierda).
- También puedes presionar la tecla **`Esc`** en cualquier momento para replegarlo de inmediato.

### E. Auto-Plegado por Inactividad
- Si despliegas el panel y no realizas ninguna acción durante **8 segundos**, el panel se repliega automáticamente al icono semi-opaco.
- Si pasas el puntero del ratón sobre el panel (*hover*), el temporizador se reinicia.

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
