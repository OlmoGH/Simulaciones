import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import copy

#Defino las reglas de movimiento para la hormiga
#   -Si se encuentra en una casilla negra cambia el color de la casilla, gira 90º y avanza una casilla
#   -Si se encuentra en una casilla blanca cambia el color de la casilla, gira -90º y avanza una casilla
#Parámetros:
#   pos: posición de la hormiga en el tablero. [a,b]
#   dir: hacia donde está mirando la hormiga. Arriba [0,1], derecha [1,0], abajo [0,-1], izquierda [-1,0]

def cambiar(tablero, i, max, posicion):
    for k in range(i,max):
        tablero[k+1][posicion[0],posicion[1]]=1-tablero[i][posicion[0],posicion[1]]
    return

def mover(tablero, i, posicion, direccion, dimensiones):
        n, m = dimensiones
        giro = np.array([[0, -1], [1, 0]])

        if tablero[i][posicion[0], posicion[1]] == 0:
            nuevaDireccion = np.dot(direccion, giro)
        else:
            nuevaDireccion = np.dot(direccion, -giro)

        nuevaPosicion = posicion + nuevaDireccion

        if np.abs(nuevaPosicion[0]) > n or np.abs(nuevaPosicion[1]) > m:
            return (posicion, direccion)
        else:
            return (nuevaPosicion.astype(int), nuevaDireccion.astype(int))

#Genero una matriz nxm de 0. n y m deben ser impares para colocar a hormiga en el centro
n = 101
m = 101
base = np.zeros((n, m))
direccion = np.array([0, 1])
posicion = np.array([n//2, m//2])#Coloco a la hormiga en el centro

pasos = 10000
estados = [copy.deepcopy(base) for k in range(pasos + 1)]

for i in range(pasos):
    cambiar(estados, i, pasos, posicion)
    (nuevaPosicion, nuevaDireccion) = mover(estados, i, posicion, direccion, (n, m))
    posicion, direccion = nuevaPosicion, nuevaDireccion

#Generamos la figura y el área donde se va a ver la imagen
fig, ax = plt.subplots()

#Mostramos la primera imagen, estados[0] como una cuadrícula blanca y negra
im = ax.imshow(estados[0], cmap='gray', vmin=0, vmax=1)

#Definimos la función que actualiza la imagen en cada frame
def update(frame, estados):
    im.set_data(estados[frame])  # Cambia la imagen
    return im,

#Creamos la animación con un intervalo del 20 ms entre frames
animation = FuncAnimation(fig, update, frames=len(estados), fargs=(estados,), interval=50, blit=True)

#Borramos los ejes para que no se vean en la pantalla
plt.axis("off")

#Guardamos la animación como un archivo .mp4 con el nombre "Juego de la vda.mp4"
animation.save("{}.mp4".format("Hormiga de Langton"), dpi=150)

