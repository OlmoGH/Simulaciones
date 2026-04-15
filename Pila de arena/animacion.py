import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.optimize import curve_fit

# datos_avalanchas = np.loadtxt("Distribucion.txt")
# x = np.log10(datos_avalanchas[1:, 0])
# y = np.log10(datos_avalanchas[1:, 1])
# print(x)
# def lin_function(x, a, b):
#     return a * x + b
# popt, pcov = curve_fit(f=lin_function, xdata=x, ydata=y)
# plt.scatter(x, y, color='r', s=2)
# y_pred = lin_function(x, *popt)
# plt.plot(x, y_pred)
# # plt.xscale('log')
# # plt.yscale('log')
# plt.show()


estados = np.loadtxt("Estados.txt", dtype=int, delimiter='\t')
N = np.size(estados[0])
estados = estados.reshape((-1, N, N))
skip = 5

fig, ax = plt.subplots()
tablero = ax.imshow(np.empty((N, N)), cmap='viridis', vmin=0, vmax=4)
fig.colorbar(tablero)
ax.set_title("Altura de la sal")

def update(frame):
    frame_real = frame * skip
    tablero.set_data(estados[frame_real])
    return tablero,

animacion = FuncAnimation(fig, func=update, frames=np.size(estados, 0) // skip, blit=True, interval=10)
plt.show()