
TK_PIXELLANG   = "PIXELLANG"
TK_CONFIG      = "CONFIG"
TK_PAINT_BLOQUE = "PAINT_BLOQUE"
TK_BOARD       = "BOARD"
TK_NAME        = "NAME"
TK_PIXEL       = "PIXEL"
TK_HORIZONTAL  = "HORIZONTAL"
TK_VERTICAL    = "VERTICAL"
TK_FILLOUT     = "FILLOUT"
TK_PAINT_ALL   = "PAINT_ALL"
TK_COLUMNS     = "COLUMNS"
TK_ROWS        = "ROWS"
TK_LLAVE_ABRE  = "LLAVE_ABRE"
TK_LLAVE_CIERRA = "LLAVE_CIERRA"
TK_DOS_PUNTOS  = "DOS_PUNTOS"
TK_PUNTO_COMA  = "PUNTO_COMA"
TK_COMA        = "COMA"
TK_NUMERO      = "NUMERO"
TK_CADENA      = "CADENA"
TK_COLOR_HEX   = "COLOR_HEX"

PALABRAS_RESERVADAS = {
    "PixelLang": TK_PIXELLANG,
    "config":    TK_CONFIG,
    "paint":     TK_PAINT_BLOQUE,
    "BOARD":     TK_BOARD,
    "NAME":      TK_NAME,
    "PIXEL":     TK_PIXEL,
    "HORIZONTAL": TK_HORIZONTAL,
    "VERTICAL":  TK_VERTICAL,
    "FILLOUT":   TK_FILLOUT,
    "PAINT-ALL": TK_PAINT_ALL,
    "columns":   TK_COLUMNS,
    "rows":      TK_ROWS,
}

HEX_VALIDOS = set("0123456789ABCDEFabcdef")


class Token:
    def __init__(self, tipo, lexema, fila, columna):
        self.tipo = tipo
        self.lexema = lexema
        self.fila = fila
        self.columna = columna

    def __repr__(self):
        return f"Token({self.tipo}, '{self.lexema}', fila={self.fila}, col={self.columna})"


class ErrorLexico:
    def __init__(self, descripcion, lexema, fila, columna):
        self.descripcion = descripcion
        self.lexema = lexema
        self.fila = fila
        self.columna = columna


class AnalizadorLexico:
    def __init__(self, codigo):
        self.codigo = codigo
        self.pos = 0
        self.fila = 1
        self.columna = 1
        self.tokens = []
        self.errores = []

    def _actual(self):
        if self.pos < len(self.codigo):
            return self.codigo[self.pos]
        return None

    def _avanzar(self):
        c = self.codigo[self.pos]
        self.pos += 1
        if c == '\n':
            self.fila += 1
            self.columna = 1
        else:
            self.columna += 1
        return c

    def analizar(self):
        self.tokens = []
        self.errores = []
        self.pos = 0
        self.fila = 1
        self.columna = 1

        while self.pos < len(self.codigo):
            c = self._actual()

            # Ignorar espacios y saltos de linea
            if c in ' \t\r\n':
                self._avanzar()
                continue

            fila_ini = self.fila
            col_ini = self.columna

            # Simbolos de un caracter
            if c == '{':
                self._avanzar()
                self.tokens.append(Token(TK_LLAVE_ABRE, '{', fila_ini, col_ini))

            elif c == '}':
                self._avanzar()
                self.tokens.append(Token(TK_LLAVE_CIERRA, '}', fila_ini, col_ini))

            elif c == ':':
                self._avanzar()
                self.tokens.append(Token(TK_DOS_PUNTOS, ':', fila_ini, col_ini))

            elif c == ';':
                self._avanzar()
                self.tokens.append(Token(TK_PUNTO_COMA, ';', fila_ini, col_ini))

            elif c == ',':
                self._avanzar()
                self.tokens.append(Token(TK_COMA, ',', fila_ini, col_ini))

            # Numeros enteros
            elif c.isdigit():
                num = ''
                while self._actual() is not None and self._actual().isdigit():
                    num += self._avanzar()
                self.tokens.append(Token(TK_NUMERO, num, fila_ini, col_ini))

            # Cadenas de texto entre comillas
            elif c == '"':
                self._avanzar()
                contenido = ''
                cerrada = False
                while self._actual() is not None:
                    sc = self._actual()
                    if sc == '"':
                        self._avanzar()
                        cerrada = True
                        break
                    if sc == '\n':
                        break
                    contenido += self._avanzar()
                if cerrada:
                    self.tokens.append(Token(TK_CADENA, f'"{contenido}"', fila_ini, col_ini))
                else:
                    self.errores.append(ErrorLexico(
                        'Cadena sin cerrar (falta comilla de cierre)',
                        f'"{contenido}', fila_ini, col_ini))

            # Colores hexadecimales #RRGGBB
            elif c == '#':
                self._avanzar()
                hex_leido = ''
                while self._actual() is not None and len(hex_leido) < 6:
                    hc = self._actual()
                    if hc in HEX_VALIDOS:
                        hex_leido += self._avanzar()
                    else:
                        break
                if len(hex_leido) == 6:
                    self.tokens.append(Token(TK_COLOR_HEX, '#' + hex_leido.upper(), fila_ini, col_ini))
                else:
                    self.errores.append(ErrorLexico(
                        f'Color hexadecimal invalido (se esperaban 6 digitos hex despues de #)',
                        '#' + hex_leido, fila_ini, col_ini))

            # Identificadores y palabras reservadas
            elif c.isalpha() or c == '_':
                ident = ''
                while self._actual() is not None and (self._actual().isalnum() or self._actual() == '_'):
                    ident += self._avanzar()

                # Caso especial: PAINT-ALL (contiene guion)
                if ident == 'PAINT' and self._actual() == '-':
                    resto = self.codigo[self.pos + 1: self.pos + 4] if self.pos + 3 < len(self.codigo) else ''
                    if resto == 'ALL':
                        tras_all = self.pos + 4
                        sig = self.codigo[tras_all] if tras_all < len(self.codigo) else ''
                        if not sig.isalnum() and sig != '_':
                            self._avanzar()
                            ident += '-'
                            ident += self._avanzar()  
                            ident += self._avanzar()  
                            ident += self._avanzar()  

                if ident in PALABRAS_RESERVADAS:
                    self.tokens.append(Token(PALABRAS_RESERVADAS[ident], ident, fila_ini, col_ini))
                else:
                    self.errores.append(ErrorLexico(
                        f'Identificador no reconocido: "{ident}"',
                        ident, fila_ini, col_ini))

            # Caracter no valido
            else:
                self.errores.append(ErrorLexico(
                    f'Caracter no valido: "{c}"',
                    c, fila_ini, col_ini))
                self._avanzar()

        return self.tokens, self.errores