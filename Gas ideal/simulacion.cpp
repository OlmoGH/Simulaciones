# include <iostream>
# include <array>
# include <random>
# include <cmath>
# include <fstream>

using namespace std;

int main()
{
    // Inicializamos el archivo para guardar los datos de la red
    ofstream archivo;
    archivo.open("Estados.txt");
    if (!archivo.is_open()) {
        cerr << "No se pudo abrir el archivo" << endl;
        return 1;
    }

    // Definimos los parámetros de la simulación
    const size_t N = 100;
    double T = 2;
    double mu = 1;
    int pasos = 100000;

    // Inicializamos la red de espines
    array<array<int, N>, N> lattice;
    for (auto &fila : lattice) {
        for (auto &spin : fila) {
            spin = (rand() % 2) * 2 - 1;
        }
    }
    
    // Escribimos la cabecera del archivo
    for (int i = 0; i < N; i++) {
        archivo << "s" << i << "\t";
    }
    archivo << endl;

    // Guardamos el estado inicial de la red en el archivo
    for (auto &fila : lattice) {
        for (auto &spin : fila) {
            archivo << spin << "\t";
        }
        archivo << endl;
    }

    // Iteramos sobre todos los pasos Markov
    for (int i = 0; i < pasos; i++) {
        // Seleccionamos un spin al azar de la red
        int x = rand() % N;
        int y = rand() % N;

        // Calculamos la energía del spin 
        int suma;
        suma = (
        lattice[x][(y + 1) % N] +
        lattice[x][(y - 1) % N] +
        lattice[(x + 1) % N][y] +
        lattice[(x - 1) % N][y]
        );

        double energia = lattice[x][y] * (2 * suma - mu);
        double probabilidad = exp(- energia / T);

        // Generamos un número al aza entre 0 y 1 y 
        // si la probabilidad es mayor que el número se lleva a cabo el cambio
        double random = (double)rand() / RAND_MAX;
        if (probabilidad > random) {
            lattice[x][y] *= -1;
        }

        // Guardamos el estado de la red en el archivo
        for (auto &fila : lattice) {
            for (auto &spin : fila) {
                archivo << spin << "\t";
            }
            archivo << endl;
        }
    }

    return 0;
}