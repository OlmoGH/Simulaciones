import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider


class Birb:
    def __init__(self, x, y, v, dir, r, size, charge):
        self.x = x
        self.y = y
        self.v = v
        self.dir = dir
        self.r = r
        self.size = size
        self.charge = charge

    def updatePosition(self, dt, width, height):
        self.x += dt * self.v * np.cos(self.dir)
        self.x = (self.x + width) % width
        self.y += dt * self.v * np.sin(self.dir)
        self.y = (self.y + height) % height


    def updateDirection(self, boid_list, sigma, width, height):
        mean_cos = 0
        mean_sin = 0
        total_apport = 0

        for birb in boid_list:
            dx = np.abs(self.x - birb.x)
            if dx > width / 2: dx = width - dx
            dy = np.abs(self.y - birb.y)
            if dy > height / 2: dx = height - dy

            dist = np.sqrt(dx**2 + dy**2)
            infl = 1 / (1 + (dist / r) ** 10)
            total_apport += birb.size * infl
            mean_cos += infl * self.charge * birb.charge * birb.size * np.cos(birb.dir)
            mean_sin += infl * self.charge * birb.charge * birb.size * np.sin(birb.dir)

        mean_cos = mean_cos / total_apport
        mean_sin = mean_sin / total_apport

        self.dir = (np.atan2(mean_sin, mean_cos) + sigma * np.random.uniform(- np.pi, np.pi)) % (2 * np.pi)

# novio es el mejor del mundo y le amo mucho pipipi

# PARÁMETROS
width = 600
height = 600
v = 1000
r = 50
N = 100
dt = 0.01
noise_init = 0.1
boid_list = [Birb(np.random.uniform(0, width), 
                  np.random.uniform(0, height), 
                  v, 
                  np.random.uniform(-np.pi, np.pi), 
                  r, 
                  1 / np.random.rand()**2, 
                  np.random.choice([-1, 1])) for _ in range(N)]
colors = ['blue' if birb.charge == -1 else 'red' for birb in boid_list]

# VENTANA

fig, ax = plt.subplots(figsize=(10, 6))
fig.subplots_adjust(bottom=0.25)
axnoise = fig.add_axes((0.25, 0.1, 0.65, 0.03))
noise_slider = Slider(
    ax=axnoise,
    label='Noise amplitude',
    valmin=0,
    valmax=1,
    valinit=noise_init,
)
ax.set_xlim(0, width)
ax.set_ylim(0, height)

flock = ax.scatter([birb.x for birb in boid_list], [birb.y for birb in boid_list], [birb.size for birb in boid_list], alpha=0.8, c=colors)

def update(frame):
    coords = [[birb.x, birb.y] for birb in boid_list]
    flock.set_offsets(coords)

    for birb in boid_list:
        birb.updateDirection(boid_list, noise_slider.val, width, height)

    for birb in boid_list:
        birb.updatePosition(dt, width, height)

    return flock,

animation = FuncAnimation(fig, update, interval=20, cache_frame_data=False)

plt.show()