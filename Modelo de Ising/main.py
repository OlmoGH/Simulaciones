import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from numba import njit
from tqdm import tqdm

@njit
def invert_cluster(grid, T):
    L = grid.shape[0]
    seleccionado = np.full((L, L), False)

    # Seleccionamos una posición al azar inicial
    x, y = np.random.randint(low=0, high=L, size=2)
    pila = [(x, y)]

    p_add = 1 - np.exp(-2.0 / T)
    cluster_sign = grid[x, y]
    seleccionado[x, y] = True
    grid[x, y] = -cluster_sign

    while pila:
        cx, cy = pila.pop()

        vecinos = [
            ((cx + 1)%L, cy),
            (cx, (cy + 1)%L),
            ((cx - 1 + L)%L, cy),
            (cx, (cy - 1 + L)%L)
        ]

        for nx, ny in vecinos:
            if not seleccionado[nx, ny]:
                if cluster_sign == grid[nx, ny]:
                    if np.random.random() < p_add:
                        seleccionado[nx, ny] = True
                        pila.append((nx, ny))
                        grid[nx, ny] = -cluster_sign

@njit
def count_clusters(grid):
    L = grid.shape[0]
    seleccionados = np.full((L, L), False)
    cluster_size = 0
    sizes = []

    for i in range(L):
        for j in range(L):
            if not seleccionados[i, j]:
                seleccionados[i, j] = True
                cluster_sign = grid[i, j]
                pila = [(i, j)]
                while pila:
                    ci, cj = pila.pop()
                    cluster_size += 1
                    vecinos = [
                    ((ci + 1)%L, cj),
                    (ci, (cj + 1)%L),
                    ((ci - 1 + L)%L, cj),
                    (ci, (cj - 1 + L)%L)
                    ]

                    for ni, nj in vecinos:
                        if not seleccionados[ni, nj]:
                            if grid[ni, nj] == cluster_sign:
                                seleccionados[ni, nj] = True
                                pila.append((ni, nj))

                sizes.append(cluster_size)
                cluster_size = 0

    return sizes
                            

# Implemetación del algoritmo de Wolff para evolucionar el modelo de Ising

L1 = 100
L2 = 500
L3 = 1000
T = 2.0 / np.log(1.0 + np.sqrt(2.0))
steps_per_frame = 20
grid1 = np.ones((L1, L1))
grid2 = np.ones((L2, L2))
grid3 = np.ones((L3, L3))
all_sizes1 = []
all_sizes2 = []
all_sizes3 = []

# Hacemos un warmup
for t in tqdm(range(100)):
    invert_cluster(grid1, T)
    invert_cluster(grid2, T)
    invert_cluster(grid3, T)

# Cada 10 pasos calculamos el tamaño de los clusteres
for _ in tqdm(range(100)):
    for _ in range(10):
        invert_cluster(grid1, T)
        invert_cluster(grid2, T)
        invert_cluster(grid3, T)

    sizes1 = count_clusters(grid1)
    sizes2 = count_clusters(grid2)
    sizes3 = count_clusters(grid3)
    all_sizes1 += sizes1
    all_sizes2 += sizes2
    all_sizes3 += sizes3

sizes_sorted1 = np.sort(all_sizes1)
sizes_sorted2 = np.sort(all_sizes2)
sizes_sorted3 = np.sort(all_sizes3)
N_clusters1 = len(sizes_sorted1)
N_clusters2 = len(sizes_sorted2)
N_clusters3 = len(sizes_sorted3)
ccdf1 = 1.0 - np.arange(1, N_clusters1 + 1) / N_clusters1
ccdf2 = 1.0 - np.arange(1, N_clusters2 + 1) / N_clusters2
ccdf3 = 1.0 - np.arange(1, N_clusters3 + 1) / N_clusters3

plt.loglog(sizes_sorted1 / (L1 ** 1.948), ccdf1 * (sizes_sorted1 ** 1.027), marker='.', linestyle='none', label=f"L = {L1}")
plt.loglog(sizes_sorted2 / (L2 ** 1.948), ccdf2 * (sizes_sorted2 ** 1.027), marker='.', linestyle='none', label=f"L = {L2}")
plt.loglog(sizes_sorted3 / (L3 ** 1.948), ccdf3 * (sizes_sorted3 ** 1.027), marker='.', linestyle='none', label=f"L = {L3}")

plt.xlabel(r"$S/L^{D_F}$")
plt.ylabel(r"$CCDF \cdot S^{\tau-1}$")
plt.legend()

plt.show()
