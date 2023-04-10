from explorador.Explorador import Explorador
from analizador.Analizador_ASA import Analizador
from verificador.Verificador import Verificador
from generador.Generador import Generador


import argparse

"""
Manejo de parámetros para ejecutar de una manera sencilla el explorador y posibles etapas del proyecto 
con ayuda de la libreria argparse.
"""
parser = argparse.ArgumentParser(description='Interprete para Los Betes Ra! (el lenguaje)')

parser.add_argument('--solo-explorar', dest='explorador', action='store_true',
        help='ejecuta solo el explorador y retorna una lista de componentes léxicos')

parser.add_argument('--solo-analizar', dest='analizador', action='store_true', 
        help='ejecuta hasta el analizador y retorna un preorden del árbol sintáctico')

parser.add_argument('--solo-verificar', dest='verificador', action='store_true', 
        help='''ejecuta hasta el verificador y retorna un preorden del árbol
        sintáctico y estructuras de apoyo generadas en la verificación''')

parser.add_argument('--generar-python', dest='python', action='store_true', 
        help='''Genera código python''')

parser.add_argument('archivo',
        help='Archivo de código fuente')


def losbetesra():

    """
    Con el manejo de los parámetros descrito anteriormente se procede a establecer la ejecución 
    del explorador, primeramente se carga el archivo, para luego el texto del archivo sea
    ejecutado por el explorador y al final imprimir sus componentes léxicos
    """
    args = parser.parse_args()

    if args.explorador is True:
        texto = cargar_archivo(args.archivo)
        exp = Explorador(texto)
        exp.explorar()
        exp.imprimir_componentes()

    elif args.analizador is True:

        texto = cargar_archivo(args.archivo)

        exp = Explorador(texto)
        exp.explorar()
        
        if exp.bandera_error == -1:
            exp.imprimir_componentes()
            quit()


        analizador = Analizador(exp.componentes)
        analizador.analizar()
        analizador.imprimir_asa()

    elif args.verificador is True: 

        texto = cargar_archivo(args.archivo)

        exp = Explorador(texto)
        exp.explorar()
        
        analizador = Analizador(exp.componentes)
        analizador.analizar()
        analizador.imprimir_asa()

        verificador = Verificador(analizador.asa)
        verificador.verificar()
        verificador.imprimir_asa()
        verificador.imprimir_tabla_simbolos()

    elif args.python is True:

        texto = cargar_archivo(args.archivo)

        exp = Explorador(texto)
        exp.explorar()
        
        analizador = Analizador(exp.componentes)
        analizador.analizar()

        verificador = Verificador(analizador.asa)
        verificador.verificar()

        generador = Generador(verificador.asa)
        generador.generar()




    else:
        parser.print_help()


def cargar_archivo(ruta_archivo):
    """
    Carga un archivo y lo retorna cómo un solo string pero línea por línea
    en caso de que el archivo exista
    """

    with open(ruta_archivo) as archivo:
        for linea in archivo:
            yield linea.strip("\n")

if __name__ == '__main__':
    losbetesra()
    
