#Explorador del Lenguaje LosBetesRa!
from enum import Enum, auto
import re


class TipoComponente(Enum):
    """
       Establecer los enums para poder expresar de una mejor manera
       los tipos de componentes.

       La clase de "Explorador" se encargará principalmente de un
       principal próposito la cual es la de validación
       """

    COMENTARIO = auto()
    PALABRA_CLAVE = auto()
    CONDICIONAL = auto()
    INVOCACION = auto()
    REPETICION = auto()
    OPERAR = auto()
    ASIGNACION = auto()
    IMPLICACION = auto() #Se añade
    LECTURA = auto() #Se añade
    OPERADOR = auto()
    COMPARADOR_LOGICO = auto() #Se añade
    TIPO_VARIABLE = auto()
    TIPO_VALOR = auto()
    NULO = auto()
    COMPARADOR_MATEMATICO = auto()
    TEXTO = auto()
    IDENTIFICADOR = auto()
    ENTERO = auto()
    FLOTANTE = auto()       
    PUNTUACION = auto()
    BLANCOS = auto()
    NINGUNO = auto()


class  ComponenteLéxico:
    """
       Esta clase se encargará de almacenar la información sobre el componente léxico
    """

    tipo: TipoComponente
    texto: str
    linea: int
    columna: int
    texto_linea: str

    """
       El siguiente fragmento de código será el constructor el cual establecerá el nuevo componente léxico
    """

    def __init__(self, tipo: TipoComponente, texto: str, linea: int, columna: int, texto_linea: str):
        self.tipo = tipo
        self.texto = texto
        self.linea = linea
        self.columna = columna
        self.texto_linea = texto_linea

    """
       Se procede a representar en texto la determinada instancia actual la cual
       se usa un string de formato python
    """

    def __str__(self):
        componente = f'Tipo: {self.tipo.name:32} Componente: {self.texto:32}Fila y Columma: ({self.linea}, {self.columna})'
        return componente


"""
Esta clase se encarga del proceso principal de exploración y deja debidamente 
procesados los componentes léxicos.
En cuanto respecta al descriptor que tenga un especifico componente tendrá presente estos dos elementos:
               - El tipo de componente
               - Un string de regex que describe los textos que son generados para
                 ese componente
"""

