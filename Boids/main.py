import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider


class Birb:
    def __init__(self, x, y, v, dir, r):
        self.x = x
        self.y = y
        self.v = v
        self.dir = dir
        self.r = r

    def updatePosition(self, boid_list, dt, width, height):
        self.x += self.v * np.cos(self.dir)
        self.x = (self.x + width) % width
        self.y += self.v * np.sin(self.dir)
        self.y = (self.y + height) % height


    def updateDirection(self, boid_list, sigma, width, height):
        mean_cos = 0
        mean_sin = 0
        n_inside = 0

        for birb in boid_list:
            dx = np.abs(self.x - birb.x)
            if dx > width / 2: dx = width - dx
            dy = np.abs(self.y - birb.y)
            if dy > height / 2: dx = height - dy

            if np.sqrt(dx**2 + dy**2) < self.r:
                n_inside += 1
                mean_cos += np.cos(birb.dir)
                mean_sin += np.sin(birb.dir)

        mean_cos = mean_cos / n_inside
        mean_sin = mean_sin / n_inside

        self.dir = (np.atan2(mean_sin, mean_cos) + sigma * np.random.uniform(- np.pi, np.pi)) % (2 * np.pi)

# novio es el mejor del mundo y le amo mucho pipipi

# PARÁMETROS
width = 600
height = 600
v = 10
r = 100
N = 100
dt = 0.0001
noise_init = 0.1
boid_list = [Birb(np.random.uniform(0, width), np.random.uniform(0, height), v, np.random.uniform(-np.pi, np.pi), r) for _ in range(N)]

# VENTANA

fig, [ax, ax_plot] = plt.subplots(ncols=2, figsize=(10, 6))
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
ax_plot.set_xlim(0, 1)
ax_plot.set_xlabel("Intensidad del ruido")
ax_plot.set_ylim(0, v)
ax_plot.set_ylabel(r"$\langle v \rangle$")

flock, = ax.plot([], 'k.', markersize=10)

def update(frame):
    x = [birb.x for birb in boid_list]
    y = [birb.y for birb in boid_list]
    flock.set_data(x, y)
    mean_vx = 0
    mean_vy = 0
    for birb in boid_list:
        birb.updatePosition(boid_list, dt, width, height)
        birb.updateDirection(boid_list, noise_slider.val, width, height)
        mean_vx += v * np.cos(birb.dir)
        mean_vy += v * np.sin(birb.dir)

    mean_v = np.sqrt((mean_vx / N)**2 + (mean_vy / N)**2)
    ax_plot.plot(noise_slider.val, mean_v, 'k.', markersize=10)


    return flock,

animation = FuncAnimation(fig, update, interval=20, cache_frame_data=False)

plt.show()