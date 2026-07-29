import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation

# 1. Carga de datos
data = pd.read_csv("Pendulo doble/Variables.txt", delimiter=',', header=0, 
                   names=['theta1', 'theta2', 'thetaPunto1', 'thetaPunto2'])

l1 = 1.0
l2 = 1.0

# 2. Submuestreo para la animación (1 de cada 5 pasos -> dt_anim = 0.05s)
# Esto evita que matplotlib se congele procesando un millón de puntos
paso_anim = 5
theta1 = data.theta1.values[::paso_anim]
theta2 = data.theta2.values[::paso_anim] # CORREGIDO: data.theta2

# 3. Cinemática directa (Coordenadas cartesianas)
x1 = l1 * np.sin(theta1)
y1 = -l1 * np.cos(theta1)

x2 = x1 + l2 * np.sin(theta2)
y2 = y1 - l2 * np.cos(theta2) # CORREGIDO: y1 positivo, no -y1

# 4. Configuración del lienzo
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-2.2, 0)
ax.set_aspect('equal') # CRÍTICO: Para que las barras no se deformen al girar
ax.grid(True, linestyle='--', alpha=0.5)
ax.set_title("Simulación de Péndulo Doble (RK4)")

# Elementos gráficos iniciales
Rod1, = ax.plot([], [], color='black', lw=2)
Rod2, = ax.plot([], [], color='black', lw=2)
Mass1 = ax.scatter([], [], s=50, c='blue', zorder=3)
Mass2 = ax.scatter([], [], s=50, c='red', zorder=3)
Traza, = ax.plot([], [], color='red', alpha=0.3, lw=1) # Extra: estela del péndulo 2

def update(frame):
    # Actualización de las barras
    Rod1.set_data([0, x1[frame]], [0, y1[frame]])
    Rod2.set_data([x1[frame], x2[frame]], [y1[frame], y2[frame]])
    
    # Actualización de las masas (usando formato 2D para evitar deprecation warnings)
    Mass1.set_offsets([[x1[frame], y1[frame]]])
    Mass2.set_offsets([[x2[frame], y2[frame]]])
    
    # Dibujar la estela (últimos 50 fotogramas) para ver el caos
    inicio = max(0, frame - 50)
    Traza.set_data(x2[inicio:frame], y2[inicio:frame])

    return Rod1, Rod2, Mass1, Mass2, Traza

# 5. Creación de la animación pasando el número exacto de fotogramas
# interval=30 ms da aproximadamente 33 FPS
animation = FuncAnimation(fig, update, frames=len(x1), blit=True, interval=30)

plt.show()