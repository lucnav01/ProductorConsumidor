# -*- coding: utf-8 -*-
"""
@author: lucianavarromartin

PRODUCTOR CONSUMIDOR 1 (unlimited)

No para nunca.

Cada productor tiene un unico hueco en el almacén.
Tenemos 3 productores y por tanto un almacen de tamaño 3.

"""
from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore
from multiprocessing import current_process
from multiprocessing import Array
import random

import numpy as np

NPROD = 3 #Numero de productores
NCONS = 1 #Numero de consumidores


def productor(pid, almacen, empty, non_empty):
    """
    Cuando el productor produce, añade un elemento a su almacén, entonces se bloquea
    el semaforo empty asociado a este y se desbloquea el non_empty.
    """
    dato = random.randint(0,5)
    while True:
        empty[pid].acquire()
        dato += random.randint(0,5)
        print (f"productor {current_process().name} produciendo")
        almacen[pid] = dato
        print (f"productor {current_process().name} almacenado {dato}")
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
    ordenada = []
    while True:
        dato = np.amin(almacen)
        ordenada.append(dato)
        posicion = almacen[:].index(dato)
        empty[posicion].release()
        print (f"consumidor {current_process().name} consumiendo {dato}")
        non_empty[posicion].acquire()
    print(ordenada)
  
def main():
    #Tenemos un BoundedSemaphore y un Semaphore para cada productor
    empty = [BoundedSemaphore(1) for i in range (NPROD)] 
    non_empty = [Semaphore(0) for i in range (NPROD)]
    almacen = Array('i', NPROD) #almacen vacio
    print("almacen inicial", almacen[:])
    prodlst = [Process(target = productor,
                        name = f'prod_{i}',
                        args = (i, almacen, empty, non_empty))
                for i in range(NPROD)]
    cons = [Process(target = consumidor,
                     name = f'cons',
                     args = (almacen, empty, non_empty))]
    for p in prodlst + cons:
        p.start()
    for p in prodlst + cons:
        p.join()
           
if __name__ == '__main__':
    main()