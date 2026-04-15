# include <iostream>
# include <vector>
# include <random>

using namespace std;

// Definimos la clase Seguidor

class Seguidor
{
private:
    int dimension = 2;
    vector<double> posicion;
    vector<double> velocidad;
public:
    Seguidor(vector<double> posicion_, vector<double> velocidad_);
    ~Seguidor();
    void actualizar();
    void set_posicion(double x, double y);
    void set_velocidad(double vx, double vy);
};

Seguidor::

Seguidor::~Seguidor()
{
}

void Seguidor::actualizar()
{
    for (int i = 0; i < dimension; i++)
    {
        posicion[i] += velocidad[i];
    }
    
}

void Seguidor::set_posicion(double x, double y)
{
    posicion[0] = x;
    posicion[1] = y;
}

void Seguidor::set_velocidad(double vx, double vy)
{
    velocidad[0] = vx;
    velocidad[1] = vy;
}


int main()
{
    vector<Seguidor> enjambre(10);
    for (int i = 0; i < 10; i++)
    {
        enjambre[i].set_posicion(1.0 * rand() / RAND_MAX, 1.0 * rand() / RAND_MAX);
    }
    
    return 0;
}