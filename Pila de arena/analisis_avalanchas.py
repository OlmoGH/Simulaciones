import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import powerlaw

def leer_estados_desde_txt(archivo_txt, tam_matriz):
    estados = np.loadtxt(archivo_txt, delimiter='t').reshape((-1, tam_matriz, tam_matriz))
    return estados

def analizar_avalanchas(archivo_avalanchas):
    # Leer tamaños de avalanchas
    tamanos = np.loadtxt(archivo_avalanchas)
    
    # Filtrar avalanchas pequeñas (opcional)
    tamanos = tamanos[tamanos > 0]
    
    # 1. Histograma en escala log-log
    plt.figure(figsize=(12, 6))
    
    # Histograma convencional
    plt.subplot(121)
    counts, bins, _ = plt.hist(tamanos, bins=50, alpha=0.7, color='blue')
    plt.xlabel('Tamaño de avalancha')
    plt.ylabel('Frecuencia')
    plt.title('Distribución de avalanchas')
    
    # Histograma log-log
    plt.subplot(122)
    log_bins = np.logspace(np.log10(bins[1]), np.log10(bins[-1]), 50)
    counts, bins = np.histogram(tamanos, bins=log_bins)
    centers = (bins[:-1] + bins[1:]) / 2
    valid = counts > 0
    
    plt.scatter(centers[valid], counts[valid], color='red')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Tamaño (log)')
    plt.ylabel('Frecuencia (log)')
    plt.title('Escala log-log')
    
    # Ajuste lineal para estimar exponente
    slope, intercept, r_value, _, _ = linregress(
        np.log(centers[valid]), 
        np.log(counts[valid])
    )
    plt.plot(centers[valid], np.exp(intercept) * centers[valid]**slope, 
             'k--', label=f'Pendiente: {slope:.2f}')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('distribucion_avalanchas.png')
    
    # 2. Análisis con paquete powerlaw
    plt.figure()
    fit = powerlaw.Fit(tamanos, discrete=True)
    print(f"Exponente tau: {fit.power_law.alpha:.3f}")
    print(f"x_min: {fit.power_law.xmin}")
    
    # Comparar con otras distribuciones
    fig = fit.plot_ccdf(label='Datos')
    fit.power_law.plot_ccdf(ax=fig, color='r', linestyle='--', label='Ajuste ley de potencias')
    fit.lognormal.plot_ccdf(ax=fig, color='g', linestyle='--', label='Lognormal')
    fit.exponential.plot_ccdf(ax=fig, color='b', linestyle='--', label='Exponencial')
    
    plt.legend()
    plt.title("Distribución complementaria acumulada")
    plt.savefig('ccdf_avalanchas.png')
    
    # Test estadístico
    R, p = fit.distribution_compare('power_law', 'exponential')
    print(f"Comparación con exponencial: R={R}, p={p}")
    
    R, p = fit.distribution_compare('power_law', 'lognormal')
    print(f"Comparación con lognormal: R={R}, p={p}")
    
    return slope, fit.power_law.alpha

def visualizar_estado_txt(archivo_txt, tam_matriz, indice_estado):
    """Visualiza un estado específico desde archivo de texto"""
    estados = leer_estados_desde_txt(archivo_txt, tam_matriz)
    
    if indice_estado >= len(estados):
        print(f"Error: Solo hay {len(estados)} estados, no se puede acceder al índice {indice_estado}")
        return
    
    estado = estados[indice_estado]
    
    plt.figure(figsize=(8, 6))
    plt.imshow(estado, cmap='viridis', interpolation='nearest')
    plt.colorbar(label='Altura de granos')
    
    # Calcular estadísticas
    altura_max = estado.max()
    altura_min = estado.min()
    altura_prom = estado.mean()
    suma_total = estado.sum()
    
    plt.title(f'Estado del sistema (Índice {indice_estado})\n'
              f'Min: {altura_min}, Max: {altura_max}, Prom: {altura_prom:.2f}, Total: {suma_total}')
    plt.savefig(f'estado_{indice_estado}.png')
    plt.close()
    
    # Devolver estadísticas
    return {
        'indice': indice_estado,
        'min': altura_min,
        'max': altura_max,
        'promedio': altura_prom,
        'suma': suma_total
    }

