import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from numba import njit, prange

@njit(parallel=True)
def evolve(grid, survive_rules, born_rules):
    size = grid.shape[0]
    next_grid = np.zeros_like(grid)
    for i in prange(size):
        for j in range(size):
            neighboors = grid[(i + 1) % size, j] + grid[i, (j + 1) % size] + grid[(i - 1 + size) % size, j] + grid[i, (j - 1 + size) % size] + grid[(i + 1) % size, (j + 1) % size] + grid[(i - 1 + size) % size, (j - 1 + size) % size] + grid[(i - 1 + size) % size, (j + 1) % size] + grid[(i + 1) % size, (j - 1 + size) % size]
            if (grid[i, j] == 0 and born_rules[neighboors]) or (grid[i, j] == 1 and survive_rules[neighboors]):
                next_grid[i,j] = 1
            else:
                next_grid[i,j] = 0
    
    return next_grid

    

L = 200
survive_rules = np.zeros(9, dtype=np.bool_)
survive_rules[[1, 2, 5, 6]] = True

born_rules = np.zeros(9, dtype=np.bool_)
born_rules[[3]] = True

fig, ax = plt.subplots()
grid = np.random.randint(0, 2, (L, L))
image = ax.imshow(grid, cmap='binary')

def update(frame):
    global grid, born_rules, survive_rules
    next_grid = evolve(grid, survive_rules, born_rules)
    grid = next_grid
    image.set_data(grid)

    return image,

animation = FuncAnimation(fig, update, cache_frame_data=False, interval=20)

plt.show()


