from lib2to3.pgen2.token import TILDE
from telnetlib import PRAGMA_HEARTBEAT
from utils.asa import ÁrbolSintáxisAbstracta, NodoÁrbol, TipoNodo
from utils.tipos_datos import TipoDatos


class TablaSímbolos:
    """
    Almacena información auxiliar para decorar el árbol de sintáxis
    abstracta con información de tipo y alcance.

    La estructura de símbolos es una lista de diccionarios
    """

    profundidad: int = 0
    símbolos: list = []

    def abrir_bloque(self):
        """
        Inicia un bloque de alcance (scope)
        """
        self.profundidad += 1

    def cerrar_bloque(self):
        """
        Termina un bloque de alcance y al acerlo elimina todos los
        registros de la tabla que estan en ese bloque
        """

        for registro in self.símbolos:
            if registro['profundidad'] == self.profundidad:
                self.símbolos.remove(registro)  

        self.profundidad -= 1

    def nuevo_registro(self, nodo, nombre_registro=''):
        """
        Introduce un nuevo registro a la tabla de símbolos
        """
        # El nombre del identificador + el nivel de profundidad

        """
        Los atributos son: nombre, profundidad, referencia

        referencia es una referencia al nodo dentro del árbol
        (Técnicamente todo lo 'modificable (mutable)' en python es una
        referencia siempre y cuando use la POO... meh... más o menos.
        """

        diccionario = {}

        diccionario['nombre'] = nodo.contenido
        diccionario['profundidad'] = self.profundidad
        diccionario['referencia'] = nodo

        self.símbolos.append(diccionario)

    def verificar_existencia(self, nombre):
        """
        Verficia si un identificador existe cómo variable/función global o local
        """
        for registro in self.símbolos:

            # si es local
            if registro['nombre'] == nombre and \
                    registro['profundidad'] <= self.profundidad:
                return registro

        return -1

    def __str__(self):

        resultado = 'TABLA DE SÍMBOLOS\n\n'
        resultado += 'Profundidad: ' + str(self.profundidad) + '\n\n'
        for registro in self.símbolos:
            resultado += str(registro) + '\n'

        return resultado


