import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

from analizador_lexico import AnalizadorLexico
from tablero import InterpretadorPixelLang

try:
    from PIL import Image, ImageDraw
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False


CODIGO_EJEMPLO = '''PixelLang {
  config {
    BOARD: columns 10 rows 8;
    NAME: "artepixel";
  },
  paint{
    PIXEL: 3 4 #FF0000;
    HORIZONTAL: 3 2 7 #80BCE8;
    VERTICAL: 5 1 6 #FFD966;
    FILLOUT: 2 2 6 6 #CCCCCC;
    PAINT-ALL: #FFD966;
  }
}'''


def configurar_estilos():
    estilo = ttk.Style()
    estilo.theme_use('clam')
    estilo.configure('Treeview',
    background='#252526',
    foreground='#d4d4d4',
    fieldbackground='#252526',
    rowheight=24,
    font=('Consolas', 10))
    estilo.configure('Treeview.Heading',
    background='#37373d',
    foreground='#cccccc',
    font=('Arial', 10, 'bold'),
    relief='flat')
    estilo.map('Treeview',
    background=[('selected', '#264f78')],
    foreground=[('selected', '#ffffff')])
    estilo.configure('TScrollbar', background='#3c3c3c', troughcolor='#252526')


class PixelLangApp:

    COLOR_FONDO       = '#1e1e1e'
    COLOR_BARRA       = '#2d2d2d'
    COLOR_BOTON       = '#0e639c'
    COLOR_BOTON_HOVER = '#1177bb'
    COLOR_TEXTO       = '#d4d4d4'
    COLOR_SUBTEXTO    = '#858585'
    COLOR_ACENTO      = '#4ec9b0'
    COLOR_ERROR       = '#f44747'
    COLOR_OK          = '#4ec9b0'

    def __init__(self, ventana_raiz):
        self.root = ventana_raiz
        self.root.title("PixelLang — Analizador Lexico")
        self.root.geometry("1300x740")
        self.root.minsize(900, 550)
        self.root.configure(bg=self.COLOR_FONDO)

        self.tokens = []
        self.errores = []
        self.tablero = None
        self.tam_celda = 40
        self.margen = 28

        configurar_estilos()
        self._construir_ui()



    def _construir_ui(self):
        self._barra_herramientas()
        self._area_principal()
        self._barra_estado()

    def _barra_herramientas(self):
        barra = tk.Frame(self.root, bg=self.COLOR_BARRA, pady=6)
        barra.pack(fill=tk.X, side=tk.TOP)

        def boton(parent, texto, cmd, bg='#0e639c', ancho=14):
            b = tk.Button(parent, text=texto, command=cmd,
                          bg=bg, fg='white', font=('Arial', 9, 'bold'),
                          relief=tk.FLAT, padx=10, pady=5,
                          cursor='hand2', activebackground='#1177bb',
                          activeforeground='white', width=ancho)
            b.pack(side=tk.LEFT, padx=4)
            return b

        boton(barra, "Analizar",      self.analizar,      bg='#388a34')
        boton(barra, "Limpiar",       self.limpiar,       bg='#8b1a1a')
        boton(barra, "Cargar .pxl",  self.cargar_archivo, bg='#0e639c')

        tk.Frame(barra, bg='#444', width=1).pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=4)

        boton(barra, "Tokens",        self.ver_tokens,          bg='#5a4f0e')
        boton(barra, "Errores",       self.ver_errores,         bg='#6e2020')
        boton(barra, "Tablero",       self.ver_reporte_tablero, bg='#5a4f0e')
        boton(barra, "Colores",       self.ver_colores,         bg='#5a4f0e')
        boton(barra, "Coordenadas",   self.ver_coordenadas,     bg='#5a4f0e')

        tk.Frame(barra, bg='#444', width=1).pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=4)

        boton(barra, "Exportar PNG",  self.exportar_imagen, bg='#0e5c6e')

    def _area_principal(self):
        contenedor = tk.Frame(self.root, bg=self.COLOR_FONDO)
        contenedor.pack(fill=tk.BOTH, expand=True, padx=6, pady=(4, 0))

        paned = tk.PanedWindow(contenedor, orient=tk.HORIZONTAL,
        bg='#3c3c3c', sashwidth=5, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True)

        frame_editor = tk.Frame(paned, bg=self.COLOR_FONDO)
        self._encabezado(frame_editor, "Codigo Fuente PixelLang")

        texto_cont = tk.Frame(frame_editor, bg=self.COLOR_FONDO)
        texto_cont.pack(fill=tk.BOTH, expand=True)

        sc_y = tk.Scrollbar(texto_cont, bg='#3c3c3c')
        sc_y.pack(side=tk.RIGHT, fill=tk.Y)
        sc_x = tk.Scrollbar(texto_cont, orient=tk.HORIZONTAL, bg='#3c3c3c')
        sc_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.editor = tk.Text(
            texto_cont,
            font=('Consolas', 12),
            bg='#1e1e1e', fg='#d4d4d4',
            insertbackground='#aeafad',
            undo=True, wrap=tk.NONE,
            yscrollcommand=sc_y.set,
            xscrollcommand=sc_x.set,
            borderwidth=0, padx=12, pady=10,
            selectbackground='#264f78')
        self.editor.pack(fill=tk.BOTH, expand=True)
        sc_y.config(command=self.editor.yview)
        sc_x.config(command=self.editor.xview)

        self.editor.insert('1.0', CODIGO_EJEMPLO)
        paned.add(frame_editor, minsize=370)

        frame_tablero = tk.Frame(paned, bg=self.COLOR_FONDO)
        self._encabezado(frame_tablero, "Tablero Pixelado")

        canvas_cont = tk.Frame(frame_tablero, bg=self.COLOR_FONDO)
        canvas_cont.pack(fill=tk.BOTH, expand=True)

        csv_y = tk.Scrollbar(canvas_cont, bg='#3c3c3c')
        csv_y.pack(side=tk.RIGHT, fill=tk.Y)
        csv_x = tk.Scrollbar(canvas_cont, orient=tk.HORIZONTAL, bg='#3c3c3c')
        csv_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(
            canvas_cont, bg='#141414',
            yscrollcommand=csv_y.set,
            xscrollcommand=csv_x.set,
            borderwidth=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        csv_y.config(command=self.canvas.yview)
        csv_x.config(command=self.canvas.xview)

        self.canvas.bind('<Motion>', self._hover_canvas)
        self.canvas.bind('<Leave>',  self._canvas_leave)

        paned.add(frame_tablero, minsize=320)

    def _encabezado(self, parent, texto):
        tk.Label(parent, text=texto, bg='#2d2d2d', fg='#9cdcfe',
        font=('Arial', 10, 'bold'), anchor='w',
        pady=4, padx=8).pack(fill=tk.X)

    def _barra_estado(self):
        barra = tk.Frame(self.root, bg='#007acc', pady=3)
        barra.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_estado = tk.Label(
            barra, text="Listo  —  Ingrese codigo PixelLang y presione Analizar",
            bg='#007acc', fg='white', font=('Arial', 9), anchor='w', padx=10)
        self.lbl_estado.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.lbl_coord = tk.Label(
            barra, text="", bg='#007acc', fg='#cce7ff',
            font=('Consolas', 9), padx=10)
        self.lbl_coord.pack(side=tk.RIGHT)


    def analizar(self):
        codigo = self.editor.get('1.0', tk.END)
        analizador = AnalizadorLexico(codigo)
        self.tokens, self.errores = analizador.analizar()
        self.tablero = None
        self.canvas.delete('all')

        if self.errores:
            self.lbl_estado.config(
                text=f"{len(self.errores)} error(es) lexico(s) — {len(self.tokens)} tokens reconocidos. No se genero el tablero.",
                bg='#5f1313')
        else:
            interpretador = InterpretadorPixelLang(self.tokens)
            self.tablero = interpretador.interpretar()

            if self.tablero:
                self._dibujar_tablero()
                self.lbl_estado.config(
                    text=f"Analisis exitoso — {len(self.tokens)} tokens  |  Tablero: {self.tablero.columnas} col × {self.tablero.filas} fil  |  Celdas pintadas: {self.tablero.celdas_pintadas()}",
                    bg='#007acc')
            else:
                self.lbl_estado.config(
                    text=f"{len(self.tokens)} tokens reconocidos. No se pudo construir el tablero (revise BOARD y NAME).",
                    bg='#6d4c00')

    def _dibujar_tablero(self):
        if not self.tablero:
            return

        CELL = self.tam_celda
        MAR  = self.margen
        cols = self.tablero.columnas
        filas = self.tablero.filas

        ancho_total  = MAR + cols * CELL + 10
        alto_total   = MAR + filas * CELL + 10
        self.canvas.config(scrollregion=(0, 0, ancho_total, alto_total))

        for x in range(cols):
            cx = MAR + x * CELL + CELL // 2
            self.canvas.create_text(cx, MAR // 2, text=str(x),
            fill='#6a9fb5', font=('Consolas', 8))


        for y in range(filas):
            cy = MAR + y * CELL + CELL // 2
            self.canvas.create_text(MAR // 2, cy, text=str(y),
            fill='#6a9fb5', font=('Consolas', 8))

        for y in range(filas):
            for x in range(cols):
                x1 = MAR + x * CELL
                y1 = MAR + y * CELL
                x2 = x1 + CELL
                y2 = y1 + CELL

                celda = self.tablero.celdas[y][x]
                relleno = celda['color'] if celda else '#1e1e1e'
                borde   = '#3a3a3a' if not celda else '#2a2a2a'

                self.canvas.create_rectangle(x1, y1, x2, y2,
                fill=relleno, outline=borde)

    def _hover_canvas(self, event):
        if not self.tablero:
            return
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        col  = int((cx - self.margen) // self.tam_celda)
        fila = int((cy - self.margen) // self.tam_celda)

        if 0 <= col < self.tablero.columnas and 0 <= fila < self.tablero.filas:
            celda = self.tablero.celdas[fila][col]
            if celda:
                info = f"  (col {col}, fila {fila})  →  {celda['color']}  [{celda['instruccion']}]"
            else:
                info = f"  (col {col}, fila {fila})  →  vacia"
            self.lbl_coord.config(text=info)
        else:
            self.lbl_coord.config(text="")

    def _canvas_leave(self, event):
        self.lbl_coord.config(text="")

    def limpiar(self):
        self.editor.delete('1.0', tk.END)
        self.canvas.delete('all')
        self.tokens = []
        self.errores = []
        self.tablero = None
        self.lbl_estado.config(
            text="Listo  —  Ingrese codigo PixelLang y presione Analizar",
            bg='#007acc')
        self.lbl_coord.config(text="")

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Abrir archivo PixelLang",
            filetypes=[("PixelLang", "*.pxl"), ("Texto", "*.txt"), ("Todos", "*.*")])
        if ruta:
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', contenido)
                nombre = os.path.basename(ruta)
                self.lbl_estado.config(text=f"  Archivo cargado: {nombre}", bg='#007acc')
            except Exception as e:
                messagebox.showerror("Error al cargar", str(e))

    def _ventana_reporte(self, titulo, ancho=700, alto=480):
        v = tk.Toplevel(self.root)
        v.title(titulo)
        v.geometry(f"{ancho}x{alto}")
        v.configure(bg=self.COLOR_FONDO)
        v.grab_set()
        return v

    def _tabla_con_scroll(self, parent, columnas, anchos):
        frame = tk.Frame(parent, bg=self.COLOR_FONDO)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        tree = ttk.Treeview(frame, columns=columnas, show='headings')
        for col, ancho in zip(columnas, anchos):
            tree.heading(col, text=col)
            tree.column(col, width=ancho, anchor='center', minwidth=40)

        sc_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        sc_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=sc_y.set, xscrollcommand=sc_x.set)

        sc_x.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc_y.pack(side=tk.RIGHT, fill=tk.Y)

        return tree

    def ver_tokens(self):
        if not self.tokens:
            messagebox.showinfo("Tokens", "No hay tokens. Ejecute el analisis primero.")
            return

        v = self._ventana_reporte(f"Reporte de Tokens  ({len(self.tokens)} tokens)", 720, 520)
        tk.Label(v, text=f"Total de tokens reconocidos: {len(self.tokens)}",
        bg=self.COLOR_FONDO, fg=self.COLOR_ACENTO,
        font=('Arial', 10, 'bold'), anchor='w', padx=12, pady=6).pack(fill=tk.X)

        cols = ('No.', 'Lexema', 'Tipo de Token', 'Fila', 'Columna')
        anchos = (50, 160, 180, 60, 80)
        tree = self._tabla_con_scroll(v, cols, anchos)

        for i, tok in enumerate(self.tokens, 1):
            tree.insert('', 'end', values=(i, tok.lexema, tok.tipo, tok.fila, tok.columna))

        tk.Button(v, text="Exportar HTML",
                  command=lambda: self._exportar_tokens_html(),
                  bg='#0e639c', fg='white', font=('Arial', 9),
                  relief=tk.FLAT, padx=10, pady=4).pack(pady=(0, 8))

    def ver_errores(self):
        if not self.errores:
            messagebox.showinfo("Errores Lexicos", "No se encontraron errores lexicos.")
            return

        v = self._ventana_reporte(f"Reporte de Errores Lexicos  ({len(self.errores)} error(es))", 780, 420)
        tk.Label(v, text=f"Errores encontrados: {len(self.errores)}",
        bg=self.COLOR_FONDO, fg=self.COLOR_ERROR,
        font=('Arial', 10, 'bold'), anchor='w', padx=12, pady=6).pack(fill=tk.X)

        cols = ('No.', 'Lexema', 'Descripcion', 'Fila', 'Columna')
        anchos = (45, 110, 340, 55, 70)
        tree = self._tabla_con_scroll(v, cols, anchos)
        tree.column('Descripcion', anchor='w')

        for i, err in enumerate(self.errores, 1):
            tree.insert('', 'end',
                        values=(i, err.lexema, err.descripcion, err.fila, err.columna),
                        tags=('err',))
        tree.tag_configure('err', foreground='#f44747')

    def ver_reporte_tablero(self):
        if not self.tablero:
            messagebox.showinfo("Tablero", "No hay tablero. Ejecute el analisis sin errores lexicos.")
            return

        v = self._ventana_reporte("Reporte del Tablero Generado", 440, 380)
        t = self.tablero

        datos = [
            ("Nombre de la imagen:",  f"{t.nombre}.png"),
            ("Columnas:",             str(t.columnas)),
            ("Filas:",                str(t.filas)),
            ("Total de celdas:",      str(t.total_celdas())),
            ("Celdas pintadas:",      str(t.celdas_pintadas())),
            ("Celdas vacias:",        str(t.celdas_vacias())),
            ("Colores distintos:",    str(len(t.get_colores_usados()))),
            ("Colores usados:",       ', '.join(t.get_colores_usados().keys()) or 'ninguno'),
        ]

        marco = tk.Frame(v, bg=self.COLOR_FONDO, padx=18, pady=16)
        marco.pack(fill=tk.BOTH, expand=True)

        for i, (label, valor) in enumerate(datos):
            tk.Label(marco, text=label, bg=self.COLOR_FONDO, fg=self.COLOR_SUBTEXTO,
            font=('Arial', 10), anchor='w').grid(row=i, column=0, sticky='nw', pady=5, padx=5)
            tk.Label(marco, text=valor, bg=self.COLOR_FONDO, fg=self.COLOR_TEXTO,
            font=('Consolas', 10, 'bold'), anchor='w',
            wraplength=220).grid(row=i, column=1, sticky='w', pady=5, padx=14)

    def ver_colores(self):
        if not self.tablero:
            messagebox.showinfo("Colores", "No hay tablero generado.")
            return
        colores = self.tablero.get_colores_usados()
        if not colores:
            messagebox.showinfo("Colores", "No se utilizaron colores.")
            return

        v = self._ventana_reporte(f"Reporte de Colores Utilizados  ({len(colores)} colores)", 560, 400)

        cols = ('Color Hex', 'Muestra', 'Invocaciones', 'Celdas Finales')
        anchos = (110, 80, 120, 130)
        tree = self._tabla_con_scroll(v, cols, anchos)

        for color, datos in colores.items():
            tree.insert('', 'end',
                        values=(color, '  ████████', datos['invocaciones'], datos['celdas']),
                        tags=(color,))
            try:
                tree.tag_configure(color, foreground=color)
            except tk.TclError:
                pass

    def ver_coordenadas(self):
        if not self.tablero:
            messagebox.showinfo("Coordenadas", "No hay tablero generado.")
            return
        coords = self.tablero.get_coordenadas_pintadas()
        if not coords:
            messagebox.showinfo("Coordenadas", "No hay celdas pintadas.")
            return

        v = self._ventana_reporte(f"Reporte de Coordenadas Pintadas  ({len(coords)} celdas)", 560, 500)
        tk.Label(v, text=f"Celdas con color final asignado: {len(coords)}",
        bg=self.COLOR_FONDO, fg=self.COLOR_ACENTO,
        font=('Arial', 10, 'bold'), anchor='w', padx=12, pady=6).pack(fill=tk.X)

        cols = ('X (Columna)', 'Y (Fila)', 'Color', 'Instruccion de Origen')
        anchos = (100, 80, 110, 160)
        tree = self._tabla_con_scroll(v, cols, anchos)

        for x, y, color, instruccion in coords:
            tree.insert('', 'end', values=(x, y, color, instruccion))


    def exportar_imagen(self):
        if not self.tablero:
            messagebox.showwarning("Exportar PNG", "No hay tablero para exportar.")
            return
        if not PIL_DISPONIBLE:
            messagebox.showerror(
                "Pillow no instalado",
                "Se necesita la libreria Pillow para exportar PNG.\n"
                "Instale con:  pip install pillow")
            return

        nombre_sugerido = (self.tablero.nombre or "imagen") + ".png"
        ruta = filedialog.asksaveasfilename(
            title="Guardar imagen PNG",
            initialfile=nombre_sugerido,
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Todos", "*.*")])
        if not ruta:
            return

        CELL = 40
        cols = self.tablero.columnas
        filas = self.tablero.filas

        img = Image.new('RGB', (cols * CELL, filas * CELL), '#1e1e1e')
        draw = ImageDraw.Draw(img)

        for y in range(filas):
            for x in range(cols):
                celda = self.tablero.celdas[y][x]
                color = celda['color'] if celda else '#1e1e1e'
                x1, y1 = x * CELL, y * CELL
                draw.rectangle([x1, y1, x1 + CELL - 1, y1 + CELL - 1], fill=color)

        img.save(ruta)
        messagebox.showinfo("Exportar PNG", f"Imagen guardada:\n{ruta}")

    def _exportar_tokens_html(self):
        if not self.tokens:
            return
        ruta = filedialog.asksaveasfilename(
            title="Exportar reporte de tokens",
            initialfile="reporte_tokens.html",
            defaultextension=".html",
            filetypes=[("HTML", "*.html")])
        if not ruta:
            return

        filas_html = '\n'.join(
            f'  <tr><td>{i}</td><td>{tok.lexema}</td><td>{tok.tipo}</td>'
            f'<td>{tok.fila}</td><td>{tok.columna}</td></tr>'
            for i, tok in enumerate(self.tokens, 1))

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Reporte de Tokens — PixelLang</title>
  <style>
    body  {{ font-family: 'Segoe UI', Arial, sans-serif; background:#1e1e1e; color:#d4d4d4; padding:24px; }}
    h1    {{ color:#4ec9b0; margin-bottom:4px; }}
    p     {{ color:#858585; margin-top:0; }}
    table {{ border-collapse:collapse; width:100%; margin-top:16px; }}
    th    {{ background:#2d2d2d; color:#9cdcfe; padding:10px 14px; text-align:center; font-size:13px; }}
    td    {{ padding:7px 14px; text-align:center; border-bottom:1px solid #2d2d2d; font-family:Consolas,monospace; font-size:12px; }}
    tr:nth-child(even) {{ background:#252526; }}
    tr:hover {{ background:#264f78; }}
  </style>
</head>
<body>
  <h1>Reporte de Tokens — PixelLang</h1>
  <p>Total de tokens reconocidos: {len(self.tokens)}</p>
  <table>
    <tr><th>No.</th><th>Lexema</th><th>Tipo de Token</th><th>Fila</th><th>Columna</th></tr>
{filas_html}
  </table>
</body>
</html>"""

        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(html)
        messagebox.showinfo("Exportar HTML", f"Reporte exportado:\n{ruta}")


if __name__ == '__main__':
    raiz = tk.Tk()
    app = PixelLangApp(raiz)
    raiz.mainloop()
    