import numpy as np
from numba import njit
import matplotlib.pyplot as plt

@njit(fastmath=True)
def regresion_lineal_numba(x, y):
    """
    Sustituto ultrarrápido de np.polyfit(x, y, 1)[0] para Numba.
    Calcula solo la pendiente (m) usando mínimos cuadrados.
    """
    n = len(x)
    sum_x = np.sum(x)
    sum_y = np.sum(y)
    sum_xy = np.sum(x * y)
    sum_xx = np.sum(x * x)
    
    denominador = (n * sum_xx - sum_x * sum_x)
    if denominador == 0.0:
        return 0.0 # Evitar división por cero si todos los tiempos fuesen iguales
    
    pendiente = (n * sum_xy - sum_x * sum_y) / denominador
    return pendiente

def interacting_time_series(x_0, sigma, tau, dt, A, steps):
    N_species = x_0.shape[0]
    int_time_series = np.zeros((steps, N_species))
    int_time_series[0] = x_0
    for t in range(1, steps):
        for i in range(N_species):
            interaction_term = 0
            for j in range(N_species):
                interaction_term += A[i, j] * int_time_series[t-1, j]

            x_i = int_time_series[t-1, i]
            drift = x_i / tau * (1 + interaction_term)
            diffusion = x_i * sigma * np.random.standard_normal()
            int_time_series[t, i] = x_i + dt * drift + np.sqrt(dt) * diffusion
    
    return int_time_series

@njit(fastmath=True)
def deterministic_interacting_time_series(x_0, tau, dt, A, steps):
    N_species = x_0.shape[0]
    int_time_series = np.zeros((steps, N_species))
    int_time_series[0] = x_0
    for t in range(1, steps):

        for i in range(N_species):
            interaction_term = 0
            for j in range(N_species):
                interaction_term += A[i, j] * int_time_series[t-1, j]

            int_time_series[t, i] = int_time_series[t-1, i] + dt * int_time_series[t-1, i] / tau * (1 + interaction_term)
    
    return int_time_series

@njit(fastmath=True)
def construir_matriz_ISLM(N, C, sigma, mu_K=0.0, sigma_K=1.0):
    """
    Construye la matriz de interacción A siguiendo el ensamble balanceado
    del artículo de Calvo et al. (2026). Versión optimizada y blindada para Numba.
    """
    # 1. Fuerza que mu_K y sigma_K sean floats para evitar que np.random.lognormal falle
    K = np.random.lognormal(float(mu_K), float(sigma_K), N)
    
    # Pre-asignamos la matriz final A
    A = np.zeros((N, N))
    
    # Desviación estándar para los pesos aleatorios Z
    std_z = 1.0 / np.sqrt(N)
    
    # Pre-asignamos vectores temporales para procesar cada fila eficientemente
    row_B = np.zeros(N)
    row_Z = np.zeros(N)
    
    # Procesamos fila por fila
    for i in range(N):
        # Limpiamos los vectores temporales para la fila actual
        row_B[:] = 0.0
        row_Z[:] = 0.0
        
        suma_z = 0.0
        cuenta = 0
        
        # Pasos 2 y 3: Generamos la conectividad (B) y los pesos (Z) solo para esta fila
        for j in range(N):
            if i != j: # Sin auto-interacciones en la red aleatoria
                if np.random.rand() < C:
                    row_B[j] = 1.0
                    val_z = np.random.normal(0.0, std_z)
                    row_Z[j] = val_z
                    suma_z += val_z
                    cuenta += 1
        
        # Paso 4: Calculamos la media de los enlaces activos de esta fila para balancear
        media = 0.0
        if cuenta > 0:
            media = suma_z / cuenta
            
        # Pasos 5 y Diagonal: Construimos los elementos finales de la fila i de la matriz A
        for j in range(N):
            if i == j:
                A[i, i] = -1.0 / K[i] # Diagonal de control D_ii
            else:
                if row_B[j] == 1.0:
                    G_ij = row_Z[j] - media       # Peso balanceado
                    A[i, j] = sigma * G_ij / K[j] # Escalado final por K_j
                else:
                    A[i, j] = 0.0
                    
    return A, K