class Explorador:
    descriptores_componentes = [(TipoComponente.COMENTARIO, r'^#C.*'),
                                (TipoComponente.PALABRA_CLAVE, r'^(messirve|siu|Func)'),
                                (TipoComponente.CONDICIONAL, r'^(Si)'),
                                (TipoComponente.INVOCACION, r'^(Inv)'),
                                (TipoComponente.REPETICION, r'^(Rep)'),
                                (TipoComponente.OPERAR, r'^(Operar)'),
                                (TipoComponente.ASIGNACION, r'^(<=>)'),
                                (TipoComponente.IMPLICACION, r'^(->|<-)'),
                                (TipoComponente.LECTURA, r'^(\[|\])'),
                                (TipoComponente.FLOTANTE, r'^(-?([0-9]*[.])[0-9]+)'),
                                (TipoComponente.ENTERO, r'^(-?[0-9]+)'),
                                (TipoComponente.OPERADOR, r'^(\+|-|\*\*|\*|//|/|%)'),
                                (TipoComponente.COMPARADOR_LOGICO, r'^(~\^|\^)'),
                                (TipoComponente.TIPO_VARIABLE, r'^(GLOB|LOC|CONS)'),
                                (TipoComponente.TIPO_VALOR, r'^(Entero|Flotante|Texto)'),
                                (TipoComponente.NULO, r'^(Nulo)'),
                                (TipoComponente.COMPARADOR_MATEMATICO, r'^(>=|<=|<|>|~==|==)'),
                                (TipoComponente.TEXTO, r'^("[^"]*)"'),
                                (TipoComponente.IDENTIFICADOR, r'^([a-zA-Z][_a-zA-Z0-9]*)'),
                                (TipoComponente.PUNTUACION, r'^([,{};])'),
                                (TipoComponente.BLANCOS, r'^(\s)+')]

    def __init__(self, contenido_archivo):
        self.texto = contenido_archivo
        self.componentes = []
        self.bandera_error = 0

    """
       Esta función se encarga de iterar sobre cada una de las líneas
       y adicionalmente se va procesando a la hora que se van generando
       los componentes léxicos que puedan ocupar. 
    """

    def explorar(self):

        numeroLinea = 1

        for linea in self.texto:
            resultado = self.procesar_linea(linea, numeroLinea)
            self.componentes += resultado
            numeroLinea += 1

    """
       Imprime en pantalla en formato amigable al usuario los componentes
       léxicos creados a partir del archivo de entrada
       """

    def imprimir_componentes(self):
        for componente in self.componentes:
            print(componente)

    """
       Toma cada línea y la procesa extrayendo los componentes léxicos.

       En cuanto respecta al manejo de errores, se establece un contador
       de columnas y el numero de linea, para que pueda contemplar errores
       de una manera más especifica
    """

    def procesar_linea(self, linea, numeroLinea):

        linea_componente = '' + linea
        componentes = []
        columna = 1

        # Toma una línea y le va cortando pedazos hasta que se acaba
        while (linea != ""):

            # Separa los descriptores de componente en dos variables
            for tipo_componente, regex in self.descriptores_componentes:

                # Trata de hacer match con el descriptor actual

                respuesta = re.match(regex, linea)

                # Si hay coincidencia se procede a generar el componente
                # léxico final
                if respuesta is not None:

                    # Si la coincidencia corresponde a un BLANCO o un
                    # COMENTARIO se ignora por que no se ocupa
                    if tipo_componente is not TipoComponente.BLANCOS and tipo_componente is not TipoComponente.COMENTARIO:
                        # Crea el componente léxico y lo guarda
                        nuevo_componente = ComponenteLéxico(tipo_componente, respuesta.group(), numeroLinea, columna, linea_componente)
                        componentes.append(nuevo_componente)


                    #Se suma al contador de columna el tamaño del componente para saber donnde comienza
                    columna += len(respuesta.group())

                    # Se elimina el pedazo que hizo match
                    componenteLargo = respuesta.end()
                    linea = linea[componenteLargo:]
                    break
                
                #Si llego aipoComponente.BLANCO y no encontro match es que lo que le entro no existe en la gramática
                elif tipo_componente == TipoComponente.BLANCOS:
                    
                    #Aqui se obtiene la parte del error
                    error = linea.split()[0][0]
                    print("\n")
                    print('Se encuentra un error en la línea '+ str(numeroLinea) + ' y columna '+ str(columna))
                    
                    #Posibles Errores Léxicoss
                    if error == "=":
                        print(linea,"  Declarador", error, "inválido, quizás quisiste decir <=> o consulta la gramática: https://docs.google.com/document/d/1zfCf5laMNBOTx2u_WjK7rViz64cS0OzM18J6sljjseo/edit?usp=sharing")

                    elif error == "(" or error == ")":
                        print(linea,"  Carácter", error, "inválido, quizás quisite decir { o } o consulta la gramática: https://docs.google.com/document/d/1zfCf5laMNBOTx2u_WjK7rViz64cS0OzM18J6sljjseo/edit?usp=sharing")

                    elif error == "!":
                        print(linea,"  Comparador", error, "inválido, quizás quisiste decir ~== o consulta la gramática: https://docs.google.com/document/d/1zfCf5laMNBOTx2u_WjK7rViz64cS0OzM18J6sljjseo/edit?usp=sharing")

                    elif error == "&":
                        print(linea,"  Comparador lógico", error, "inválido, quizás quisiste decir ^ o consulta la gramática: https://docs.google.com/document/d/1zfCf5laMNBOTx2u_WjK7rViz64cS0OzM18J6sljjseo/edit?usp=sharing")

                    elif error == "|":
                        print(linea,"  Comparador lógico", error, "inválido, quizás quisiste decir ~^ o consulta la gramática: https://docs.google.com/document/d/1zfCf5laMNBOTx2u_WjK7rViz64cS0OzM18J6sljjseo/edit?usp=sharing")
                    
                    elif error == "." and componentes.pop().__dict__['texto'].isnumeric():
                        print(linea,"  Error en flotante")
                    else:
                        print(linea,"  Carácter", error, "inválido por favor eliminar el mismo")
                        

                    print("\u2191 \n")
                    print("Se procede a retornar los componenetes válidos a partir de la siguiente línea: ")

                    if self.bandera_error == 0:
                        self.bandera_error = -1

                    return ""

        return componentes
