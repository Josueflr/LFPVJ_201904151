from analizador_lexico import (
    TK_PIXELLANG, TK_CONFIG, TK_PAINT_BLOQUE, TK_BOARD, TK_NAME,
    TK_PIXEL, TK_HORIZONTAL, TK_VERTICAL, TK_FILLOUT, TK_PAINT_ALL,
    TK_COLUMNS, TK_ROWS, TK_LLAVE_ABRE, TK_LLAVE_CIERRA, TK_DOS_PUNTOS,
    TK_PUNTO_COMA, TK_COMA, TK_NUMERO, TK_CADENA, TK_COLOR_HEX
)


class Tablero:
    """Representa el tablero de pixeles y ejecuta las instrucciones de pintado."""

    def __init__(self, columnas, filas):
        self.columnas = columnas
        self.filas = filas
        self.celdas = [[None] * columnas for _ in range(filas)]
        self.nombre = "imagen"
        self._invocaciones = {}

    def _registrar_invocacion(self, color):
        self._invocaciones[color] = self._invocaciones.get(color, 0) + 1

    def _pintar_celda(self, x, y, color, instruccion):
        if 0 <= x < self.columnas and 0 <= y < self.filas:
            self.celdas[y][x] = {'color': color, 'instruccion': instruccion}

    def pintar_pixel(self, x, y, color):
        self._registrar_invocacion(color)
        self._pintar_celda(x, y, color, 'PIXEL')

    def pintar_horizontal(self, fila, x_ini, x_fin, color):
        self._registrar_invocacion(color)
        inicio = min(x_ini, x_fin)
        fin = max(x_ini, x_fin)
        for x in range(inicio, fin + 1):
            self._pintar_celda(x, fila, color, 'HORIZONTAL')

    def pintar_vertical(self, col, y_ini, y_fin, color):
        self._registrar_invocacion(color)
        inicio = min(y_ini, y_fin)
        fin = max(y_ini, y_fin)
        for y in range(inicio, fin + 1):
            self._pintar_celda(col, y, color, 'VERTICAL')

    def pintar_fillout(self, x1, y1, x2, y2, color):
        self._registrar_invocacion(color)
        xs, xe = min(x1, x2), max(x1, x2)
        ys, ye = min(y1, y2), max(y1, y2)
        for y in range(ys, ye + 1):
            for x in range(xs, xe + 1):
                self._pintar_celda(x, y, color, 'FILLOUT')

    def pintar_todo(self, color):
        self._registrar_invocacion(color)
        for y in range(self.filas):
            for x in range(self.columnas):
                self._pintar_celda(x, y, color, 'PAINT-ALL')

    def total_celdas(self):
        return self.columnas * self.filas

    def celdas_pintadas(self):
        return sum(1 for y in range(self.filas)
        for x in range(self.columnas)
            if self.celdas[y][x] is not None)

    def celdas_vacias(self):
        return self.total_celdas() - self.celdas_pintadas()

    def get_coordenadas_pintadas(self):
        resultado = []
        for y in range(self.filas):
            for x in range(self.columnas):
                if self.celdas[y][x] is not None:
                    celda = self.celdas[y][x]
                    resultado.append((x, y, celda['color'], celda['instruccion']))
        return resultado

    def get_colores_usados(self):
        celdas_por_color = {}
        for y in range(self.filas):
            for x in range(self.columnas):
                if self.celdas[y][x] is not None:
                    color = self.celdas[y][x]['color']
                    celdas_por_color[color] = celdas_por_color.get(color, 0) + 1

        todos = set(list(self._invocaciones.keys()) + list(celdas_por_color.keys()))
        resultado = {}
        for color in todos:
            resultado[color] = {
                'invocaciones': self._invocaciones.get(color, 0),
                'celdas': celdas_por_color.get(color, 0)
            }
        return resultado