@njit(fastmath=True)
def calcular_lyapunov_automatico(tiempo, dist, epsilon=1e-8, d_sat=0.1):
    """
    Versión Numba-friendly, con protección contra explosiones (NaN/Inf).
    """
    # 1. PROTECCIÓN CONTRA EXPLOSIONES
    # Si el sistema diverge a infinito o produce NaNs, lo detectamos rápido
    for i in range(len(dist)):
        if np.isnan(dist[i]) or np.isinf(dist[i]):
            # Si explota, la separación de trayectorias es brutal, el sistema es 
            # inestable/caótico divergente. Devolvemos np.nan para que no rompa 
            # tus gráficas, pero lo salte limpiamente.
            return np.nan 

    d_min = 10.0 * epsilon
    d_max = 0.01 * d_sat
    
    max_dist = np.max(dist)
    
    # CASO 1: SISTEMA CAÓTICO ESTABLE (crece y luego satura)
    if max_dist > d_max:
        # En Numba, en lugar de np.where con múltiples condiciones lógicas (que a 
        # veces falla), es muchísimo más rápido y seguro hacer un bucle para contar:
        cuenta = 0
        for i in range(len(dist)):
            if dist[i] >= d_min and dist[i] <= d_max:
                cuenta += 1
                
        # Si hay suficientes puntos, guardamos en arrays de ese tamaño exacto
        if cuenta > 10:
            t_ajuste = np.zeros(cuenta)
            log_d_ajuste = np.zeros(cuenta)
            idx = 0
            for i in range(len(dist)):
                if dist[i] >= d_min and dist[i] <= d_max:
                    t_ajuste[idx] = tiempo[i]
                    log_d_ajuste[idx] = np.log(dist[i])
                    idx += 1
            
            # Usamos nuestra propia función en lugar de polyfit
            lambda_max = regresion_lineal_numba(t_ajuste, log_d_ajuste)
            return lambda_max

    # CASO 2: SISTEMA ESTABLE O CRÍTICO (No crece lo suficiente)
    n = len(tiempo)
    mitad_idx = n // 2
    
    cuenta_final = n - mitad_idx
    t_final = np.zeros(cuenta_final)
    log_d_final = np.zeros(cuenta_final)
    
    idx = 0
    for i in range(mitad_idx, n):
        t_final[idx] = tiempo[i]
        # Evitamos hacer np.log(0) si por causalidad la distancia es 0 exacto
        if dist[i] > 0:
            log_d_final[idx] = np.log(dist[i])
        else:
            log_d_final[idx] = -100.0 # Valor logarítmico bajo seguro
        idx += 1
        
    lambda_max = regresion_lineal_numba(t_final, log_d_final)
    
    return lambda_max

@njit(fastmath=True)
def sacar_imagen():
    # Listas para guardar los resultados de la transición
    n_medias = 1
    n_sigma = 10
    n_C = 10
    valores_sigma = np.linspace(0, 2, n_sigma)
    valores_conectividad = np.linspace(0, 1, n_C)
    lyapunov_exponents = np.zeros((n_sigma, n_C))

    for i, s in enumerate(valores_sigma):
        for j, C in enumerate(valores_conectividad):
            media = 0
            if ((i * n_sigma + j) * 10) % (n_sigma * n_C) == 0:
                print("Paso ", (i * n_sigma + j), " de ", n_sigma * n_C)

            for muestra in range(n_medias):

                # 1. Construyes la matriz con el sigma actual
                N = 1000

                tau = 1

                dt = 0.01
                steps = int(10/dt)
                time = np.linspace(0, steps * dt, steps)
                transient_steps = int(30/dt)
                epsilon = 1e-8

                A , K = construir_matriz_ISLM(N, C, s, 0, 1)

                # --- CALCULAMOS X TRAS PASAR EL TRANSITORIO
                X_tran = np.ones(N)

                X_post = deterministic_interacting_time_series(X_tran, tau, dt, A, transient_steps)

                X_0 = X_post[-1]
                u = np.random.standard_normal(N)

                X_0_pert = X_0 + epsilon * u / np.linalg.norm(u)

                X = deterministic_interacting_time_series(X_0, tau, dt, A, steps)
                X_pert = deterministic_interacting_time_series(X_0_pert, tau, dt, A, steps)
                
                # 4. Calculas distancia y vector de tiempo
                dist = np.zeros(steps)
                for t in range(steps):
                    dist[t] = np.linalg.norm(X[t] - X_pert[t])
                
                # 5. LLAMADA AUTOMÁTICA
                lambda_mle = calcular_lyapunov_automatico(time, dist)
                media += lambda_mle

            media = media/n_medias

            lyapunov_exponents[i, j] = media

    return lyapunov_exponents


# # regresion_lineal_numba(np.ones(2), np.ones(2))

# print("Antes de la función")
# # lyapunov_exponents = sacar_imagen()
# print("Después de la función")
# # --- GRAFICAR LA TRANSICIÓN DE FASE DE LYAPUNOV ---
# plt.figure()
# img = plt.imshow(lyapunov_exponents.T, cmap='RdBu_r', extent=[0, 1, 2, 0], vmin=-1, vmax=1, aspect='auto')
# plt.colorbar(img)
# plt.ylabel(r"$\sigma$")
# plt.xlabel(r"$C$")
# plt.title("Transición de fase al Caos Dinámico")
# plt.tight_layout()
# plt.savefig("Transición de fase.png")
# plt.savefig("Transición de fase.pdf")
# plt.show()

N = 100
C = 1
s = 2

tau = 1

dt = 0.01
steps = int(30/dt)
time = np.linspace(0, steps * dt, steps)
epsilon = 1e-8

A , K = construir_matriz_ISLM(N, C, s, 0, 1)


X_0 = np.ones(N)

X = deterministic_interacting_time_series(X_0, tau, dt, A, steps)

plt.plot(time, X, c='red', alpha=0.6)
plt.xlabel("Time", fontsize=18)
plt.ylabel("Abundance", fontsize=18)
plt.title(fr"$\sigma = {s}$  $C = {C}$", fontsize=18)
plt.tick_params(axis='both', labelsize=14)
plt.tight_layout()
plt.show()
