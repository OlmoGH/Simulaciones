import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation

skip = 50

lattice = pd.read_csv("Estados.txt", sep="\t", header=0).dropna(axis=1)
N = lattice.shape[1]
frames = lattice.shape[0] // N

fig, ax = plt.subplots()

red = ax.imshow(lattice[:N], cmap='viridis')
titulo = ax.get_title()

def init():
    red.set_data(np.empty((N, N)))
    return red, 

def update(frame):
    frame = frame * skip
    titulo = (f"Frame {frame}")
    ax.set_title(titulo)
    red.set_data(lattice[frame * N:(frame + 1) * N])
    return red, 

animacion = FuncAnimation(fig=fig, func=update, init_func=init, frames=frames // skip, blit=True, interval=10)
plt.show()