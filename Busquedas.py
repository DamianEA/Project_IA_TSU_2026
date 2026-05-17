import sys # libreria para abrir ventanas del sistema
import random #libreria para poder tener valores aleatorios
import time #libreria para tener un cronometro del tiempo que se tarda en resolver las busquedas.
import math #para hacer operaciones matematicas como raices cuadradas

#Las siguientes librerias son para el uso de nuestra interfaz, la cual fue desarrollada en Qt Designer

from PyQt5 import QtWidgets, uic #Aqui estamos habilitando los componenetes del frontend para su uso en python
from PyQt5.QtWidgets import QTableWidgetItem #Para poder aplicarle cambios desde python a nuestra tabla en la que mostraremos la matriz
from PyQt5.QtGui import QColor #Para permitirnos cambiar colres desde el codigo y que se vea reflejado en el front

#Estos son los costos que manejaremos por terrenos los cuales afectaran a la busqueda A*
COSTOS = {
    "Bosque": 1,
    "Desierto": 3,
    "Montaña": 4,
    "Nieve": 2
}

#Y estos son los colores que representaran cada parte de nuestro terreno
COLORES = {
    "Bosque": QColor("#228B22"),
    "Desierto": QColor("#EDE9AF"),
    "Montaña": QColor("#B9907C"),
    "Nieve": QColor("#EEFFFF"),
    "Obstaculo": QColor("#000000"),
    "Inicio": QColor("#00FF00"),
    "Final": QColor("#FF0000"),
    "Camino": QColor("#96357E")
}

AMBIENTES = list(COSTOS.keys()) #Lista de los costos guardada en "AMBIENTES"