class InterpretadorPixelLang:
    """Recorre la lista de tokens y ejecuta las instrucciones sobre el tablero."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.tablero = None

    def _actual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consumir(self):
        tok = self._actual()
        if tok:
            self.pos += 1
        return tok

    def _esperar(self, tipo):
        tok = self._actual()
        if tok and tok.tipo == tipo:
            self.pos += 1
            return tok
        return None

    def interpretar(self):
        if not self.tokens:
            return None

        self._esperar(TK_PIXELLANG)
        self._esperar(TK_LLAVE_ABRE)
        self._parsear_config()
        self._esperar(TK_COMA)
        self._parsear_paint()
        self._esperar(TK_LLAVE_CIERRA)

        return self.tablero

    def _parsear_config(self):
        if not (self._actual() and self._actual().tipo == TK_CONFIG):
            return
        self._esperar(TK_CONFIG)
        self._esperar(TK_LLAVE_ABRE)

        while self._actual() and self._actual().tipo != TK_LLAVE_CIERRA:
            tok = self._actual()
            if tok.tipo == TK_BOARD:
                self._parsear_board()
            elif tok.tipo == TK_NAME:
                self._parsear_name()
            else:
                self._consumir()

        self._esperar(TK_LLAVE_CIERRA)

    def _parsear_board(self):
        self._esperar(TK_BOARD)
        self._esperar(TK_DOS_PUNTOS)
        self._esperar(TK_COLUMNS)
        cols_tok = self._esperar(TK_NUMERO)
        self._esperar(TK_ROWS)
        rows_tok = self._esperar(TK_NUMERO)
        self._esperar(TK_PUNTO_COMA)

        if cols_tok and rows_tok:
            cols = int(cols_tok.lexema)
            rows = int(rows_tok.lexema)
            if cols > 0 and rows > 0:
                self.tablero = Tablero(cols, rows)

    def _parsear_name(self):
        self._esperar(TK_NAME)
        self._esperar(TK_DOS_PUNTOS)
        name_tok = self._esperar(TK_CADENA)
        self._esperar(TK_PUNTO_COMA)

        if name_tok and self.tablero:
            self.tablero.nombre = name_tok.lexema[1:-1]

    def _parsear_paint(self):
        if not (self._actual() and self._actual().tipo == TK_PAINT_BLOQUE):
            return
        self._esperar(TK_PAINT_BLOQUE)
        self._esperar(TK_LLAVE_ABRE)

        while self._actual() and self._actual().tipo != TK_LLAVE_CIERRA:
            tok = self._actual()
            if tok.tipo == TK_PIXEL:
                self._parsear_pixel()
            elif tok.tipo == TK_HORIZONTAL:
                self._parsear_horizontal()
            elif tok.tipo == TK_VERTICAL:
                self._parsear_vertical()
            elif tok.tipo == TK_FILLOUT:
                self._parsear_fillout()
            elif tok.tipo == TK_PAINT_ALL:
                self._parsear_paint_all()
            else:
                self._consumir()

        self._esperar(TK_LLAVE_CIERRA)

    def _parsear_pixel(self):
        self._esperar(TK_PIXEL)
        self._esperar(TK_DOS_PUNTOS)
        x_tok = self._esperar(TK_NUMERO)
        y_tok = self._esperar(TK_NUMERO)
        color_tok = self._esperar(TK_COLOR_HEX)
        self._esperar(TK_PUNTO_COMA)

        if x_tok and y_tok and color_tok and self.tablero:
            self.tablero.pintar_pixel(int(x_tok.lexema), int(y_tok.lexema),
            color_tok.lexema)

    def _parsear_horizontal(self):
        self._esperar(TK_HORIZONTAL)
        self._esperar(TK_DOS_PUNTOS)
        fila_tok = self._esperar(TK_NUMERO)
        xi_tok = self._esperar(TK_NUMERO)
        xf_tok = self._esperar(TK_NUMERO)
        color_tok = self._esperar(TK_COLOR_HEX)
        self._esperar(TK_PUNTO_COMA)

        if fila_tok and xi_tok and xf_tok and color_tok and self.tablero:
            self.tablero.pintar_horizontal(int(fila_tok.lexema), int(xi_tok.lexema),
            int(xf_tok.lexema), color_tok.lexema)

    def _parsear_vertical(self):
        self._esperar(TK_VERTICAL)
        self._esperar(TK_DOS_PUNTOS)
        col_tok = self._esperar(TK_NUMERO)
        yi_tok = self._esperar(TK_NUMERO)
        yf_tok = self._esperar(TK_NUMERO)
        color_tok = self._esperar(TK_COLOR_HEX)
        self._esperar(TK_PUNTO_COMA)

        if col_tok and yi_tok and yf_tok and color_tok and self.tablero:
            self.tablero.pintar_vertical(int(col_tok.lexema), int(yi_tok.lexema),
            int(yf_tok.lexema), color_tok.lexema)

    def _parsear_fillout(self):
        self._esperar(TK_FILLOUT)
        self._esperar(TK_DOS_PUNTOS)
        x1_tok = self._esperar(TK_NUMERO)
        y1_tok = self._esperar(TK_NUMERO)
        x2_tok = self._esperar(TK_NUMERO)
        y2_tok = self._esperar(TK_NUMERO)
        color_tok = self._esperar(TK_COLOR_HEX)
        self._esperar(TK_PUNTO_COMA)

        if x1_tok and y1_tok and x2_tok and y2_tok and color_tok and self.tablero:
            self.tablero.pintar_fillout(int(x1_tok.lexema), int(y1_tok.lexema),
            int(x2_tok.lexema), int(y2_tok.lexema),color_tok.lexema)

    def _parsear_paint_all(self):
        self._esperar(TK_PAINT_ALL)
        self._esperar(TK_DOS_PUNTOS)
        color_tok = self._esperar(TK_COLOR_HEX)
        self._esperar(TK_PUNTO_COMA)

        if color_tok and self.tablero:
            self.tablero.pintar_todo(color_tok.lexema)