def analizar_estados(archivo_txt, tam_matriz):
    """Analiza todos los estados y calcula estadísticas"""
    estados = leer_estados_desde_txt(archivo_txt, tam_matriz)
    n_estados = len(estados)
    
    # Inicializar arrays para estadísticas
    sumas = np.zeros(n_estados)
    maximos = np.zeros(n_estados)
    minimos = np.zeros(n_estados)
    promedios = np.zeros(n_estados)
    
    # Calcular estadísticas para cada estado
    for i, estado in enumerate(estados):
        sumas[i] = estado.sum()
        maximos[i] = estado.max()
        minimos[i] = estado.min()
        promedios[i] = estado.mean()
    
    # Gráfico de evolución
    plt.figure(figsize=(12, 8))
    
    plt.subplot(221)
    plt.plot(sumas)
    plt.title('Evolución de la suma total de granos')
    plt.xlabel('Índice de estado')
    plt.ylabel('Granos totales')
    
    plt.subplot(222)
    plt.plot(maximos)
    plt.title('Evolución de la altura máxima')
    plt.xlabel('Índice de estado')
    plt.ylabel('Altura máxima')
    
    plt.subplot(223)
    plt.plot(minimos)
    plt.title('Evolución de la altura mínima')
    plt.xlabel('Índice de estado')
    plt.ylabel('Altura mínima')
    
    plt.subplot(224)
    plt.plot(promedios)
    plt.title('Evolución de la altura promedio')
    plt.xlabel('Índice de estado')
    plt.ylabel('Altura promedio')
    
    plt.tight_layout()
    plt.savefig('evolucion_sistema.png')
    
    return {
        'sumas': sumas,
        'maximos': maximos,
        'minimos': minimos,
        'promedios': promedios
    }

# --- Ejecución principal ---
if __name__ == "__main__":
    # Parámetros (ajustar según tu simulación)
    TAM_MATRIZ = 50  # Tamaño de la matriz (NxN)
    ARCHIVO_AVALANCHAS = 'Distribucion.txt'
    ARCHIVO_ESTADOS = 'Estados.txt'
    
    # 1. Analizar distribución de avalanchas
    exponente_bruto, exponente_ajustado = analizar_avalanchas(ARCHIVO_AVALANCHAS)
    print(f"Exponente bruto: {exponente_bruto:.3f}")
    print(f"Exponente ajustado: {exponente_ajustado:.3f}")
    
    # 2. Visualizar algunos estados clave
    for indice in [0, 10, 50, 100]:
        stats = visualizar_estado_txt(ARCHIVO_ESTADOS, TAM_MATRIZ, indice)
        if stats:
            print(f"\nEstado {indice}:")
            print(f"  - Altura mínima: {stats['min']}")
            print(f"  - Altura máxima: {stats['max']}")
            print(f"  - Altura promedio: {stats['promedio']:.2f}")
            print(f"  - Granos totales: {stats['suma']}")
    
    # 3. Analizar evolución de todos los estados
    stats_globales = analizar_estados(ARCHIVO_ESTADOS, TAM_MATRIZ)
    
    # 4. Calcular correlación entre tamaño de avalancha y granos totales
    if len(stats_globales['sumas']) > 1:
        avalanchas = np.loadtxt(ARCHIVO_AVALANCHAS)
        # Asegurar que tenemos suficientes datos
        min_len = min(len(avalanchas), len(stats_globales['sumas']))
        correlacion = np.corrcoef(avalanchas[:min_len], stats_globales['sumas'][:min_len])[0, 1]
        print(f"\nCorrelación entre tamaño de avalancha y granos totales: {correlacion:.3f}")