class Visitante:
    tabla_símbolos: TablaSímbolos

    REGLAS_VISITAR: dict

    def __init__(self, tabla_símbolos):
        self.tabla_símbolos = tabla_símbolos

        self.REGLAS_VISITAR = {
            TipoNodo.PROGRAMA: self.__visitar_programa,
            TipoNodo.PARAMETROS: self.__visitar_parametros,
            TipoNodo.CONDICIONAL: self.__visitar_condicional,
            TipoNodo.INVOCACION: self.__visitar_invocacion,
            TipoNodo.REPETICION: self.__visitar_repeticion,
            TipoNodo.OPERAR: self.__visitar_operación,
            TipoNodo.ASIGNACION: self.__visitar_asignacion,
            TipoNodo.COMPARACION: self.__visitar_comparacion,
            TipoNodo.EXPRCONDICIONAL: self.__visitar_ExpCondicional,
            TipoNodo.VARIABLE_OPERADOR: self._visitar_operar_variable,
            TipoNodo.OPERADOR: self.__visitar_operador,
            TipoNodo.COMPARADOR_LOGICO: self.__visitar_comparador_logico,
            TipoNodo.INSTRUCCIONES: self.__visitar_bloque_instrucciones,
            TipoNodo.INSTRUCCIÓN: self.__visitar_instruccion,
            TipoNodo.TIPO_VARIABLE: self.__visitar_tipo_variable,
            TipoNodo.TIPO_VALOR: self.__visitar_tipo_valor,
            TipoNodo.NULO: self.__visitar_nulo,
            TipoNodo.RETORNO: self.__visitar_retorno,
            TipoNodo.ROMPE: self.__visitar_rompe,
            TipoNodo.COMPARADOR_MATEMATICO: self.__visitar_comparador_matematico,
            TipoNodo.TEXTO: self.__visitar_texto,
            TipoNodo.IDENTIFICADOR: self.__visitar_identificador,
            TipoNodo.ENTERO: self.__visitar_entero,
            TipoNodo.FLOTANTE: self.__visitar_flotante,
            TipoNodo.FUNCIÓN: self.__visitar_funcion
        }

    def generar_error_identificación(self, nodo_actual):
        """
        Por ahora imprime un error con la linea, y los números de línea y columna

        Por ahora la estrategia escogida fue que terminara inmediatamente el programa
        """

        print()
        print()
        print()
        print(
            "Se ha encontrado un error de identificación en la línea "
            + str(nodo_actual.atributos['numeroLinea']) 
            + ":\n\n" + nodo_actual.atributos['textoLinea'] + "\n\n"
            + "Indetificador no encontrado, porfavor corregir el error respectivo"
        )

        print(self.tabla_símbolos)

        quit()

    def generar_error_inferencia(self, nodo_actual):
        """
        Por ahora imprime un error con la linea, y los números de línea y columna

        Por ahora la estrategia escogida fue que terminara inmediatamente el programa
        """

        print()
        print()
        print()
        print(
            "Se ha encontrado un error de inferencia en la línea "
            + str(nodo_actual.atributos['numeroLinea'])            
            + ":\n\n" + nodo_actual.atributos['textoLinea'] + "\n\n"
            + "Porfavor corregir el error respectivo"
        )

        quit()

    def visitar(self, nodo: TipoNodo):

        if (nodo.tipo in self.REGLAS_VISITAR):
            self.REGLAS_VISITAR[nodo.tipo](nodo)

    def __visitar_programa(self, nodo_actual):
        """
        Programa ::= (Función | Condicional | Asignación | Ciclo | Invocar)+
        """
        for nodo_hijo in nodo_actual.nodos:
            nodo_hijo.visitar(self)

    """
    -------------------------------------------------
    - Bloque de funciones para analizar una función -
    -------------------------------------------------
    """

    def __visitar_funcion(self, nodo_actual):
        """
        Func Identificador {Parametro} -> (Instrucciones)+ <-
        """

        self.tabla_símbolos.nuevo_registro(nodo_actual)
        self.tabla_símbolos.abrir_bloque()
        

        tipo_valor = ""
        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

            if nodo.tipo == TipoNodo.RETORNO:
                tipo_valor = nodo.nodos[0].atributos['tipo']


        self.tabla_símbolos.cerrar_bloque()

        #for nodo in nodo_actual.nodos:
         #   if nodo.tipo == TipoNodo.RETORNO:
          #      nodo_actual.atributos['tipo'] = nodo.nodos[0].atributos['tipo']
           #     break

        nodo_actual.atributos['tipo'] = tipo_valor

    def __visitar_invocacion(self, nodo_actual):
        """
        Invocar ::= Inv Identificador {Parámetro}
        """
        registro = self.tabla_símbolos.verificar_existencia(nodo_actual.nodos[0].contenido)


        if registro == -1:
            self.generar_error_identificación(nodo_actual)

        if registro['referencia'].tipo != TipoNodo.FUNCIÓN:
            self.generar_error_inferencia(nodo_actual)

        for nodo in nodo_actual.nodos:
            nodo.visitar(self)


        nodo_actual.atributos['tipo'] = registro['referencia'].atributos['tipo']

    def __visitar_parametros(self, nodo_actual):
        """
        Parametros ::= TipoValor Identificador (, TipoValor Identificador)+
        """
        
        tipo_valor = " "
        for nodo in nodo_actual.nodos:

            if nodo.tipo == TipoNodo.IDENTIFICADOR:
                
                self.tabla_símbolos.nuevo_registro(nodo)

                if tipo_valor == 'Entero' or tipo_valor == 'Flotante':
                    nodo.atributos['tipo'] = TipoDatos.NÚMERO
    

                if tipo_valor == 'Texto':
                    nodo.atributos['tipo'] = TipoDatos.TEXTO
                
                continue


            tipo_valor = nodo.contenido

            nodo.visitar(self)

    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una condicional -
    -----------------------------------------------------
    """

    def __visitar_condicional(self, nodo_actual):
        """
        Condicional ::= Si {ExpCondicional} ->  Instrucciones + <-
        """

        self.tabla_símbolos.abrir_bloque()

        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        self.tabla_símbolos.cerrar_bloque()

        nodo_actual.atributos['tipo'] = nodo_actual.nodos[1].atributos['tipo']

    
    def __visitar_ExpCondicional(self, nodo_actual):
        """
        ExpCondicional ::= (Comparación (( ^ | ~^) Comparación)*))
        """
        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        nodo_actual.atributos['tipo'] = TipoDatos.VALOR_VERDAD

    
    def __visitar_comparador_logico(self, nodo_actual):
        nodo_actual.atributos['tipo'] = TipoDatos.NÚMERO

    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una repeticion --
    -----------------------------------------------------
    """

    def __visitar_repeticion(self, nodo_actual):
        """
        Ciclo ::= Rep {Comparación}  -> Instrucciones + <-
        """
        self.tabla_símbolos.abrir_bloque()

        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        # nodo_actual.nodos[0].visitar(self)

        self.tabla_símbolos.cerrar_bloque()

        # Anoto el tipo de retorno (TIPO)
        nodo_actual.atributos['tipo'] = nodo_actual.nodos[1].atributos['tipo']

    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una comparacion -
    -----------------------------------------------------
    """

    def __visitar_comparacion(self, nodo_actual):
        """
        Comparación ::= ((Valor | Operación) Comparador (Valor | Operación)
        """
        for nodo in nodo_actual.nodos:
            if nodo.tipo == TipoNodo.IDENTIFICADOR:
                registro = self.tabla_símbolos.verificar_existencia(nodo.contenido)
                if registro == -1:
                    self.generar_error_identificación(nodo_actual)

            nodo.visitar(self)

        valor_izq = nodo_actual.nodos[0]
        comparador = nodo_actual.nodos[1]
        valor_der = nodo_actual.nodos[2]

        if valor_izq.atributos['tipo'] == valor_der.atributos['tipo']:
            comparador.atributos['tipo'] = valor_izq.atributos['tipo']

            # Una comparación siempre tiene un valor de verdad
            nodo_actual.atributos['tipo'] = TipoDatos.VALOR_VERDAD

        elif valor_izq.atributos['tipo'] == TipoDatos.CUALQUIERA or \
                valor_der.atributos['tipo'] == TipoDatos.CUALQUIERA:

            comparador.atributos['tipo'] = TipoDatos.CUALQUIERA

            # Todavía no estoy seguro.
            nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA

        else:

            self.generar_error_inferencia(nodo_actual)

    def __visitar_comparador_matematico(self, nodo_actual):
        """
        Comparador ::= (<|>|<=|>=|~==|==)
        """
        if nodo_actual.contenido not in ['~==^', '==']:
            nodo_actual.atributos['tipo'] = TipoDatos.NÚMERO

        else:
            nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA

    """
    ---------------------------------------------------------------
    - Bloque de funciones para analizar un bloque de instrucciones -
    ----------------------------------------------------------------
    """

    def __visitar_bloque_instrucciones(self, nodo_actual):
        """
        BloqueInstrucciones ::= -> Instrucciones+ | Rompe <-
        Instrucciones ::= (Ciclo | Condicional | Retorna | Asignación | OperarVariable | Invocar)
        """
        # Visita todas las instrucciones que contiene
        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        nodo_actual.atributos['tipo'] = TipoDatos.NINGUNO

        for nodo in nodo_actual.nodos:
            if nodo.atributos['tipo'] != TipoDatos.NINGUNO:
                nodo_actual.atributos['tipo'] = nodo.atributos['tipo']

    def __visitar_instruccion(self, nodo_actual):
        """
        Instrucciones ::= (Ciclo | Condicional | Retorna | Asignación | OperarVariable | Invocar)
        """
        for nodo in nodo_actual.nodos:
            nodo.visitar(self)
            nodo_actual.atributos['tipo'] = nodo.atributos['tipo']

    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una instruccion -
    -----------------------------------------------------
    """

    def _visitar_operar_variable(self, nodo_actual):
        """
        OperarVariable::= Identificador ( <=> ) (Operación | Valor);

        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo)        
        """

        #Si se va a operar una variable es que ya existe 
        registro = self.tabla_símbolos.verificar_existencia(nodo_actual.nodos[0].contenido)
        if registro == -1:
            self.generar_error_identificación(nodo_actual)

        #self.tabla_símbolos.nuevo_registro(nodo_actual.nodos[0])

        for nodo in nodo_actual.nodos:

            if nodo.tipo == TipoNodo.IDENTIFICADOR:
                registro = self.tabla_símbolos.verificar_existencia(nodo.contenido)

                nodo.atributos['tipo'] = registro['referencia'].atributos['tipo']
                continue

            nodo.visitar(self)  



        """ 
        for nodo in nodo_actual.nodos:    
            if nodo.tipo == TipoNodo.OPERAR:
                for nodo_operar in nodo.nodos:
                    if nodo_operar.tipo != nodo_actual.nodos[0].tipo and \
                        nodo_operar.tipo != TipoNodo.OPERADOR:
                        raise Exception('Esa vara no existe', str(nodo_actual))
        """


        # Si es una función verifico el tipo que retorna para incluirlo en
        # la asignación y si es un literal puedo anotar el tipo (TIPO)

        nodo_actual.atributos['tipo'] = nodo_actual.nodos[1].atributos['tipo']

        nodo_actual.nodos[0].atributos['tipo'] = nodo_actual.nodos[1].atributos['tipo']

        tipo_dato = nodo_actual.nodos[0].atributos['tipo']
        for nodo in nodo_actual.nodos:
            if nodo.tipo != TipoNodo.TIPO_VARIABLE:
                if nodo.atributos['tipo'] != tipo_dato:
                    self.generar_error_inferencia(nodo_actual)        


    def __visitar_asignacion(self, nodo_actual):
        """
        Asignación ::= TipoVariable TipoValor Identificador <=> (Operación | Valor | Invocación);

        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo)
        """
        self.tabla_símbolos.nuevo_registro(nodo_actual.nodos[2])

        for nodo in nodo_actual.nodos:
            if nodo.tipo == TipoNodo.IDENTIFICADOR and nodo != nodo_actual.nodos[2]:
                registro = self.tabla_símbolos.verificar_existencia(nodo.contenido)

                if registro == -1:
                    self.generar_error_identificación(nodo_actual)

                nodo.atributos['tipo'] = registro['referencia'].atributos['tipo']
                continue

            nodo.visitar(self)

        nodo_actual.atributos['tipo'] = nodo_actual.nodos[1].atributos['tipo']

        nodo_actual.nodos[2].atributos['tipo'] = nodo_actual.nodos[1].atributos['tipo']

        tipo_dato = nodo_actual.nodos[1].atributos['tipo']
        for nodo in nodo_actual.nodos:
            if nodo.tipo != TipoNodo.TIPO_VARIABLE:
                if nodo.tipo == TipoNodo.INVOCACION:
                    continue
                if nodo.atributos['tipo'] != tipo_dato:
                    self.generar_error_inferencia(nodo_actual)



    def __visitar_operación(self, nodo_actual):
        """
        Operación ::= Operar Valor  (Operadores Valor)+

        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo)


        Ojo esto soportaría un texto
        """
        for nodo in nodo_actual.nodos:

            # Verifico que exista si es un identificador (IDENTIFICACIÓN)
            if nodo.tipo == TipoNodo.IDENTIFICADOR:
                registro = self.tabla_símbolos.verificar_existencia(nodo.contenido)

                if registro == -1:
                    self.generar_error_identificación(nodo_actual)

                nodo.atributos['tipo'] = registro['referencia'].atributos['tipo']
                continue

            nodo.visitar(self)

        # Anoto el tipo de datos 'NÚMERO' (TIPO)
        nodo_actual.atributos['tipo'] = TipoDatos.NÚMERO

        tipo_dato = TipoDatos.NÚMERO
        for nodo in nodo_actual.nodos:
            if nodo.tipo != TipoNodo.TIPO_VARIABLE:
                if nodo.tipo == TipoNodo.INVOCACION:
                    continue

                if nodo.atributos['tipo'] != tipo_dato:
                    self.generar_error_inferencia(nodo_actual)


    def __visitar_retorno(self, nodo_actual):
        """
        Retorna ::= messirve Valor;

        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo)
        """

        for nodo in nodo_actual.nodos:
            nodo.visitar(self)

        if nodo_actual.nodos == []:
            # Si no retorna un valor no retorna un tipo específico
            nodo_actual.atributos['tipo'] = TipoDatos.NINGUNO

        else:

            for nodo in nodo_actual.nodos:

                nodo.visitar(self)

                if nodo.tipo == TipoNodo.IDENTIFICADOR:
                    # Verifico si valor es un identificador que exista (IDENTIFICACIÓN)
                    registro = self.tabla_símbolos.verificar_existencia(nodo.contenido)
                    if registro == -1:
                        self.generar_error_identificación(nodo_actual)

                    # le doy al sarpe el tipo de retorno del identificador encontrado
                    nodo_actual.atributos['tipo'] = registro['referencia'].atributos['tipo']

                else:
                    # Verifico si es un Literal de que tipo es (TIPO)
                    nodo_actual.atributos['tipo'] = nodo.atributos['tipo']

    def __visitar_rompe(self, nodo_actual):
        """
        Rompe ::= siu;

        """
        nodo_actual.atributos['tipo'] = TipoDatos.NINGUNO

    """
    ---------------------------------------------------------------------
    - Bloque de funciones para verificar componentes léxicos o un texto -
    ---------------------------------------------------------------------
    """

    def __visitar_operador(self, nodo_actual):
        """
        Operador ::= ( + | - | ** | * | // | / | % )
        """
        # Operador para trabajar con números (TIPO)
        nodo_actual.atributos['tipo'] = TipoDatos.NÚMERO

    def __visitar_texto(self, nodo_actual):
        """
        Texto ::= ~/\w(\s\w)*)?~
        """
        nodo_actual.atributos['tipo'] = TipoDatos.TEXTO

    def __visitar_entero(self, nodo_actual):
        """
        Entero ::= (-)?\d+
        """
        nodo_actual.atributos['tipo'] = TipoDatos.NÚMERO

    def __visitar_flotante(self, nodo_actual):
        """
        Flotante ::= (-)?\d+.(-)?\d+
        """
        nodo_actual.atributos['tipo'] = TipoDatos.NÚMERO

    def __visitar_identificador(self, nodo_actual):
        """
        Identificador ::= [a-z][a-zA-Z0-9]+
        """
        nodo_actual.atributos['tipo'] = TipoDatos.CUALQUIERA

    def __visitar_tipo_variable(self, nodo_actual):
        """
        TipoVariable ::= (GLOB | CONS | LOC)
        """
        nodo_actual.atributos['tipo'] = TipoDatos.NINGUNO

    def __visitar_tipo_valor(self, nodo_actual):
        """
        TipoValor::= (Texto |  Entero | Flotante)
        """

        if nodo_actual.contenido == 'Entero' or nodo_actual.contenido == 'Flotante':
            nodo_actual.atributos['tipo'] = TipoDatos.NÚMERO
        

        if nodo_actual.contenido == 'Texto':
            nodo_actual.atributos['tipo'] = TipoDatos.TEXTO
        
        

    def __visitar_nulo(self, nodo_actual):
        """
        Nulo ::= Nulo
        """
        nodo_actual.atributos['tipo'] = TipoDatos.NINGUNO



class Verificador:
    asa: ÁrbolSintáxisAbstracta
    visitador: Visitante
    tabla_símbolos: TablaSímbolos

    def __init__(self, nuevo_asa: ÁrbolSintáxisAbstracta):

        self.asa = nuevo_asa

        self.tabla_símbolos = TablaSímbolos()
        self.__cargar_ambiente_estándar()

        self.visitador = Visitante(self.tabla_símbolos)


    def __cargar_ambiente_estándar(self):

        funciones_estandar = [('pinte', TipoDatos.NINGUNO), ('reemplazar', TipoDatos.NINGUNO),
        ('aleatorio', TipoDatos.NÚMERO)]

        for nombre, tipo in  funciones_estandar:
            nodo = NodoÁrbol(TipoNodo.FUNCIÓN, contenido=nombre, atributos= {'tipo': tipo})
            self.tabla_símbolos.nuevo_registro(nodo)


    def imprimir_asa(self):
        """
        Imprime el árbol de sintáxis abstracta
        """

        if self.asa.raiz is None:
            print([])
        else:
            print("\n \n-----------------------------------------------------")
            print("Árbol Decorado")
            print("-----------------------------------------------------")
            self.asa.imprimir_preorden()

    def imprimir_tabla_simbolos(self):
        print(self.tabla_símbolos)

    def verificar(self):
        self.visitador.visitar(self.asa.raiz)