class BusquedaApp(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("Terreneitor.ui", self)  # Carga el archivo del front o ui

        # Conectar botones de la ui para asignarle funciones
        self.btnGenerar.clicked.connect(self.generar_terreno)
        self.btnResolver.clicked.connect(self.resolver)
        self.btnReiniciar.clicked.connect(self.reiniciar)

        # Configuración inicial para el terreno
        self.matriz = []
        self.inicio = None
        self.fin = None

    def generar_terreno(self):
        n = self.spinTamano.value()  # Tamaño total de la matriz
        k = self.spinKernel.value()  # Tamaño del bloque (Kernel)

        # Matriz vacía
        self.matriz = [[None for _ in range(n)] for _ in range(n)]

        # Llenar por bloques según el Kernel
        for i in range(0, n, k):
            for j in range(0, n, k):
                # Elige un terreno para este bloque
                tipo_bloque = random.choice(AMBIENTES)
                
# Llena las celdas del bloque k * k (osea Kernel), aqui utliza kernel y el tamaño de la matriz para designar el tamaño apropiado a las celdas
# En otras palabras, se asegura que los kernels queden de manera correcta y no traten de llenar celdas que no existen
        
        for bi in range(i, min(i + k, n)):
            for bj in range(j, min(j + k, n)):
                self.matriz[bi][bj] = tipo_bloque

        for _ in range(n // 2):
            x, y = random.randint(0, n - 1), random.randint(0, n - 1)
            self.matriz[x][y] = "Obstaculo" #selecciona obstaculos en celdas aleatorias dentro de la matriz

        self.inicio = (random.randint(0, n - 1), random.randint(0, n - 1))
        self.fin = (random.randint(0, n - 1), random.randint(0, n - 1)) #se encargan de generar posiciones (coordenadas) aleatorias en nuestra matriz

        self.tablaTerreno.setRowCount(n)
        self.tablaTerreno.setColumnCount(n) # asigna las columnas y filas de la matriz

        for i in range(n):
            #Aqui ya asignamos inicio y final, lo hacemos aqui para que no se lo coma en la parte de kernel
            
            for j in range(n):
                tipo = self.matriz[i][j]
                
                if (i, j) == self.inicio:
                    tipo_mostrar = "Inicio" # Igual aqui xd
                    self.inicioIndicador.setText(f"El inicio se encuentra en {j+1}, {i+1}") 
                elif (i, j) == self.fin:
                    tipo_mostrar = "Final"
                    self.finalIndicador.setText(f"El final se encuentra en {j+1}, {i+1}")
                else:
                    tipo_mostrar = tipo

                item = QTableWidgetItem(tipo_mostrar)
                
                if tipo_mostrar in COLORES: 
                    item.setBackground(COLORES[tipo_mostrar])
                    if tipo_mostrar == "Obstaculo":
                        item.setForeground(QColor("#FFFFFF"))
                    else:
                        item.setForeground(QColor("#000000"))
                
                self.tablaTerreno.setItem(i, j, item)

    def resolver(self):
        
        algoritmo = self.comboAlgoritmo.currentText() #Agarra el texto del combo box algoritmo que se va a resolver
        inicio_tiempo = time.time() #Aqui iniciamos el timer para ver cuanto tardo resolviendo el algoritmo

        self.reiniciar() #Se reinicia la matriz, en caso de si tiene algun camino ya asignado

        if algoritmo == "Anchura": #Si se resulve con el de anchura o sino con el de A estrella
            camino = self.busqueda_anchura()
        else:
            camino = self.busqueda_a_star()

        fin_tiempo = time.time() #Termina el timer
        duracion = fin_tiempo - inicio_tiempo #Esto se hace para que el tiempo este se represente bien

        if camino: # Checa si las funciones en camino no dieron ningun error
            self.lblResultado.setText(f"Solución encontrada en {duracion:.4f} segundos")
            for (x, y) in camino: # Recorre toda la lista camino
                if (x, y) != self.inicio and (x, y) != self.fin:
                    trazado = self.tablaTerreno.item(x, y) 
                    #En las celdas que recorrio le asigna los parametros del camino
                    trazado.setText("•")
                    trazado.setBackground(COLORES["Camino"])
        else:
            self.lblResultado.setText("No se encontró solución")

    def vecinos(self, nodo): # Esta funcion es la que checa los vecinos, ya que se usa en ambas la anchura y a*
        x, y = nodo #Asigna los dos valores de la celda, osea su poscicion x e y
        movimientos = [(0,1),(0,-1),(1,0),(-1,0)] #Los movimientos que se pueden realizar
        resultado = []
        for dx, dy in movimientos: #Loop para pasar por todos los movimientos
            nx, ny = x+dx, y+dy #Traslacion de un nodo al siguiente
            if 0 <= nx < len(self.matriz) and 0 <= ny < len(self.matriz):  #Si la traslacion fue hecha apropiadamente se continua en el codigo
                if self.matriz[nx][ny] != "Obstaculo":  #pasa si no es obstáculo
                    resultado.append((nx, ny))
        return resultado

    def busqueda_anchura(self):
        from collections import deque
        cola = deque([self.inicio]) #Acceso a la lista asignada a cola
        visitados = {self.inicio: None} # Esto nos indica el inicio y guarda todos los nodos visitados

        while cola:
            actual = cola.popleft() # Esto guarda la celda en la que "esta"
            if actual == self.fin:
                return self.reconstruir_camino(visitados) # Si la celda en la que esta es la final, regresa toda la lista usando reconstruir_camino()
            for vecino in self.vecinos(actual):
                if vecino not in visitados: # checa la lista visitados y si no se ha visitado el vecino lo asigna a la lista visitados
                    visitados[vecino] = actual
                    cola.append(vecino)
                    self.lista.clear()  # Limpia la lista antes de actualizar
                    for nodo in visitados.keys():
                        self.lista.addItem(str(nodo))


        return None

    def busqueda_a_star(self):
        import heapq
        frontera = []
        heapq.heappush(frontera, (0, self.inicio)) 
        # Añade el inicio a la lista de frontera, usamos heappush para manipular la lista facilmente
        visitados = {self.inicio: None} # Se asigna el inicio como vistado
        g = {self.inicio: 0} # El costo de inicio (g) en valor a 0

        while frontera: 
            _, actual = heapq.heappop(frontera) 
            # Utilizamos heapq para extraer el elemento con la prioridad más alta (el valor más pequeño) de la cola 
            if actual == self.fin:
                return self.reconstruir_camino(visitados) # Muestra el camino que se hizo

        for vecino in self.vecinos(actual): # Checa los costos del terreno actual
            costo = COSTOS[self.matriz[vecino[0]][vecino[1]]] if self.matriz[vecino[0]][vecino[1]] in COSTOS else 1
            nuevo_g = g[actual] + costo # Aqui esta el costo mas reciente que se va a evaluar
            if vecino not in g or nuevo_g < g[vecino]: 
                # Si no se ha visitado o cuesta menos el vecino que el costo actual
                
                g[vecino] = nuevo_g # Se le asigna el costo al vecino
                f = nuevo_g + self.heuristica(vecino, self.fin) # Hace la evaluacion heuristica (los costes)
                heapq.heappush(frontera, (f, vecino)) # Añade el costo y vecino a la cola
                visitados[vecino] = actual 
                # Nos movemos al vecino                    self.lista.clear()  # Limpia la lista antes de actualizar
                for nodo in visitados.keys():
                    self.lista.addItem(str(nodo))
        return None

    def heuristica(self, a, b): #Para calcular los costes
        return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

    def reconstruir_camino(self, visitados):
        camino = [] # nota que todas las listas relacionadas a la tabla tienen dos valores correspondientes a X e Y
        actual = self.fin # Empezamos desde el final porque ahi nos quedamos y necesitamos re-recorrer el camino
        while actual is not None:
            camino.append(actual) # Inserta todas las celdas visitadas en una lista
            actual = visitados[actual] 
        camino.reverse() # Se invierte la lista porque empezamos desde el final y regresamos al inicio
        return camino
    
    def reiniciar(self):
        if not self.matriz: 
            return

        n = len(self.matriz)
        for i in range(n):
            for j in range(n):
                
                # Agarra todos los ITEMS (las celdas) de la tabla
                item = self.tablaTerreno.item(i, j)
                if item:
                    # Esto recupera el tipo de terreno original
                    tipo_original = self.matriz[i][j]
                    
                    # Aqui verificamos si es el inicio o fin o terreno normal
                    if (i, j) == self.inicio:
                        item.setText("Inicio")
                        item.setBackground(COLORES["Inicio"])
                    elif (i, j) == self.fin:
                        item.setText("Final")
                        item.setBackground(COLORES["Final"])
                    else:
                        # Restauramos el texto original 
                        item.setText(tipo_original)
                        # Restauramos el color original
                        color = COLORES.get(tipo_original, QColor("#FFFFFF"))
                        item.setBackground(color)
                    
                    if tipo_original == "Obstaculo":
                        item.setForeground(QColor("#FFFFFF"))
                    else:
                        item.setForeground(QColor("#000000"))

        self.lblResultado.setText("Mapa restablecido")

#Mostramos la ventana
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventana = BusquedaApp()
    ventana.show()
    sys.exit(app.exec_())