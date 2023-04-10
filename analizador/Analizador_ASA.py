# Analizador de Los Betes Ra!
from lib2to3.pgen2.token import TILDE
from explorador.Explorador import TipoComponente, ComponenteLéxico
from utils.asa import ÁrbolSintáxisAbstracta, NodoÁrbol, TipoNodo

"""
Clase Analizador
Se encarga de realizar el análsis por descenso recursivo 
"""
class Analizador():
    # Información de la estructura que contiene los componente léxicos
    componentes_léxicos: list
    cantidad_componentes: int

    # Información del componente léxico actual
    posición_componente_actual: int
    componente_actual: ComponenteLéxico

    # Diccionarios para poder acceder a las funciones para analizar las reglas del programa
    REGLAS_PROGRAMA: dict
    REGLAS_LITERAL: dict
    TIPO_NODO_A_TIPO_COMPONENTE : dict

    def __init__(self, lista_componentes):
        self.componentes_léxicos = lista_componentes
        self.cantidad_componentes = len(lista_componentes)
        self.posición_componente_actual = 0
        self.componente_actual = lista_componentes[0]

        #Añade el árbol de sintáxis abstracta
        self.asa = ÁrbolSintáxisAbstracta()

        self.REGLAS_PROGRAMA = {
            'Func': self.__analizar_función,
            'Si': self.__analizar_condicional,
            'Rep': self.__analizar_repetición,
            'Inv': self.__analizar_invocación,
            'Operar': self.__analizar_operación
        }

        self.REGLAS_LITERAL = {
            TipoComponente.TEXTO: self.__verificar_texto,
            TipoComponente.ENTERO: self.__verificar_entero,
            TipoComponente.FLOTANTE: self.__verificar_flotante,
            TipoComponente.NULO: self.__verificar_nulo
        }

        self.TIPO_NODO_A_TIPO_COMPONENTE = {
            TipoComponente.OPERADOR : TipoNodo.OPERADOR,
            TipoComponente.TEXTO : TipoNodo.TEXTO,
            TipoComponente.ENTERO : TipoNodo.ENTERO,
            TipoComponente.FLOTANTE : TipoNodo.FLOTANTE,
            TipoComponente.IDENTIFICADOR : TipoNodo.IDENTIFICADOR,
            TipoComponente.TIPO_VARIABLE : TipoNodo.TIPO_VARIABLE,
            TipoComponente.TIPO_VALOR : TipoNodo.TIPO_VALOR,
            TipoComponente.NULO : TipoNodo.NULO,
            TipoComponente.OPERAR : TipoNodo.OPERAR,
            TipoComponente.COMPARADOR_MATEMATICO : TipoNodo.COMPARADOR_MATEMATICO
        }


    def analizar(self):
        """
        Método principal que inicia el análisis siguiendo el esquema de
        análisis por descenso recursivo
        """

        self.asa.raiz = self.__analizar_programa()

    def __analizar_programa(self):
        """
        Programa ::= (Función | Condicional | Asignación | Ciclo | Invocar)+
        """
        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        # Puede ser tanto un Funcion, una Condicional, una Asignación, Ciclo, Invocar o una Asginación
        # Pero no puede ser una operación
        while self.componente_actual.tipo == TipoComponente.TIPO_VARIABLE \
            or self.componente_actual.texto in self.REGLAS_PROGRAMA and self.componente_actual.texto != 'Operar':

            # Si es un tipo variable es el comienzo de una asingación
            if (self.componente_actual.tipo == TipoComponente.TIPO_VARIABLE):
                nodos_nuevos += [self.__analizar_asignación()]


            # Si otra de las reglas
            elif (self.componente_actual.texto in self.REGLAS_PROGRAMA):
                nodos_nuevos += [self.REGLAS_PROGRAMA[self.componente_actual.texto]()]

        if self.posición_componente_actual != len(self.componentes_léxicos) - 1 and self.componente_actual != self.componentes_léxicos.pop():
            self.__generar_error()

        return NodoÁrbol(TipoNodo.PROGRAMA, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})

    """
    -------------------------------------------------
    - Bloque de funciones para analizar una función -
    -------------------------------------------------
    """

    def __analizar_función(self):
        """
        Func Identificador {Parametro} -> (Instrucciones)+ <-
        """
        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        self.__verificar('Func')
        nodos_nuevos += [self.__verificar_identificador()]
        self.__verificar('{')

        if self.componente_actual.tipo == TipoComponente.TIPO_VALOR:
            nodos_nuevos += [self.__analizar_parámetros()]

        self.__verificar('}')

        # Según la gramática el rommpe solo va en un bloque condicional
        nodos_nuevos += [self.__analizar_bloque_instrucciones_sin_rompe()]

        return NodoÁrbol(TipoNodo.FUNCIÓN, contenido=nodos_nuevos[0].contenido, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})

    def __analizar_invocación(self):
        """
        Invocar ::= Inv Identificador {Parámetro}
        """
        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        self.__verificar('Inv')
        nodos_nuevos += [self.__verificar_identificador()]
        self.__verificar('{')

        if self.componente_actual.tipo == TipoComponente.TIPO_VALOR:
            nodos_nuevos += [self.__analizar_parámetros()]

        self.__verificar('}')
        return NodoÁrbol(TipoNodo.INVOCACION, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})


    # DUDAS CON RESPECTO A TipoNodo.
    def __analizar_parámetros(self):
        """
        Parametros ::= TipoValor Identificador (, TipoValor Identificador)+
        """
        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        # Tiene que haber un parámetro
        nodos_nuevos += [self.__verificar_tipo_valor()]
        nodos_nuevos += [self.__verificar_identificador()]

        while (self.componente_actual.texto == ','):
            self.__verificar(',')
            nodos_nuevos += [self.__verificar_tipo_valor()]
            nodos_nuevos += [self.__verificar_identificador()]
        return NodoÁrbol(TipoNodo.PARAMETROS, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea}) # <-

    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una condicional -
    -----------------------------------------------------
    """

    def __analizar_condicional(self):
        """
        Condicional ::= Si {ExpCondicional} ->  Instrucciones + <-
        """
        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        self.__verificar('Si')
        self.__verificar('{')
        nodos_nuevos += [self.__analizar_ExpCondicional()]
        self.__verificar('}')
        nodos_nuevos += [self.__analizar_bloque_con_rompe()]

        return NodoÁrbol(TipoNodo.CONDICIONAL, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})

    # DUDAS CON RESPECTO A TipoNodo.
    def __analizar_ExpCondicional(self):
        """
        ExpCondicional ::= (Comparación (( ^ | ~^) Comparación)*))
        """

        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        # La primera sección obligatoria la comparación
        nodos_nuevos += [self.__analizar_comparación()]

        # Esta parte es opcional
        while (self.componente_actual.tipo == TipoComponente.COMPARADOR_LOGICO):
            nodos_nuevos += [self.__verificar_comparador_lógico()]
            nodos_nuevos += [self.__analizar_comparación()]

        return NodoÁrbol(TipoNodo.EXPRCONDICIONAL, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})

    def __verificar_comparador_lógico(self):
        """
        Comparador ::= (^|~^)
        """
        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        nodos_nuevos += [self.__verificar_tipo_componente(TipoComponente.COMPARADOR_LOGICO)]
        return NodoÁrbol(TipoNodo.COMPARADOR_LOGICO, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})

    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una repeticion --
    -----------------------------------------------------
    """

    def __analizar_repetición(self):
        """
        Ciclo ::= Rep {Comparación}  -> Instrucciones + <-
        """
        nodos_nuevos = []

        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        self.__verificar('Rep')
        self.__verificar('{')
        nodos_nuevos += [self.__analizar_comparación()]
        self.__verificar('}')

        # La el romper o "break" solo viene en las repeticiones
        nodos_nuevos += [self.__analizar_bloque_instrucciones_sin_rompe()]
        return NodoÁrbol(TipoNodo.REPETICION, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})

    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una comparacion -
    -----------------------------------------------------
    """

    def __analizar_comparación(self):
        """
        Comparación ::= ((Valor | Operación) Comparador (Valor | Operación)
        """
        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        # Operación
        if (self.componente_actual.texto == 'Operar'):
            nodos_nuevos += [self.REGLAS_PROGRAMA[self.componente_actual.texto]()]

        # Valor
        elif (self.componente_actual.tipo in self.REGLAS_LITERAL):
            nodos_nuevos += [self.REGLAS_LITERAL[self.componente_actual.tipo]()]

        elif (self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):
            nodos_nuevos += [self.__verificar_identificador()]

        else:
            self.__generar_error()

        nodos_nuevos += [self.__verificar_comparador()]

        # Operación
        if (self.componente_actual.texto == 'Operar'):
            nodos_nuevos += [self.REGLAS_PROGRAMA[self.componente_actual.texto]()]

        # Valor
        elif (self.componente_actual.tipo in self.REGLAS_LITERAL):
            nodos_nuevos += [self.REGLAS_LITERAL[self.componente_actual.tipo]()]

        elif (self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):
            nodos_nuevos += [self.__verificar_identificador()]

        else:
            self.__generar_error()

        return NodoÁrbol(TipoNodo.COMPARACION, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})

    def __verificar_comparador(self):
        """
        Comparador ::= (<|>|<=|>=|~==|==)
        """
        nodos_nuevos = []
        return self.__verificar_tipo_componente(TipoComponente.COMPARADOR_MATEMATICO)
        #return NodoÁrbol(TipoNodo.COMPARADOR_MATEMATICO, nodos=[])

    """
    ---------------------------------------------------------------
    - Bloque de funciones para analizar un bloque de instrucciones -
    ----------------------------------------------------------------
    """

    def __analizar_bloque_instrucciones_sin_rompe(self):
        """
        BloqueInstrucciones ::= -> Instrucciones+ <-
        Instrucciones ::= (Ciclo | Condicional | Retorna | Asignación | OperarVariable | Invocar)
        """
        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        # Empieza por  '->'
        self.__verificar('->')

        # Si no es ninguno de las instrucciones es un error
        if (self.componente_actual.texto not in self.REGLAS_PROGRAMA and \
                self.componente_actual.tipo != TipoComponente.TIPO_VARIABLE and \
                self.componente_actual.texto != 'messirve' and self.componente_actual.tipo != TipoComponente.IDENTIFICADOR):
            self.__generar_error()

        # Analiza todas las instrucciones
        while (self.componente_actual.texto in self.REGLAS_PROGRAMA or \
               self.componente_actual.tipo == TipoComponente.TIPO_VARIABLE or \
               self.componente_actual.texto == 'messirve' or self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):

            if (self.componente_actual.texto in self.REGLAS_PROGRAMA or \
                    self.componente_actual.tipo == TipoComponente.TIPO_VARIABLE or \
                    self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):

                nodos_nuevos += [self.__analizar_instrucción()]

            # Si es retorno termina el bloque en específico
            elif (self.componente_actual.texto == 'messirve'):
                nodos_nuevos += [self.__analizar_retorno()]
                break

        # Obligatorio
        self.__verificar('<-')
        return NodoÁrbol(TipoNodo.INSTRUCCIONES, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})

    def __analizar_bloque_con_rompe(self):
        """
        BloqueInstrucciones ::= -> Instrucciones+ | Rompe <-
        Instrucciones ::= (Ciclo | Condicional | Retorna | Asignación | OperarVariable | Invocar)

        Similiar a la anterior, nada más añade el componente para romper un bucle
        """
        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        self.__verificar('->')

        if (self.componente_actual.texto not in self.REGLAS_PROGRAMA and \
                self.componente_actual.tipo != TipoComponente.TIPO_VARIABLE and \
                self.componente_actual.texto != 'siu' and self.componente_actual.texto != 'messirve' and \
                self.componente_actual.tipo != TipoComponente.IDENTIFICADOR):
            self.__generar_error()

        while (self.componente_actual.texto in self.REGLAS_PROGRAMA or \
               self.componente_actual.tipo == TipoComponente.TIPO_VARIABLE or \
               self.componente_actual.texto == 'siu' or self.componente_actual.texto == 'messirve' or \
               self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):

            if (self.componente_actual.texto in self.REGLAS_PROGRAMA or \
                    self.componente_actual.tipo == TipoComponente.TIPO_VARIABLE or \
                    self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):

                nodos_nuevos += [self.__analizar_instrucción()]


            elif (self.componente_actual.texto == 'siu'):
                self.__analizar_rompe()
                break

            elif (self.componente_actual.texto == 'messirve'):
                nodos_nuevos += [self.__analizar_retorno()]
                break

        # Obligatorio
        self.__verificar('<-')
        return NodoÁrbol(TipoNodo.INSTRUCCIONES, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})

    def __analizar_instrucción(self):
        """
        Instrucciones ::= (Ciclo | Condicional | Retorna | Asignación | OperarVariable | Invocar)
        """
        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        if (self.componente_actual.texto in self.REGLAS_PROGRAMA):
            nodos_nuevos += [self.REGLAS_PROGRAMA[self.componente_actual.texto]()]

        elif (self.componente_actual.tipo == TipoComponente.TIPO_VARIABLE):
            nodos_nuevos += [self.__analizar_asignación()]

        elif (self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):
            nodos_nuevos += [self._analizar_operar_variable()]


        else:
            self.__generar_error()
        return NodoÁrbol(TipoNodo.INSTRUCCIÓN, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})

    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una instruccion -
    -----------------------------------------------------
    """

    def _analizar_operar_variable(self):
        # Reasignación de variables ya definidas
        """
        OperarVariable::= Identificador ( <=> ) (Operación | Valor);

        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo)
        """
        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        # Identificador ya existente
        nodos_nuevos += [self.__verificar_identificador()]

        self.__verificar('<=>')

        # Si es una operación
        if (self.componente_actual.texto == 'Operar'):
            nodos_nuevos += [self.__analizar_operación()]

        # Si es un valor
        elif (self.componente_actual.tipo in self.REGLAS_LITERAL):
            nodos_nuevos += [self.REGLAS_LITERAL[self.componente_actual.tipo]()]

        # Si es un identificador
        elif (self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):
            nodos_nuevos += [self.__verificar_identificador()]
        
        elif (self.componente_actual.texto == 'Inv'):
            nodos_nuevos += [self.REGLAS_PROGRAMA[self.componente_actual.texto]()]

        else:
            self.__generar_error()

        # Obligatorio
        self.__verificar(';')
        return NodoÁrbol(TipoNodo.VARIABLE_OPERADOR, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})

    def __analizar_asignación(self):
        """
        Asignación ::= TipoVariable TipoValor Identificador <=> (Operación | Valor | Invocación);

        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo)
        """
        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea
    
        # El identificador en esta posición es obligatorio
        nodos_nuevos += [self.__verificar_tipo_variable()]

        nodos_nuevos += [self.__verificar_tipo_valor()]

        nodos_nuevos += [self.__verificar_identificador()]

        self.__verificar('<=>')

        # Verificar Indentificador
        if (self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):
            nodos_nuevos += [self.__verificar_identificador()]

        # Verificar Invocación
        elif (self.componente_actual.texto == 'Inv'):
            nodos_nuevos += [self.REGLAS_PROGRAMA[self.componente_actual.texto]()]

        # Verificar Literal
        elif (self.componente_actual.tipo in self.REGLAS_LITERAL):
            nodos_nuevos += [self.REGLAS_LITERAL[self.componente_actual.tipo]()]


        # Verificar Operación
        elif (self.componente_actual.texto == "Operar"):
            nodos_nuevos += [self.__analizar_operación()]

        else:
            self.__generar_error()

        self.__verificar(';')

        return NodoÁrbol(TipoNodo.ASIGNACION, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})

    def __analizar_operación(self):
        """
        Operación ::= Operar Valor  (Operadores Valor)+

        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo)
        """

        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        # Verifica el componente Operar
        self.__verificar('Operar')

        # No se puede operar un nulo
        if self.componente_actual.tipo in self.REGLAS_LITERAL \
                and self.componente_actual.texto != 'Nulo':

            nodos_nuevos += [self.REGLAS_LITERAL[self.componente_actual.tipo]()]

        # Si es un identificador
        elif self.componente_actual.tipo == TipoComponente.IDENTIFICADOR:
            nodos_nuevos += [self.__verificar_identificador()]

        elif (self.componente_actual.texto == 'Inv'):
            nodos_nuevos += [self.REGLAS_PROGRAMA[self.componente_actual.texto]()]

        else:
            self.__generar_error()

        nodos_nuevos += [self.__verificar_operador()]

        if self.componente_actual.tipo in self.REGLAS_LITERAL \
                and self.componente_actual.texto != 'Nulo':

            nodos_nuevos += [self.REGLAS_LITERAL[self.componente_actual.tipo]()]

        elif self.componente_actual.tipo == TipoComponente.IDENTIFICADOR:
            nodos_nuevos += [self.__verificar_identificador()]

        elif (self.componente_actual.texto == 'Inv'):
            nodos_nuevos += [self.REGLAS_PROGRAMA[self.componente_actual.texto]()]

        else:
            self.__generar_error()

        # Si es mas de una operación
        while (self.componente_actual.texto in ['+', '-', '*', '**', '/', '//', '%']):

            nodos_nuevos += [self.__verificar_operador()]

            if self.componente_actual.tipo in self.REGLAS_LITERAL \
                    and self.componente_actual.texto != 'Nulo':

                nodos_nuevos += [self.REGLAS_LITERAL[self.componente_actual.tipo]()]

            elif self.componente_actual.tipo == TipoComponente.IDENTIFICADOR:
                nodos_nuevos += [self.__verificar_identificador()]

            elif (self.componente_actual.texto == 'Inv'):
                nodos_nuevos += [self.REGLAS_PROGRAMA[self.componente_actual.texto]()]

            else:
                self.__generar_error()

        return NodoÁrbol(TipoNodo.OPERAR, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})

    def __analizar_retorno(self):
        """
        Retorna ::= messirve Valor;

        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo)
        """

        nodos_nuevos = []
        numero_linea = self.componente_actual.linea
        numero_columna = self.componente_actual.columna
        texto_linea = self.componente_actual.texto_linea

        self.__verificar('messirve')

        if self.componente_actual.tipo == TipoComponente.IDENTIFICADOR:
            nodos_nuevos += [self.__verificar_identificador()]

        elif (self.componente_actual.tipo in self.REGLAS_LITERAL):
            nodos_nuevos += [self.REGLAS_LITERAL[self.componente_actual.tipo]()]

        else:
            self.__generar_error()

        self.__verificar(';')

        return NodoÁrbol(TipoNodo.RETORNO, nodos=nodos_nuevos, atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})

    def __analizar_rompe(self):
        """
        Rompe ::= siu;

        """
        self.__verificar('siu')
        self.__verificar(';')

    """
    ---------------------------------------------------------------------
    - Bloque de funciones para verificar componentes léxicos o un texto -
    ---------------------------------------------------------------------
    """

    def __verificar_operador(self):
        """
        Operador ::= ( + | - | ** | * | // | / | % )
        """
        return self.__verificar_tipo_componente(TipoComponente.OPERADOR)


    def __verificar_texto(self):
        """
        Texto ::= ~/\w(\s\w)*)?~
        """
        return self.__verificar_tipo_componente(TipoComponente.TEXTO)


    def __verificar_entero(self):
        """
        Entero ::= (-)?\d+
        """
        return self.__verificar_tipo_componente(TipoComponente.ENTERO)


    def __verificar_flotante(self):
        """
        Flotante ::= (-)?\d+.(-)?\d+
        """
        return self.__verificar_tipo_componente(TipoComponente.FLOTANTE)


    def __verificar_identificador(self):
        """
        Identificador ::= [a-z][a-zA-Z0-9]+
        """
        return self.__verificar_tipo_componente(TipoComponente.IDENTIFICADOR)


    def __verificar_tipo_variable(self):
        """
        TipoVariable ::= (GLOB | CONS | LOC)
        """
        return self.__verificar_tipo_componente(TipoComponente.TIPO_VARIABLE)


    def __verificar_tipo_valor(self):
        """
        TipoValor::= (Texto |  Entero | Flotante)
        """
        return self.__verificar_tipo_componente(TipoComponente.TIPO_VALOR)


    def __verificar_nulo(self):
        """
        Nulo ::= Nulo
        """
        return self.__verificar_tipo_componente(TipoComponente.NULO)


    def __verificar_operación(self):
        """
        Operar ::= Operar
        """
        return self.__verificar_tipo_componente(TipoComponente.OPERAR)


    def __verificar(self, texto_esperado):
        """
        Verifica si el texto del componente léxico actual corresponde con
        el esperado cómo argumento
        """
        if self.componente_actual.texto != texto_esperado:
            self.__generar_error()

        else:
            self.__pasar_siguiente_componente()

    def __verificar_tipo_componente(self, tipo_esperado):
        """
        Verifica si el texto del componente léxico actual corresponde con
        el esperado cómo argumento
        """
        if self.componente_actual.tipo is not tipo_esperado:
            self.__generar_error()

        else:
            numero_linea = self.componente_actual.linea
            numero_columna = self.componente_actual.columna
            texto_linea = self.componente_actual.texto_linea

            nodo = NodoÁrbol(self.TIPO_NODO_A_TIPO_COMPONENTE[tipo_esperado], contenido =self.componente_actual.texto,
            atributos={'numeroLinea' : numero_linea, \
            'numeroColumna' : numero_columna, 'textoLinea' : texto_linea})
            self.__pasar_siguiente_componente()
            return nodo

    """
    -----------------------------
    - Bloque de funciones extra -
    -----------------------------
    """

    def __pasar_siguiente_componente(self):
        """
        Pasa al siguiente componente léxico
        """
        self.posición_componente_actual += 1

        if self.posición_componente_actual >= self.cantidad_componentes:
            return

        self.componente_actual = self.componentes_léxicos[self.posición_componente_actual]

    def __generar_error(self):
        """
        Por ahora imprime un error con la linea, y los números de línea y columna

        Por ahora la estrategia escogida fue que terminara inmediatamente el programa
        """

        print()
        print()
        print()
        print(
            "Se ha encontrado un error de sintáxis en la línea "
            + str(self.componente_actual.linea) + " y en la columna " + str(self.componente_actual.columna)
            + ":\n\n" + self.componente_actual.texto_linea + "\n" + (
                        self.componente_actual.columna - 1) * " " + "\u2191 \n\n"
            + "Porfavor corregir el error respectivo"
        )

        quit()


    def imprimir_asa(self):
        """
        Imprime el árbol de sintáxis abstracta
        """
        if self.asa.raiz is not None:
            self.asa.imprimir_preorden()
        
        print([])
            
