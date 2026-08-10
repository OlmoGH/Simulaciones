import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import gaussian_filter
from matplotlib.widgets import Slider
from tqdm import tqdm

def mostrar_corte(pos, z_target):
# pos tiene dimensiones (nrays, steps, 3)
    z = pos[:, :, 2]
    
    # 1. Filtramos los rayos que realmente logran cruzar z_target
    mask = (z[:, 0] <= z_target) & (z[:, -1] >= z_target)
    rayos_validos = np.where(mask)[0]
    
    if len(rayos_validos) == 0:
        return np.array([]), np.array([])
        
    z_validos = z[mask]
    
    # 2. Como z siempre crece, buscamos el primer índice donde supera z_target.
    # argmax sobre un array booleano devuelve rapidísimo el índice del primer True.
    idx_z1 = np.argmax(z_validos > z_target, axis=1)
    idx_z0 = idx_z1 - 1 # El paso justo anterior al cruce
    
    # 3. Extraemos las coordenadas usando indexación avanzada
    # np.arange(len(rayos_validos)) selecciona cada rayo individualmente
    rayos_idx = np.arange(len(rayos_validos))
    
    z0 = z_validos[rayos_idx, idx_z0]
    z1 = z_validos[rayos_idx, idx_z1]
    
    fraccion = (z_target - z0) / (z1 - z0)
    
    x_validos = pos[mask, :, 0]
    y_validos = pos[mask, :, 1]
    
    x0 = x_validos[rayos_idx, idx_z0]
    x1 = x_validos[rayos_idx, idx_z1]
    
    y0 = y_validos[rayos_idx, idx_z0]
    y1 = y_validos[rayos_idx, idx_z1]
    
    x_target = x0 + fraccion * (x1 - x0)
    y_target = y0 + fraccion * (y1 - y0)
    
    return x_target, y_target


rng = np.random.default_rng()
noise_L = 100
dt = 0.001
steps = int(1.0 / dt)
# nrays debe ser un cuadrado perfecto
nrays = int(np.sqrt(100000))**2

# Pre-alocación de memoria
pos = np.zeros((nrays, steps, 3))
p = np.zeros((nrays, steps, 3))

# 1. GENERACIÓN DEL MEDIO
# Medio ruidoso
raw_noise = rng.normal(0, 1, (noise_L, noise_L, noise_L))
smooth_noise = gaussian_filter(raw_noise, sigma=4)
refraction_indices = 1.0 + (smooth_noise / np.std(smooth_noise)) * 0.1

# # Medio no ruidoso
# w = 10
# refraction_indices = 1.0 + 0.1 * np.outer(np.sin(w * np.linspace(0, 2 * np.pi, noise_L)), np.cos(np.pi * w * np.linspace(0, 2 * np.pi, noise_L)))

x = np.linspace(0, 1, noise_L)
y = np.linspace(0, 1, noise_L)
z = np.linspace(0, 1, noise_L)

# 2. INTERPOLADORES
n = RegularGridInterpolator((x, y, z), refraction_indices, method='linear', bounds_error=False, fill_value=1.0)
dn_dx, dn_dy, dn_dz = np.gradient(refraction_indices, 1 / noise_L, 1 / noise_L, 1 / noise_L)

interp_dn_dx = RegularGridInterpolator((x, y, z), dn_dx, method='linear', bounds_error=False, fill_value=0.0)
interp_dn_dy = RegularGridInterpolator((x, y, z), dn_dy, method='linear', bounds_error=False, fill_value=0.0)
interp_dn_dz = RegularGridInterpolator((x, y, z), dn_dz, method='linear', bounds_error=False, fill_value=0.0)

# Condiciones iniciales lineales
pos_0 = np.zeros((nrays, 3))

x_axis = np.linspace(0, 1, int(np.sqrt(nrays)))
y_axis = np.linspace(0, 1, int(np.sqrt(nrays)))

x_0, y_0 = np.meshgrid(x_axis, y_axis)

pos_0[:, 0] = x_0.ravel()
pos_0[:, 1] = y_0.ravel()
pos_0[:, 2] = 0.0

p_0 = np.zeros((nrays, 3))
n_iniciales = n(pos_0) # Una sola llamada al interpolador
p_0[:, 0] = 0.0 * n_iniciales
p_0[:, 1] = 0.0 * n_iniciales
p_0[:, 2] = 1.0 * n_iniciales

pos[:, 0] = pos_0
p[:, 0] = p_0

# 4. BUCLE DE INTEGRACIÓN
for t in tqdm(range(1, steps)):
    # Guardamos el estado anterior en una variable local para no re-evaluar el array
    pos_prev = pos[:, t-1] 
    p_prev = p[:, t-1]
    
    pos[:, t] = pos_prev + dt * p_prev
    
    # Extraemos todos los valores a la vez
    n_vals = n(pos_prev)
    dn_dx_vals = interp_dn_dx(pos_prev)
    dn_dy_vals = interp_dn_dy(pos_prev)
    dn_dz_vals = interp_dn_dz(pos_prev)
    
    p[:, t, 0] = p_prev[:, 0] + dt * n_vals * dn_dx_vals
    p[:, t, 1] = p_prev[:, 1] + dt * n_vals * dn_dy_vals
    p[:, t, 2] = p_prev[:, 2] + dt * n_vals * dn_dz_vals

# Para cada uno de los rayos generamos una interpolación


# 5. Visualizamos las caústicas para cada altura
fig, ax = plt.subplots(figsize=(10, 8))

fig.subplots_adjust(left=0.25, bottom=0.25)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_title(f"Caústicas de ({nrays} rayos)")
axSlider = fig.add_axes([0.25, 0.1, 0.65, 0.03])

z_init = 0.5
x, y = mostrar_corte(pos, z_init)

# Usamos scatter en lugar de plot. Genera un PathCollection muy eficiente.
# s=1 hace que el punto sea pequeño, ideal para 100,000 rayos.
# edgecolors='none' evita el renderizado de bordes, acelerando el proceso.
scatter = ax.scatter(x, y, s=1, c='blue', alpha=0.2, edgecolors='none')

z_slider = Slider(
    ax=axSlider,
    label='z',
    valmin=0.01, # Evitar justo el 0
    valmax=0.99, # Evitar justo el 1
    valinit=z_init,
)

def update(val):
    x_new, y_new = mostrar_corte(pos, z_slider.val)
    if len(x_new) > 0:
        # set_offsets necesita un array de Nx2
        scatter.set_offsets(np.column_stack((x_new, y_new)))
    fig.canvas.draw_idle()

z_slider.on_changed(update)

plt.show()