#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <fstream>
#include <array>

// Estructura para representar el estado del sistema
struct Estado {
    double theta1 = 0.0;
    double theta2 = 0.0;
    double omega1 = 0.0;
    double omega2 = 0.0;
};

// Estructura ligera para almacenar únicamente las aceleraciones calculadas
struct Aceleracion {
    double alpha1 = 0.0;
    double alpha2 = 0.0;
};

// Parámetros físicos del péndulo doble
struct Parametros {
    double m1 = 1.0;
    double m2 = 1.0;
    double l1 = 1.0;
    double l2 = 1.0;
    double g  = 9.81;
};

// Calcula exclusivamente las aceleraciones angulares dadas las posiciones y velocidades
Aceleracion calcularAceleracion(const Estado& est, const Parametros& p) {
    double dTheta = est.theta1 - est.theta2;
    double M = p.m1 + p.m2;
    double alpha = p.m1 + p.m2 * std::sin(dTheta) * std::sin(dTheta);

    double num1 = -std::sin(dTheta) * (p.m2 * p.l1 * est.omega1 * est.omega1 * std::cos(dTheta) + p.m2 * p.l2 * est.omega2 * est.omega2) 
                  - p.g * (M * std::sin(est.theta1) - p.m2 * std::sin(est.theta2) * std::cos(dTheta));
    double alpha1 = num1 / (p.l1 * alpha);

    double num2 = std::sin(dTheta) * (M * p.l1 * est.omega1 * est.omega1 + p.m2 * p.l2 * est.omega2 * est.omega2 * std::cos(dTheta)) 
                  + p.g * (M * std::sin(est.theta1) * std::cos(dTheta) - M * std::sin(est.theta2));
    double alpha2 = num2 / (p.l2 * alpha);

    return {alpha1, alpha2};
}

// Integrador Simpléctico de 4º Orden (Método de Yoshida / Forest-Ruth)
std::vector<Estado> Yoshida4(const Estado& inicial, const Parametros& p, double dt, size_t pasos) {
    std::vector<Estado> trayectoria(pasos);
    trayectoria[0] = inicial;

    // Constantes mágicas de Yoshida (1990) para orden 4
    const double w1 = 1.3512071919596577718;
    const double w0 = 1.0 - 2.0 * w1;
    
    // Coeficientes de avance fraccionario para la posición (c) y la velocidad (d)
    const std::array<double, 4> c = { w1 / 2.0, (w1 + w0) / 2.0, (w1 + w0) / 2.0, w1 / 2.0 };
    const std::array<double, 3> d = { w1, w0, w1 };

    for (size_t i = 1; i < pasos; i++) {
        Estado actual = trayectoria[i - 1];

        // 3 etapas internas de avance entrelazado posición-velocidad
        for (int step = 0; step < 3; ++step) {
            // 1. Avance parcial de posición
            actual.theta1 += c[step] * dt * actual.omega1;
            actual.theta2 += c[step] * dt * actual.omega2;

            // 2. Evaluación de la fuerza en la nueva posición intermedia
            Aceleracion acel = calcularAceleracion(actual, p);

            // 3. Avance de velocidad utilizando la aceleración recién calculada
            actual.omega1 += d[step] * dt * acel.alpha1;
            actual.omega2 += d[step] * dt * acel.alpha2;
        }

        // Cierre simétrico: último avance de posición con la velocidad final
        actual.theta1 += c[3] * dt * actual.omega1;
        actual.theta2 += c[3] * dt * actual.omega2;

        trayectoria[i] = actual;
    }

    return trayectoria;
}

int main() {
    Parametros p = {1.0, 1.0, 1.0, 1.0, 9.81};
    Estado inicial = {
        45.0 * std::numbers::pi / 180.0, // theta1
        0.0 * std::numbers::pi / 180.0,  // theta2
        5.0,                             // thetaPunto1
        -5.0                              // thetaPunto2
    };

    double tiempo = 10000.0;
    double dt = 0.01;
    size_t pasos = static_cast<size_t>(tiempo / dt);

    std::cout << "Iniciando simulación simpléctica (Yoshida 4º Orden) con " << pasos << " pasos...\n";
    std::vector<Estado> sim = Yoshida4(inicial, p, dt, pasos);
    std::cout << "Simulación finalizada. Guardando datos...\n";

    std::ofstream archivo("Variables.txt");
    if (!archivo.is_open()) {
        std::cerr << "Error al abrir el archivo de salida.\n";
        return 1;
    }

    archivo << "theta1,theta2,thetaPunto1,thetaPunto2\n";
    for (const auto& est : sim) {
        archivo << est.theta1 << "," << est.theta2 << "," 
                << est.omega1 << "," << est.omega2 << '\n';
    }

    archivo.close();
    std::cout << "Datos guardados exitosamente en 'Variables.txt'.\n";

    return 0;
}