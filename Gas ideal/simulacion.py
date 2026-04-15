import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Definimos los parámetros de la distribución
beta = 10
mu = 1

# Número de frames
secs = 10
fps = 120

# Definimos la red de posiciones
N = 100
lattice = np.random.randint(0, 2, (N, N)) * 2 - 1
print(lattice)

fig, ax = plt.subplots()

red = plt.imshow(lattice, cmap='viridis')

def update(frame):
    # Elegimos la partícula que se va cambiar
    x = np.random.randint(0, N)
    y = np.random.randint(0, N)

    # Calculamos la probabilidad de transición
    suma = (
        lattice[x, (y + 1) % N] +
        lattice[x, (y - 1) % N] +
        lattice[(x + 1) % N, y] +
        lattice[(x - 1) % N, y]
    )
    energia = lattice[x, y] * (2 * suma - mu)
    probabilidad = np.exp(- beta * energia)

    # Aplicamos el cambio de espín con probabilidad p, si p > 1 se realiza el cambio
    random = np.random.rand()
    if probabilidad > random:
        lattice[x, y] *= -1


    red.set_data(lattice)
    return [red]

animacion = FuncAnimation(fig, func=update, frames=secs * fps, blit=True, interval=1000/fps)
print("Animación generada")
animacion.save('test_anim.mp4', fps=fps, extra_args=['-vcodec', 'libx264'])
print("Animacion guardada")