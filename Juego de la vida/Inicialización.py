#Inicializamos un tablero de n por m casillas con un número aleatorio de valores 0 y 1. 
#Los bordes siempre valen 0
import numpy as np
import random
n = 100
m = 100
matrix = []
for i in range(n):
    row=[]
    for j in range(m):
        if i in {0,n-1} or j in {0,m-1}:
            row.append(0)
        else:
            row.append(random.choice([0,1]))
    matrix.append(row)
#Imprimimos el valor de la matriz
print(matrix)

#Guardamos la matriz como un fichero llamado "lattice.dat"
np.savetxt("lattice.txt", matrix, fmt="%d", delimiter="\t")
print("Matriz exportada exitosamente")