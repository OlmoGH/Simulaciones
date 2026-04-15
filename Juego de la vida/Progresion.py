#Vamos a recorrer toda la matriz comprobando si los valores al rededor de cada punto 
#satisfacen las reglas

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import copy

#Defino las reglas que dictan la vida de una célúla del lattice:
#   -Si está viva y está rodeada de 2 o 3 células vivas vive (True)
#   -Si está muerta y está rodeada de 4 células vivas vive (True)
#   -En cualquier otro caso muere (False)

def rules(matrix,x,y):
    ind = 0
    for a in (x-1,x,x+1):
        for b in (y-1,y,y+1):
            ind += matrix[a][b]#Para cada célula suma el valor de las adyacentes y ella misma
    if ind == 3:
        return True
    elif matrix[x][y] == 1 and ind == 4:
       return True
    else:
        return False

#Cargamos la matriz que será nuetro lattice desde el archivo lattice.txt y lo ocnvertimos a enteros
matriz = np.loadtxt('lattice.txt', delimiter='\t')
matriz = matriz.astype(int)

#Decidimos cuantos pasos queremos dar y en cada paso creamos una nueva matriz dadas las reglas 
#donde comprobamos si las células viven o mueren
pasos = 1500

#El vector "estados" contiene todos los estados por los que pasa el sistema
estados = [copy.deepcopy(matriz) for k in range(pasos+1)]

#Extraemos la dimensión de la matriz para trabajar con ella
(n,m) = matriz.shape 

#Para el estado i+1 y la célula (a,b) tenemos en cuenta 
#si la célula (a,b) del estado i debe vivir o morir
for i in range(pasos):
    for a in range(1,n-1):
        for b in range(1,m-1):
            if rules(estados[i],a,b):
                estados[i+1][a][b] = 1
            else:
                estados[i+1][a][b] = 0

#Generamos la figura y el área donde se va a ver la imagen
fig, ax = plt.subplots()

#Mostramos la primera imagen, estados[0] como una cuadrícula blanca y negra
im = ax.imshow(estados[0], cmap='gray', vmin=0, vmax=1)

#Definimos la función que actualiza la imagen en cada frame
def update(frame, estados):
    im.set_data(estados[frame])  # Cambia la imagen
    return im,

#Creamos la animación con un intervalo del 20 ms entre frames
animation = FuncAnimation(fig, update, frames=len(estados), fargs=(estados,), interval=20, blit=True)

#Borramos los ejes para que no se vean en la pantalla
plt.axis("off")

#Guardamos la animación como un archivo .mp4 con el nombre "Juego de la vda.mp4"
animation.save("{}.mp4".format("Juego de la vida"), dpi=150)