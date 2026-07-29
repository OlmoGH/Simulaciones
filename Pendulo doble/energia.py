import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. Carga de los datos generados por tu programa en C++
data = pd.read_csv(
    "Pendulo doble/Variables.txt",
    delimiter=",",
    header=0,
    names=["theta1", "theta2", "omega1", "omega2"],
)

# 2. Parámetros físicos (¡Deben coincidir exactamente con los de C++!)
m1, m2 = 1.0, 1.0
l1, l2 = 1.0, 1.0
g = 9.81

# Extraer las variables como arrays de numpy
t1 = data.theta1.values
t2 = data.theta2.values
w1 = data.omega1.values
w2 = data.omega2.values

# 3. Cálculo vectorial de la Energía Cinética (T)
T = (
    0.5 * (m1 + m2) * (l1**2) * (w1**2)
    + 0.5 * m2 * (l2**2) * (w2**2)
    + m2 * l1 * l2 * w1 * w2 * np.cos(t1 - t2)
)

# 4. Cálculo vectorial de la Energía Potencial (V)
V = -(m1 + m2) * g * l1 * np.cos(t1) - m2 * g * l2 * np.cos(t2)

# 5. Energía Mecánica Total (E)
E = T + V

# 6. Cálculo del error relativo de energía respecto al valor inicial
error_relativo = np.abs((E - E[0]) / E[0]) * 100.0
print(f"Error máximo de conservación: {np.max(error_relativo):.6f}%")

# 7. Graficar los resultados
tiempo = np.arange(len(E)) * 0.01  # Asumiendo dt = 0.01s en tu simulación

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Gráfico de intercambio de energía
ax1.plot(tiempo, T, label="Energía Cinética (T)", color="blue", alpha=0.7)
ax1.plot(tiempo, V, label="Energía Potencial (V)", color="green", alpha=0.7)
ax1.plot(
    tiempo, E, label="Energía Total (E)", color="black", lw=2, linestyle="--"
)
ax1.set_ylabel("Energía (Julios)")
ax1.set_title(
    "Dinámica y Conservación de la Energía del Péndulo Doble (Yoshida 4)"
)
ax1.legend(loc="upper right")
ax1.grid(True, linestyle=":", alpha=0.6)
ax1.set_ylim(-1, 1)

# Gráfico del error relativo para comprobar la estabilidad simpléctica
ax2.plot(tiempo, error_relativo, color="red", lw=1)
ax2.set_xlabel("Tiempo (segundos)")
ax2.set_ylabel("Error Relativo (%)")
ax2.set_title(r"Deriva de Energía: $|\frac{E(t) - E_0}{E_0}| \times 100$")
ax2.grid(True, linestyle=":", alpha=0.6)
ax2.set_ylim(-1, 1)
plt.tight_layout()
plt.show()