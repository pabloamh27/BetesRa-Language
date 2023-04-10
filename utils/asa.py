# Clases para el manejo de un árbol de sintáxis abstracta
import copy
from enum import Enum, auto


class TipoNodo(Enum):
    """
    Describe el tipo de nodo del árbol
    """
    PROGRAMA = auto()  # Se añade
    PARAMETROS = auto()  # Se añade
    COMENTARIO = auto()
    PALABRA_CLAVE = auto()
    CONDICIONAL = auto()
    INVOCACION = auto()
    REPETICION = auto()
    OPERAR = auto()
    ASIGNACION = auto()
    IMPLICACION = auto()  # Se añade
    LECTURA = auto()  # Se añade
    COMPARACION = auto()  # Se añade
    EXPRCONDICIONAL = auto()  # Se añade
    VARIABLE_OPERADOR = auto()  # Se añade
    OPERADOR = auto()
    COMPARADOR_LOGICO = auto()  # Se añade
    INSTRUCCIÓN = auto()  # Se añade
    INSTRUCCIONES = auto()  # Se añade
    TIPO_VARIABLE = auto()
    TIPO_VALOR = auto()
    NULO = auto()
    RETORNO = auto()  # Se añade
    ROMPE = auto()  # Se añade
    COMPARADOR_MATEMATICO = auto()
    TEXTO = auto()
    IDENTIFICADOR = auto()
    ENTERO = auto()
    FLOTANTE = auto()
    PUNTUACION = auto()
    BLANCOS = auto()
    NINGUNO = auto()
    FUNCIÓN = auto()



class NodoÁrbol:
    tipo: TipoNodo
    contenido: str
    atributos: dict

    def __init__(self, tipo, contenido = None, nodos = [], atributos = {}):

        self.tipo = tipo
        self.contenido = contenido
        self.nodos = nodos
        self.atributos = copy.deepcopy(atributos)


    def __str__(self):

        # Coloca la información del nodo
        resultado = 'Tipo: {:30}\t'.format(self.tipo)

        if self.contenido is not None:
            resultado += 'Contenido: {:10}\t'.format(self.contenido)
        else:
            resultado += 'Contenido: {:10}\t'.format('')

        if self.atributos != {}:
            resultado += 'Atributos: {:38}'.format(str(self.atributos))
        else:
            resultado += 'Atributos: {:38}\t'.format('')

        if self.nodos != []:
            resultado += 'Nodos: <'

            # Imprime los tipos de los nodos del nivel siguiente
            for nodo in self.nodos[:-1]:
                if nodo is not None:
                    resultado += '{}, '.format(nodo.tipo)

            resultado += '{}'.format(self.nodos[-1].tipo)
            resultado += '>'

        return resultado

    def visitar(self, visitador):
        return visitador.visitar(self)


class ÁrbolSintáxisAbstracta:
    raiz: NodoÁrbol

    def imprimir_preorden(self):
        self.__preorden(self.raiz)

    def __preorden(self, nodo):

        print(nodo)
        

        if nodo is not None:
            for nodo in nodo.nodos:
                self.__preorden(nodo)
