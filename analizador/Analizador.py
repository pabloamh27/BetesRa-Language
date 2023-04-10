# Analizador de Los Betes Ra!
from explorador.Explorador import TipoComponente, ComponenteLéxico




"""
Clase Analizador
Se encarga de realizar el análsis por descenso recursivo 
"""
class Analizador():
    

    #Información de la estructura que contiene los componente léxicos
    componentes_léxicos : list
    cantidad_componentes : int
    
    #Información del componente léxico actual
    posición_componente_actual : int
    componente_actual : ComponenteLéxico


    #Diccionarios para poder acceder a las funciones para analizar las reglas del programa
    REGLAS_PROGRAMA : dict
    REGLAS_LITERAL : dict



    def __init__(self, lista_componentes):
        self.componentes_léxicos = lista_componentes
        self.cantidad_componentes = len(lista_componentes)
        self.posición_componente_actual = 0
        self.componente_actual = lista_componentes[0]


        self.REGLAS_PROGRAMA = {
            'Func' : self.__analizar_función,
            'Si'   : self.__analizar_condicional,
            'Rep'  : self.__analizar_repetición,
            'Inv'  : self.__analizar_invocación,
            'Operar' : self.__analizar_operación
            }

        self.REGLAS_LITERAL = {
            TipoComponente.TEXTO : self.__verificar_texto,
            TipoComponente.ENTERO : self.__verificar_entero,
            TipoComponente.FLOTANTE : self.__verificar_flotante,
            TipoComponente.NULO : self.__verificar_nulo
            }





    def analizar(self):
        """
        Método principal que inicia el análisis siguiendo el esquema de
        análisis por descenso recursivo
        """

        self.__analizar_programa()
        print("Analizado con éxito")



    def __analizar_programa(self):
        """
        Programa ::= (Función | Condicional | Asignación | Ciclo | Invocar)+
        """

        #Puede ser tanto un Funcion, una Condicional, una Asignación, Ciclo, Invocar o una Asginación
        #Pero no puede ser una operación
        while self.componente_actual.tipo == TipoComponente.TIPO_VARIABLE \
            or self.componente_actual.texto in self.REGLAS_PROGRAMA and \
                self.componente_actual.texto != 'Operar':
            
        
            #Si es un tipo variable es el comienzo de una asingación
            if (self.componente_actual.tipo == TipoComponente.TIPO_VARIABLE):
                self.__analizar_asignación()


            #Si otra de las reglas
            elif (self.componente_actual.texto in self.REGLAS_PROGRAMA):
                self.REGLAS_PROGRAMA[self.componente_actual.texto]()


        if self.posición_componente_actual != len(self.componentes_léxicos) - 1 \
            and self.componente_actual != self.componentes_léxicos.pop():
                self.__generar_error()



        return 





    """
    -------------------------------------------------
    - Bloque de funciones para analizar una función -
    -------------------------------------------------
    """

    def __analizar_función(self):
        """
        Func Identificador {Parametro} -> (Instrucciones)+ <- 
        """
        self.__verificar('Func')
        self.__verificar_identificador()
        self.__verificar('{')

        if self.componente_actual.tipo == TipoComponente.TIPO_VALOR:
            self.__analizar_parámetros()

        self.__verificar('}')

        #Según la gramática el rommpe solo va en un bloque condicional
        self.__analizar_bloque_instrucciones_sin_rompe()

    def __analizar_invocación(self):
        """
        Invocar ::= Inv Identificador {Parámetro}
        """

        self.__verificar('Inv')
        self.__verificar_identificador()
        self.__verificar('{')

        if self.componente_actual.tipo == TipoComponente.TIPO_VALOR:
            self.__analizar_parámetros()

        self.__verificar('}')


    def __analizar_parámetros(self):
        """
        Parametros ::= TipoValor Identificador (, TipoValor Identificador)+
        """
        # Tiene que haber un parámetro
        self.__verificar_tipo_valor()
        self.__verificar_identificador()

        while (self.componente_actual.texto == ','):
            self.__verificar(',')
            self.__verificar_tipo_valor()
            self.__verificar_identificador()





    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una condicional -
    -----------------------------------------------------
    """
    def __analizar_condicional(self):
        """
        Condicional ::= Si {ExpCondicional} ->  Instrucciones + <-
        """
        self.__verificar('Si')
        self.__verificar('{')
        self.__analizar_ExpCondicional()
        self.__verificar('}')
        self.__analizar_bloque_con_rompe()



    def __analizar_ExpCondicional(self):
        """
        ExpCondicional ::= (Comparación (( ^ | ~^) Comparación)*))
        """
        # La primera sección obligatoria la comparación
        self.__analizar_comparación()

        # Esta parte es opcional
        while (self.componente_actual.tipo == TipoComponente.COMPARADOR_LOGICO):
            self.__verificar_comparador_lógico()
            self.__analizar_comparación()



    def __verificar_comparador_lógico(self):
        """
        Comparador ::= (^|~^)
        """
        self.__verificar_tipo_componente(TipoComponente.COMPARADOR_LOGICO)
        



    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una repeticion --
    -----------------------------------------------------
    """
    def __analizar_repetición(self):
        """
        Ciclo ::= Rep {Comparación}  -> Instrucciones + <-
        """
        self.__verificar('Rep')
        self.__verificar('{')
        self.__analizar_comparación()
        self.__verificar('}')

        #La el romper o "break" solo viene en las repeticiones
        self.__analizar_bloque_instrucciones_sin_rompe()







    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una comparacion -
    -----------------------------------------------------
    """
    def __analizar_comparación(self):
        """
        Comparación ::= ((Valor | Operación) Comparador (Valor | Operación)
        """

        #Operación
        if (self.componente_actual.texto == 'Operar'):
            self.REGLAS_PROGRAMA[self.componente_actual.texto]()

        #Valor
        elif (self.componente_actual.tipo in self.REGLAS_LITERAL):
            self.REGLAS_LITERAL[self.componente_actual.tipo]()

        elif (self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):
            self.__verificar_identificador()

        else:
            self.__generar_error()


        self.__verificar_comparador()


        #Operación
        if (self.componente_actual.texto == 'Operar'):
            self.REGLAS_PROGRAMA[self.componente_actual.texto]()

        #Valor
        elif (self.componente_actual.tipo in self.REGLAS_LITERAL):
            self.REGLAS_LITERAL[self.componente_actual.tipo]()

        elif (self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):
            self.__verificar_identificador()

        else:
            self.__generar_error()


    def __verificar_comparador(self):
        """
        Comparador ::= (<|>|<=|>=|~==|==)
        """
        self.__verificar_tipo_componente(TipoComponente.COMPARADOR_MATEMATICO)








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

        #Empieza por  '->'
        self.__verificar('->')


        #Si no es ninguno de las instrucciones es un error
        if (self.componente_actual.texto not in self.REGLAS_PROGRAMA and \
                self.componente_actual.tipo != TipoComponente.TIPO_VARIABLE and \
                    self.componente_actual.texto != 'messirve' and self.componente_actual.tipo != TipoComponente.IDENTIFICADOR):

                    self.__generar_error()

        #Analiza todas las instrucciones
        while (self.componente_actual.texto in self.REGLAS_PROGRAMA or \
                self.componente_actual.tipo == TipoComponente.TIPO_VARIABLE or \
                    self.componente_actual.texto == 'messirve' or self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):
                    
                    if (self.componente_actual.texto in self.REGLAS_PROGRAMA or \
                        self.componente_actual.tipo == TipoComponente.TIPO_VARIABLE or \
                            self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):
                        
                        self.__analizar_instrucción()
                    
                    #Si es retorno termina el bloque en específico
                    elif (self.componente_actual.texto == 'messirve'):
                        self.__analizar_retorno()
                        break

        # Obligatorio
        self.__verificar('<-')



    def __analizar_bloque_con_rompe(self):
        """
        BloqueInstrucciones ::= -> Instrucciones+ | Rompe <-
        Instrucciones ::= (Ciclo | Condicional | Retorna | Asignación | OperarVariable | Invocar)

        Similiar a la anterior, nada más añade el componente para romper un bucle
        """

        self.__verificar('->')

        if (self.componente_actual.texto not in self.REGLAS_PROGRAMA and \
                self.componente_actual.tipo != TipoComponente.TIPO_VARIABLE and \
                    self.componente_actual.texto != 'siu' and self.componente_actual.texto != 'messirve' and\
                        self.componente_actual.tipo != TipoComponente.IDENTIFICADOR):

                    self.__generar_error()

        
        while (self.componente_actual.texto in self.REGLAS_PROGRAMA or \
                self.componente_actual.tipo == TipoComponente.TIPO_VARIABLE or \
                    self.componente_actual.texto == 'siu' or self.componente_actual.texto == 'messirve' or \
                        self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):
                    
                    if (self.componente_actual.texto in self.REGLAS_PROGRAMA or \
                        self.componente_actual.tipo == TipoComponente.TIPO_VARIABLE or \
                            self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):
                        
                        self.__analizar_instrucción()
                        
                    
                    elif (self.componente_actual.texto == 'siu'):
                        self.__analizar_rompe()
                        break

                    elif (self.componente_actual.texto == 'messirve'):
                        self.__analizar_retorno()
                        break
                        

        # Obligatorio
        self.__verificar('<-')



    def __analizar_instrucción(self):
        """
        Instrucciones ::= (Ciclo | Condicional | Retorna | Asignación | OperarVariable | Invocar)
        """

        if (self.componente_actual.texto in self.REGLAS_PROGRAMA):
            self.REGLAS_PROGRAMA[self.componente_actual.texto]()

        elif (self.componente_actual.tipo == TipoComponente.TIPO_VARIABLE):
            self.__analizar_asignación()

        elif (self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):
            self._analizar_operar_variable()


        else:
            self.__generar_error()





    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una instruccion -
    -----------------------------------------------------
    """

    def _analizar_operar_variable(self):
        #Reasignación de variables ya definidas
        """
        OperarVariable::= Identificador ( <=> ) (Operación | Valor);

        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo) 
        """
        
        #Identificador ya existente
        self.__verificar_identificador()

        self.__verificar('<=>')
        
        #Si es una operación
        if (self.componente_actual.texto == 'Operar'):
            self.__analizar_operación()

        #Si es un valor        
        elif (self.componente_actual.tipo in self.REGLAS_LITERAL):
            self.REGLAS_LITERAL[self.componente_actual.tipo]()
        
        #Si es un identificador
        elif (self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):
            self.__verificar_identificador()

        else:
            self.__generar_error()

        #Obligatorio
        self.__verificar(';')
            


    def __analizar_asignación(self):
        """
        Asignación ::= TipoVariable TipoValor Identificador <=> (Operación | Valor | Invocación);
        
        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo) 
        """

        # El identificador en esta posición es obligatorio
        self.__verificar_tipo_variable()

        self.__verificar_tipo_valor()

        self.__verificar_identificador()

        self.__verificar('<=>')


        # Verificar Indentificador
        if (self.componente_actual.tipo == TipoComponente.IDENTIFICADOR):
            self.__verificar_identificador()

        #Verificar Invocación
        elif (self.componente_actual.texto == 'Inv'):
            self.REGLAS_PROGRAMA[self.componente_actual.texto]()
        
        #Verificar Literal
        elif (self.componente_actual.tipo in self.REGLAS_LITERAL):
            self.REGLAS_LITERAL[self.componente_actual.tipo]()


        #Verificar Operación
        elif (self.componente_actual.texto == "Operar"):
            self.__analizar_operación()

        else:
            self.__generar_error()

        self.__verificar(';')


    def __analizar_operación(self):
        """
        Operación ::= Operar Valor  (Operadores Valor)+

        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo) 
        """ 

        #Verifica el componente Operar
        self.__verificar_operación()
        
        #No se puede operar un nulo
        if self.componente_actual.tipo in self.REGLAS_LITERAL \
            and self.componente_actual.texto != 'Nulo':

            self.REGLAS_LITERAL[self.componente_actual.tipo]()

        #Si es un identificador
        elif self.componente_actual.tipo == TipoComponente.IDENTIFICADOR:
            self.__verificar_identificador()

        else:
            self.__generar_error()

        
        self.__verificar_operador()

        if self.componente_actual.tipo in self.REGLAS_LITERAL \
            and self.componente_actual.texto != 'Nulo':

            self.REGLAS_LITERAL[self.componente_actual.tipo]()

        elif self.componente_actual.tipo == TipoComponente.IDENTIFICADOR:
            self.__verificar_identificador()

        else:
            self.__generar_error()


        #Si es mas de una operación
        while (self.componente_actual.texto in ['+', '-', '*', '**', '/', '//', '%']):
            
            
            self.__verificar_operador()


            if self.componente_actual.tipo in self.REGLAS_LITERAL \
                and self.componente_actual.texto != 'Nulo':
                
                self.REGLAS_LITERAL[self.componente_actual.tipo]()

            elif self.componente_actual.tipo == TipoComponente.IDENTIFICADOR:
                self.__verificar_identificador()

            else:
                self.__generar_error()



    def __analizar_retorno(self):
        """
        Retorna ::= messirve Valor;

        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo) 
        """
        self.__verificar('messirve')

        if self.componente_actual.tipo == TipoComponente.IDENTIFICADOR:
            self.__verificar_identificador()

        elif (self.componente_actual.tipo in self.REGLAS_LITERAL):
            self.REGLAS_LITERAL[self.componente_actual.tipo]()

        else:
            self.__generar_error()

        self.__verificar(';')


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
        self.__verificar_tipo_componente(TipoComponente.OPERADOR)


    def __verificar_texto(self):
        """
        Texto ::= ~/\w(\s\w)*)?~
        """
        self.__verificar_tipo_componente(TipoComponente.TEXTO)

    def __verificar_entero(self):
        """
        Entero ::= (-)?\d+
        """
        self.__verificar_tipo_componente(TipoComponente.ENTERO)

    def __verificar_flotante(self):
        """
        Flotante ::= (-)?\d+.(-)?\d+
        """
        self.__verificar_tipo_componente(TipoComponente.FLOTANTE)

    def __verificar_identificador(self):
        """
        Identificador ::= [a-z][a-zA-Z0-9]+
        """
        self.__verificar_tipo_componente(TipoComponente.IDENTIFICADOR)

    def __verificar_tipo_variable(self):
        """
        TipoVariable ::= (GLOB | CONS | LOC)
        """
        self.__verificar_tipo_componente(TipoComponente.TIPO_VARIABLE)

    def __verificar_tipo_valor(self):
        """
        TipoValor::= (Texto |  Entero | Flotante)
        """
        self.__verificar_tipo_componente(TipoComponente.TIPO_VALOR)

    def __verificar_nulo(self):
        """
        Nulo ::= Nulo
        """
        self.__verificar_tipo_componente(TipoComponente.NULO)

    def __verificar_operación(self):
        """
        Operar ::= Operar
        """
        self.__verificar_tipo_componente(TipoComponente.OPERAR)


    def __verificar(self, texto_esperado):
        """
        Verifica si el texto del componente léxico actual corresponde con
        el esperado cómo argumento
        """
        if self.componente_actual.texto != texto_esperado:
            self.__generar_error()

        else:
            print(self.componente_actual.texto) 
            self.__pasar_siguiente_componente()


    def __verificar_tipo_componente(self, tipo_esperado):
        """
        Verifica si el texto del componente léxico actual corresponde con
        el esperado cómo argumento
        """
        if self.componente_actual.tipo is not tipo_esperado:
            self.__generar_error()

        else:
            print(self.componente_actual.texto)
            self.__pasar_siguiente_componente()







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
                + ":\n\n" + self.componente_actual.texto_linea + "\n" + (self.componente_actual.columna - 1) * " " + "\u2191 \n\n"
                + "Porfavor corregir el error respectivo"
            )
        
        quit()
