import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import gaussian_filter
from matplotlib.collections import LineCollection

rng = np.random.default_rng()
noise_L = 1000
dt = 0.001
steps = int(1.0 / dt)
nrays = 10000

# Pre-alocación de memoria
pos = np.zeros((nrays, steps, 2))
p = np.zeros((nrays, steps, 2))

# 1. GENERACIÓN DEL MEDIO
# Medio ruidoso
raw_noise = rng.normal(0, 1, (noise_L, noise_L))
smooth_noise = gaussian_filter(raw_noise, sigma=4)
refraction_indices = 1.0 + (smooth_noise / np.std(smooth_noise)) * 0.1

# # Medio no ruidoso
# w = 10
# refraction_indices = 1.0 + 0.1 * np.outer(np.sin(w * np.linspace(0, 2 * np.pi, noise_L)), np.cos(np.pi * w * np.linspace(0, 2 * np.pi, noise_L)))

x = np.linspace(0, 1, noise_L)
y = np.linspace(0, 1, noise_L)

# 2. INTERPOLADORES
n = RegularGridInterpolator((x, y), refraction_indices, method='linear', bounds_error=False, fill_value=1.0)
dn_dx, dn_dy = np.gradient(refraction_indices, 1 / noise_L, 1 / noise_L)

interp_dn_dx = RegularGridInterpolator((x, y), dn_dx, method='linear', bounds_error=False, fill_value=0.0)
interp_dn_dy = RegularGridInterpolator((x, y), dn_dy, method='linear', bounds_error=False, fill_value=0.0)

# # Condiciones iniciales radiales
# pos_0 = np.zeros((nrays, 2))
# pos_0[:, 0] = 0.5
# pos_0[:, 1] = 0.5

# p_0 = np.zeros((nrays, 2))
# n_iniciales = n(pos_0) # Una sola llamada al interpolador
# p_0[:, 0] = 1.2 * n_iniciales * np.sin(np.linspace(0.0, 2 * np.pi, nrays))
# p_0[:, 1] = 1.2 * n_iniciales * np.cos(np.linspace(0.0, 2 * np.pi, nrays))

# pos[:, 0] = pos_0
# p[:, 0] = p_0

# Condiciones iniciales lineales
pos_0 = np.zeros((nrays, 2))
pos_0[:, 0] = 0.0
# Se distribuyen uniformemente entre y=0.495 y y=0.500
pos_0[:, 1] = np.linspace(0.4999, 0.5, nrays)

p_0 = np.zeros((nrays, 2))
n_iniciales = n(pos_0) # Una sola llamada al interpolador
p_0[:, 0] = 1.0 * n_iniciales
p_0[:, 1] = 0.0 * n_iniciales

pos[:, 0] = pos_0
p[:, 0] = p_0

# 4. BUCLE DE INTEGRACIÓN
for t in range(1, steps):
    # Guardamos el estado anterior en una variable local para no re-evaluar el array
    pos_prev = pos[:, t-1] 
    p_prev = p[:, t-1]
    
    pos[:, t] = pos_prev + dt * p_prev
    
    # Extraemos todos los valores a la vez
    n_vals = n(pos_prev)
    dn_dx_vals = interp_dn_dx(pos_prev)
    dn_dy_vals = interp_dn_dy(pos_prev)
    
    p[:, t, 0] = p_prev[:, 0] + dt * n_vals * dn_dx_vals
    p[:, t, 1] = p_prev[:, 1] + dt * n_vals * dn_dy_vals

# 5. VISUALIZACIÓN OPTIMIZADA (LineCollection)
fig, ax = plt.subplots(figsize=(10, 8))


image = ax.imshow(refraction_indices.T, cmap='pink', extent=[0, 1, 0, 1], origin='lower', alpha=0.2)
plt.colorbar(image, ax=ax, label="Índice de Refracción")

# LineCollection es infinitamente más rápido que hacer un 'for' con plt.plot
lc = LineCollection(pos, colors='blue', alpha=0.01, linewidths=0.5)
ax.add_collection(lc)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_title(f"Flujo Ramificado ({nrays} rayos)")
plt.show()