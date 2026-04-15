import numpy as np
import matplotlib.pyplot as plt

p = 0.5
N = 10000
T = 1000
walkers = np.zeros((T, N))
sigma = np.zeros(T)

for i in range(1, T):
    choice = np.random.random_integers(0, 1, N) * 2 - 1
    walkers[i] = walkers[i-1] + choice
    # sigma[i] = np.std(walkers[i])

plt.plot(walkers, rasterized=True, markersize=1)
# plt.loglog(sigma, 'k')
plt.show()