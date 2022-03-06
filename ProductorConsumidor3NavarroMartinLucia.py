# -*- coding: utf-8 -*-
"""
@author: lucianavarromartin

PRODUCTOR CONSUMIDOR 3(limited)

El almacén ahora tiene espacio infinito, y cada productor tiene k subalmacenes
que pueden estar llenos simultaneamente.

Añadimos el objeto Lock, en este código, para tener un acceso controlado a 
los subalmacenes.

El proceso para cuando cada productor ha repuesto el elemento de sus k almacenes,
N veces, después de haber sido consumido por el consumidor.
"""

from multiprocessing import Process, Manager
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array
from time import sleep
import random

N = 3 # Cantidad de productos que puede fabricar cada productor 
K = 2 # Cantidad de subalmacenes
NPROD = 3 #Número de productores

def add_data(almacen, pid, data, mutex):
    mutex.acquire()
    try:
        almacen.append(pid*1000 + data)
        sleep(1)
    finally:
        mutex.release()

def productor(almacen, pid, empty, non_empty, mutex):
    """
    Cuando el productor produce, añade un elemento a su almacén, entonces se 
    bloquea el semaforo empty asociado a este y se desbloquea el non_empty.
    """
    dato = random.randint(0,5)
    for n in range(N):
        empty[pid].acquire()
        dato += random.randint(0,5)
        add_data(almacen, pid, dato, mutex)
        print (f"productor {current_process().name} almacenado {dato}")
        non_empty[pid].release()   
    print(f"producer {current_process().name} Ha terminado de producir") 
    empty[pid].acquire()
    sleep(1)
    non_empty[pid].release()
    
def consumidor(almacen, empty, non_empty, mutex):
    """
    Cuando el consumidor consume un elemento de uno de los productores este 
    elemento ya no está en el almacén entonces se bloquea el semaforo non_empty
    asociado a este productor y se desbloquea el empty.
    """  
    for s in non_empty:
        s.acquire()
    sleep(1)
    ordenados = []
    while len(ordenados) < NPROD * N:
        numeros = []
        lista_posicion = []
        for i in range(len(almacen)):
            if almacen[i] >= 0:
                numeros.append(almacen[i] % 1000)
                lista_posicion.append(almacen[i]//1000)
        if numeros == []:
            break
        dato = min(numeros)
        posicion = lista_posicion[numeros.index(dato)]
        posicion_almacen = almacen[:].index(dato + posicion * 1000) 
        almacen[posicion_almacen]= -2
        ordenados.append(dato)
        empty[posicion].release()
        print (f"consumidor {current_process().name} consumiendo {dato}")
        non_empty[posicion].acquire() 
    print(ordenados)

def main():
    manager = Manager()
    almacen = manager.list()
    non_empty = [Semaphore(0) for i in range (NPROD)]
    empty = [BoundedSemaphore(K) for _ in range (NPROD)]
    mutex = Lock()
    prodlst = [Process(target=productor,
                        name=f'prod_{i}',
                        args=(almacen, i, empty, non_empty, mutex))
                for i in range(NPROD)]
    cons = [ Process(target=consumidor,
                      name=f'cons',
                      args=(almacen, empty, non_empty, mutex))]
    for p in prodlst + cons:
        p.start()
        
    for p in prodlst + cons:
        p.join()
        
if __name__ == '__main__':
    main()