# include <iostream>
# include <array>
# include <random>
# include <vector>
# include <fstream>
# include <iomanip>
# include <map>

using namespace std;

template<const size_t N>
using Matrix = array<array<int, N>, N>;

template<const size_t TAM>
void escribir(ofstream& archivo, Matrix<TAM> lattice)
{
    for (size_t i = 0; i < TAM; i++)
    {
        for (size_t j = 0; j < TAM - 1; j++)
        {
            archivo << lattice[i][j] << '\t';
        }
        archivo << lattice[i][TAM - 1] << endl;
    }
    archivo << endl;
}

template<const size_t TAM>
void inicializar(Matrix<TAM>& lattice)
{
    for (auto& fila : lattice){
        for (auto& casilla : fila){
            casilla = 0;
        }
    }
}

template<const size_t TAM>
void add_salt(Matrix<TAM>& lattice)
{
    // Calculamos una posición al azar en el tablero
    array<size_t, 2> pos = {
        static_cast<size_t>(rand()) % TAM, 
        static_cast<size_t>(rand()) % TAM
    };
    lattice[pos[0]][pos[1]]++; // Añadimos uno de altura
}

template<const size_t TAM>
void colapso(Matrix<TAM>& lattice, const array<size_t, 2>& posicion)
{
    size_t x = posicion[0];
    size_t y = posicion[1];
    // Añadimos uno de altura a cada una de las casillas alrededor y disminuimos 4 la casilla central
    lattice[x][y] -= 4;
    if (x > 0) lattice[x - 1][y]++;
    if (x < TAM-1) lattice[x + 1][y]++;
    if (y > 0) lattice[x][y - 1]++;
    if (y < TAM-1) lattice[x][y + 1]++;
}

template<const size_t TAM>
size_t avalancha(Matrix<TAM>& lattice, ofstream& archivo)
{
    // Comprobamos si hay alguna posición inestable en el sistema
    bool estable;
    size_t tam_avalancha = 0;

    // Primero añadimos sal
    add_salt(lattice);
    do{
        estable = true;

        // Ahora hacemos un repaso por todas las casillas comprobando cuales tienen altura mayor a 3
        // Y guardamos la posición de las casillas inestables
        vector<array<size_t, 2>> posiciones_inestables;

        for (size_t i = 0; i < TAM; i++)
        {
            for (size_t j = 0; j < TAM; j++)
            {
                if (lattice[i][j] > 3){
                posiciones_inestables.push_back({i, j});
                estable = false; // Hay al menos una casilla inestable
                }
            }
        }

        // Si hay alguna posición inestable recorremos las posiciones en la lista y aplicamos la caída del montón de sal
        if (!estable)
        for (const auto& posiciones : posiciones_inestables)
        {
            // Cada vez que una pila de sal colapsa aumentamos en 1 el tamaño de la avalancha
            colapso(lattice, posiciones);
            tam_avalancha++;
        }
    } while (!estable);
    // Escribimos el estado en un archivo
    // escribir(archivo, lattice);

    return tam_avalancha;
}

int main()
{
    const size_t N = 100; // Número de casillas de ancho y alto
    Matrix<N> lattice; // Declaración de la matriz
    map<size_t, size_t> registro_avalanchas;

    ofstream archivo("Estados.txt");

    inicializar(lattice); // Inicializamos el lattice a altura 0
    for (int grano = 0; grano < 10 * N * N; grano++){
        size_t tam_avalancha;
        tam_avalancha = avalancha(lattice, archivo);
        registro_avalanchas[tam_avalancha]++;
        escribir(archivo, lattice);
    }

    ofstream archivo_distribucion("Distribucion.txt");
    for (const auto& [tamaño, frecuencia] : registro_avalanchas) {
        archivo_distribucion << tamaño << '\t' << frecuencia << '\n';
    }
    return 0;
}