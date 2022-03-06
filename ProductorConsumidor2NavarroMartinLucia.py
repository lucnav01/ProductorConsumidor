# -*- coding: utf-8 -*-
"""
@author: lucianavarromartin

PRODUCTOR CONSUMIDOR 2 (limited)

Cada productor tiene un unico hueco en el almacén, pero puede reponer una 
vez un elemento consumido por el consumidor, así cada productor produce sólo 
dos veces.
Cuando ya ha producido estas dos veces, rellenamos el hueco del almacen asociado
a este productor con un -1, señalizando así que el almacen del productor está vacío.

El consumidor consume el mínimo valor de los elementos producidos por cada productor.

Creamos una variable auxiliar running, de tamaño el número de productores,
que es una lista de booleanos para usarla como condición de parada. 
Empieza inicializada en True para todos los productores, ya que están produciendo,
y cuando ya han producido dos veces, se cambia por un False.

Tenemos 3 productores y por tanto un almacen de tamaño 3.

"""
from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore
from multiprocessing import current_process
from multiprocessing import Array
import random


N = 2  #Cantidad de numeros que se pueden producir
NPROD = 3 #Número de productores
NCONS = 1 #Número de consumidores

def productor(pid, almacen, empty, non_empty):
    """
    Cuando el productor produce, añade un elemento a su almacén, entonces se 
    bloquea el semaforo empty asociado a este y se desbloquea el non_empty.
    """
    dato = random.randint(1,5)
    for n in range(N):
        empty[pid].acquire()
        dato += random.randint(1,5)
        print (f"productor {current_process().name} produciendo")
        almacen[pid] = dato
        print (f"productor {current_process().name} almacenado {dato}")
        non_empty[pid].release()
    print(f"producer {current_process().name} Ha terminado de producir") 
    empty[pid].acquire()
    almacen[pid] = -1
    non_empty[pid].release()

    
def consumidor(almacen, empty, non_empty):
    """
    Cuando el consumidor consume un elemento de uno de los productores este 
    elemento ya no está en el almacén entonces se bloquea el semaforo non_empty
    asociado a este productor y se desbloquea el empty.
    """    
    for s in non_empty:
        s.acquire()
        print (f"consumidor {current_process().name} desalmacenando")
    running = [True for _ in range (NPROD)]
    ordenada = []
    while True in running:
        numeros = []
        for i in range(NPROD):
            running[i] = almacen[i]>=0
            if running[i]:
                numeros.append(almacen[i])
        if numeros == []:
            break
        dato = min(numeros)
        ordenada.append(dato)
        posicion = almacen[:].index(dato)
        empty[posicion].release()
        print (f"consumidor {current_process().name} consumiendo {dato}")
        non_empty[posicion].acquire()   
    print(ordenada)
                
def main():
    empty = [BoundedSemaphore(1) for i in range (NPROD)] 
    non_empty = [Semaphore(0) for i in range (NPROD)]
    almacen = Array('i', NPROD) #almacen vacio
    prodlst = [ Process(target = productor,
                        name = f'prod_{i}',
                        args = (i, almacen, empty, non_empty))
                for i in range(NPROD) ]

    cons = [ Process(target = consumidor,
                     name = f'cons',
                     args = (almacen, empty, non_empty))]
    
    for p in prodlst + cons:
        p.start()

    for p in prodlst + cons:
        p.join()   
    
if __name__ == '__main__':
    main()