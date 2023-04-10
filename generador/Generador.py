from operator import le
from re import L
from utils.asa import ÁrbolSintáxisAbstracta, NodoÁrbol, TipoNodo

class VisitanteDePython:

    tabuladores: int 
    REGLAS_VISITAR: dict

    def __init__(self):

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

        self.tabuladores = 0

    def visitar(self, nodo :TipoNodo):


        resultado = ''

        if (nodo.tipo in self.REGLAS_VISITAR):
            resultado = self.REGLAS_VISITAR[nodo.tipo](nodo)


        return resultado

    def __visitar_programa(self, nodo_actual):
        """
        Programa ::= (Función | Condicional | Asignación | Ciclo | Invocar)+
        """

        instrucciones = []
        # Se ignoran los comentarios

        for nodo in nodo_actual.nodos:
            instrucciones.append(nodo.visitar(self))

        return '\n'.join(instrucciones) 

    """
    -------------------------------------------------
    - Bloque de funciones para analizar una función -
    -------------------------------------------------
    """

    def __visitar_funcion(self, nodo_actual):
        """
        Func Identificador {Parametro} -> (Instrucciones)+ <-
        """

        resultado = """\ndef {}({}):\n{}""" 

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        if len(instrucciones) == 2:
            return resultado.format(instrucciones[0], "", '\n'.join(instrucciones[1]))

        return resultado.format(instrucciones[0], instrucciones[1], '\n'.join(instrucciones[2]))

    def __visitar_invocacion(self, nodo_actual):


        """
        Invocar ::= Inv Identificador {Parámetro}
        """

        resultado = """{}({})"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]


        if len(instrucciones) == 1:
            return resultado.format(instrucciones[0], "")
            
        return resultado.format(instrucciones[0], instrucciones[1])

    def __visitar_parametros(self, nodo_actual):
        """
        Parametros ::= TipoValor Identificador (, TipoValor Identificador)+
        """
        
        parámetros = []

        for nodo in nodo_actual.nodos:
            resultado_visita = nodo.visitar(self)

            if resultado_visita != " ":
                parámetros.append(resultado_visita)

        if len(parámetros) > 0:
            return ','.join(parámetros)

        else:
            return ''

    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una condicional -
    -----------------------------------------------------
    """

    def __visitar_condicional(self, nodo_actual):
        """
        Condicional ::= Si {ExpCondicional} ->  Instrucciones + <-
        """

        resultado = """if {}:\n{}"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones.append(nodo.visitar(self))

        return resultado.format(instrucciones[0],'\n'.join(instrucciones[1]))

    
    def __visitar_ExpCondicional(self, nodo_actual):
        """
        ExpCondicional ::= (Comparación (( ^ | ~^) Comparación)*))
        """
        resultado = """{} {} {}"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        if len(instrucciones) == 1:
            return resultado.format(instrucciones[0],'', '')
        else:
            return resultado.format(instrucciones[0],instrucciones[1],instrucciones[2])

    
    def __visitar_comparador_logico(self, nodo_actual):
        if nodo_actual.contenido == "^":
            return "and"
        
        elif nodo_actual.contenido == "~^":
            return "or" 


    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una repeticion --
    -----------------------------------------------------
    """

    def __visitar_repeticion(self, nodo_actual):
        """
        Ciclo ::= Rep {Comparación}  -> Instrucciones + <-
        """
        resultado = """while {}:\n{}"""

        instrucciones = []

        # Visita la condición
        for nodo in nodo_actual.nodos:
            instrucciones.append(nodo.visitar(self))

        return resultado.format(instrucciones[0],'\n'.join(instrucciones[1]))

    """
    -----------------------------------------------------
    - Bloque de funciones para analizar una comparacion -
    -----------------------------------------------------
    """

    def __visitar_comparacion(self, nodo_actual):
        """
        Comparación ::= ((Valor | Operación) Comparador (Valor | Operación)
        """
        resultado = '{} {} {}'

        elementos = []

        # Si los 'Valor' son identificadores se asegura que existan (IDENTIFICACIÓN)
        for nodo in nodo_actual.nodos:
            elementos.append(nodo.visitar(self))

        return resultado.format(elementos[0], elementos[1], elementos[2])   


    def __visitar_comparador_matematico(self, nodo_actual):
        """
        Comparador ::= (<|>|<=|>=|~==|==)
        """

        if nodo_actual.contenido == '~==':
            return '!='

        return nodo_actual.contenido

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
        self.tabuladores += 2

        instrucciones = []

        # Visita todas las instrucciones que contiene
        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        instrucciones_tabuladas = []

        for instruccion in instrucciones:
            instrucciones_tabuladas += [self.__retornar_tabuladores() + instruccion]
            

        self.tabuladores -= 2

        return instrucciones_tabuladas

    def __visitar_instruccion(self, nodo_actual):
        """
        Instrucciones ::= (Ciclo | Condicional | Retorna | Asignación | OperarVariable | Invocar)
        """

        valor = ""

        for nodo in nodo_actual.nodos:
            valor = nodo.visitar(self)

        return valor


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

        resultado = """{} = {}"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones.append(nodo.visitar(self))

        return resultado.format(instrucciones[0],instrucciones[1])     


    def __visitar_asignacion(self, nodo_actual):
        
        
        ####
        """
        Asignación ::= TipoVariable TipoValor Identificador <=> (Operación | Valor | Invocación);

        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo)
        """
        resultado = """{} = {}"""

        instrucciones = []

        for nodo in nodo_actual.nodos:
            resultado_visita = nodo.visitar(self)

            if resultado_visita != " ":
                instrucciones.append(resultado_visita)
        


        return resultado.format(instrucciones[0],instrucciones[1])


    def __visitar_operación(self, nodo_actual):
        """
        Operación ::= Operar Valor  (Operadores Valor)+

        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo)


        Ojo esto soportaría un texto
        """
        instrucciones = []

        for nodo in nodo_actual.nodos:
            instrucciones += [nodo.visitar(self)]

        return ' '.join(instrucciones) 

    def __visitar_retorno(self, nodo_actual):
        """
        Retorna ::= messirve Valor;

        Valor ::= (Identificador | Literal)
        Literal ::= (Texto | Entero | Flotante | Lectura | Nulo)
        """

        resultado = 'return {}'
        valor = ''

        for nodo in nodo_actual.nodos:
            valor = nodo.visitar(self)

        return resultado.format(valor)

    def __visitar_rompe(self, nodo_actual):
        """
        Rompe ::= siu;

        """
        return "break"

    """
    ---------------------------------------------------------------------
    - Bloque de funciones para verificar componentes léxicos o un texto -
    ---------------------------------------------------------------------
    """

    def __visitar_operador(self, nodo_actual):
        """
        Operador ::= ( + | - | ** | * | // | / | % )
        """
       
        return nodo_actual.contenido

    def __visitar_texto(self, nodo_actual):
        """
        Texto ::= ~/\w(\s\w)*)?~
        """
        return nodo_actual.contenido

    def __visitar_entero(self, nodo_actual):
        """
        Entero ::= (-)?\d+
        """
        return nodo_actual.contenido

    def __visitar_flotante(self, nodo_actual):
        """
        Flotante ::= (-)?\d+.(-)?\d+
        """
        return nodo_actual.contenido


    def __visitar_identificador(self, nodo_actual):
        """
        Identificador ::= [a-z][a-zA-Z0-9]+
        """
        return nodo_actual.contenido


    def __visitar_tipo_variable(self, nodo_actual):
        """
        TipoVariable ::= (GLOB | CONS | LOC)
        """
        return " "

    def __visitar_tipo_valor(self, nodo_actual):
        """
        TipoValor::= (Texto |  Entero | Flotante)
        """

        return " "
        

    def __visitar_nulo(self, nodo_actual):
        """
        Nulo ::= Nulo
        """
        return None

    def __retornar_tabuladores(self):
        return " " * self.tabuladores


class Generador:

    asa            : ÁrbolSintáxisAbstracta
    visitador      : VisitanteDePython

    ambiente_estandar = """import sys
import random

def pinte(texto):
    print(texto)

def reemplazar(string, posicion, cambio):
    print(string[:posicion] + cambio + string[posicion+1:])

#Para la carrera de caracoles
def aleatorio():
    return random.randint(1, 3)



"""

    def __init__(self, nuevo_asa: ÁrbolSintáxisAbstracta):

        self.asa            = nuevo_asa
        self.visitador      = VisitanteDePython() 

    def imprimir_asa(self):
        """
        Imprime el árbol de sintáxis abstracta
        """
             
        if self.asa.raiz is None:
            print([])
        else:
            self.asa.imprimir_preorden()

    def generar(self):
        resultado = self.visitador.visitar(self.asa.raiz)
        print(self.ambiente_estandar)
        print(resultado)