REQUISITOS
----------
  - Python 3.8 o superior
  - Libreria Pillow (para exportar PNG)

INSTALACION DE DEPENDENCIAS
-----------------------------
  Abra una terminal en la carpeta del proyecto y ejecute:

      pip install -r requirements.txt

  o directamente:

      pip install pillow

EJECUCION
---------
  Desde la carpeta del proyecto ejecute:

      python main.py

  La ventana principal del analizador se abrira automaticamente.

ARCHIVOS DEL PROYECTO
----------------------
  main.py              — Interfaz grafica (tkinter)
  analizador_lexico.py — Analizador lexico (caracter por caracter)
  tablero.py           — Tablero e interpretador de instrucciones
  requirements.txt     — Dependencias Python
  manual_usuario.txt   — Este archivo


  USO DE LA INTERFAZ

1. AREA DE CODIGO
   Escriba o pegue su codigo PixelLang en el editor de la izquierda.
   Tambien puede cargar un archivo .pxl con el boton "Cargar .pxl".

2. BOTON ANALIZAR
   Ejecuta el analisis lexico sobre el codigo ingresado.
   - Si no hay errores: genera el tablero de pixeles en el panel derecho.
   - Si hay errores: los reporta en la barra de estado (use "Errores" para verlos).

3. TABLERO PIXELADO
   El panel derecho muestra el resultado visual de las instrucciones.
   Al mover el cursor sobre el tablero se muestran las coordenadas y el color
   de la celda en la barra de estado inferior.

4. BOTONES DE REPORTE
   - Tokens       : tabla con todos los tokens reconocidos (lexema, tipo, fila, columna).
   - Errores      : listado de errores lexicos con descripcion y posicion.
   - Tablero      : resumen del tablero (dimensiones, celdas pintadas/vacias, colores).
   - Colores      : colores hexadecimales usados, invocaciones y celdas afectadas.
   - Coordenadas  : detalle de cada celda pintada con su color e instruccion de origen.

5. EXPORTAR PNG
   Guarda el tablero como imagen PNG usando el nombre definido en NAME.
   Requiere Pillow instalado.

6. BOTON LIMPIAR
   Borra el codigo, el tablero y todos los reportes.

  SINTAXIS DEL LENGUAJE PIXELLANG


Estructura general:

    PixelLang {
      config {
        BOARD: columns <N> rows <M>;
        NAME: "nombre_imagen";
      },
      paint{
        PIXEL: <x> <y> #RRGGBB;
        HORIZONTAL: <fila> <xInicio> <xFin> #RRGGBB;
        VERTICAL: <columna> <yInicio> <yFin> #RRGGBB;
        FILLOUT: <x1> <y1> <x2> <y2> #RRGGBB;
        PAINT-ALL: #RRGGBB;
      }
    }

Instrucciones disponibles:

  PIXEL        Pinta una celda individual en (x, y).
  HORIZONTAL   Pinta una linea horizontal en una fila dada.
  VERTICAL     Pinta una linea vertical en una columna dada.
  FILLOUT      Rellena un area rectangular.
  PAINT-ALL    Pinta todas las celdas del tablero.

Reglas importantes:
  - Las coordenadas son (x=columna, y=fila), con (0,0) en la esquina superior izquierda.
  - Los colores deben tener exactamente 6 digitos hexadecimales: #RRGGBB.
  - Los numeros deben ser enteros positivos o cero.
  - Si dos instrucciones pintan la misma celda, prevalece la ultima.
  - El tablero solo se genera si no hay errores lexicos.

  TOKENS DEL LENGUAJE


  -  PIXELLANG     "PixelLang"
  -  CONFIG        "config"
  -  PAINT_BLOQUE  "paint"
  -  BOARD         "BOARD"
  -  NAME          "NAME"
  -  PIXEL         "PIXEL"
  -  HORIZONTAL    "HORIZONTAL"
  -  VERTICAL      "VERTICAL"
  -  FILLOUT       "FILLOUT"
  -  PAINT_ALL     "PAINT-ALL"
  -  COLUMNS       "columns"
  -  ROWS          "rows"
  -  LLAVE_ABRE    "{"
  -  LLAVE_CIERRA  "}"
  -  DOS_PUNTOS    ":"
  -  PUNTO_COMA    ";"
  -  COMA          ","
  -  NUMERO        entero positivo o cero
  -  CADENA        texto entre comillas dobles
  -  COLOR_HEX     color #RRGGBB

