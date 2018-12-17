# -*- coding: UTF-8 -*-

import struct 
import errno
import socket
from time import sleep
import select
import sys
import random 
from thread import *
import threading 
import sqlite3
from sqlite3 import Error
import os
 
def execute_query(conn, sql_query):
    try:
        c = conn.cursor()
        c.execute(sql_query)
    except Error as e:
        print(e)
 
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        #print(sqlite3.version)
        return conn
    except Error as e:
        print(e)
    #finally:
        #conn.close()
    
    return None
    
def seleccionar_pokemon_aleatorio():
    dbconn = create_connection("pokedex.db")
    cur = dbconn.cursor()
    cur.execute("SELECT * FROM pokemones")
    rows = cur.fetchall()
    dbconn.close()
    #print(rows)
    r = random.randint(0,len(rows)-1)
    #print(r)
    return rows[r]

def obtener_nombre_pokemon(id_pokemon):
    dbconn = create_connection("pokedex.db")
    cur = dbconn.cursor()
    cur.execute("SELECT * FROM pokemones WHERE id=?", (id_pokemon,))
    rows = cur.fetchall()
    dbconn.close()
    return rows[0][1]
    
def obtener_nombre_usuario(id_usuario):
    dbconn = create_connection("pokedex.db")
    cur = dbconn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id=?", (id_usuario,))
    rows = cur.fetchall()
    #print(rows)
    dbconn.close()
    if len(rows) == 0:
        return None
    return rows[0][1]
    
def insertar_captura_pokemon(id_usuario, id_pokemon):
    dbconn = create_connection("pokedex.db")
    cur = dbconn.cursor()
    cur.execute("SELECT * FROM pokemones_capturados WHERE id_usuario=? AND id_pokemon=?",(id_usuario,id_pokemon))
    rows = cur.fetchall()
    if len(rows) == 0:
        cur.execute("INSERT INTO pokemones_capturados (id_usuario,id_pokemon,cantidad) VALUES (?,?,1)",(id_usuario,id_pokemon,))
        dbconn.commit()
    else:
        count = rows[0][2] + 1
        cur.execute("UPDATE pokemones_capturados SET cantidad=? WHERE id_usuario=? AND id_pokemon=?",(count,id_usuario,id_pokemon,))
        dbconn.commit()
    dbconn.close()
    return
    
def obtener_pokemones_capturados(id_usuario):
    dbconn = create_connection("pokedex.db")
    cur = dbconn.cursor()
    cur.execute("SELECT * FROM pokemones_capturados WHERE id_usuario=?", (id_usuario,))
    rows = cur.fetchall()
    dbconn.close()
    pokemones = []
    for row in rows:
        nombre = obtener_nombre_pokemon(row[1])
        pokemones.append(nombre)
    return pokemones

#aqui va implementada la maquina de estados
def procesar_datos(connection,data,vrs):   
    if data[0] == chr(32):
        return chr(32)
    #maneja cuando se pide un pokemon 
    if data[0] == chr(10):
        print("usuario solicitó capturar pokemon")       
        pokemon = seleccionar_pokemon_aleatorio()
        vrs[1] = pokemon[0]
        vrs[3] = pokemon[1]
        return "\x14" + str(pokemon[1])
    ##maneja cuando se dice si se quiere o no capturar el pokemon
    if data[0] == chr(30): 
        vrs[0] -= 1
        ##si se acabaron las pokebolas
        if vrs[0] == 0 :
            #se acabaron las pokebolas 
            return chr(23)
        if (random.randint(1,5) <= 3):
            #no capturado intentar capturar de nuevo
            return chr(21) + chr(vrs[1]) + chr(vrs[0])
        else:
            insertar_captura_pokemon(vrs[2], vrs[1])
            ##enviar imagen
            img_path = "imgs/" + vrs[3] + ".png"
            file = open(img_path,"rb")
            img_size = os.path.getsize(os.getcwd() + "/" + img_path)
            print(img_path)
            print(img_size)
            return chr(22) + chr(vrs[1]) + struct.pack("I",img_size) + file.read()
    if data[0] == chr(11): 
        print("revisando si el id {0} esta en la base de datos".format(ord(data[1])))
        #el codigo 25 es si se encontro al usuario si no se envia el codigo 40 para saber que no encontro al usuario
        #asigna tambien el id del usuario en vrs[2]
        usr_name = obtener_nombre_usuario(ord(data[1]))
        print(usr_name)
        if usr_name != None:
            vrs[2] = ord(data[1])
            return chr(25) + usr_name
        else:
            return chr(41)
    ##aqui deberia manejar la peticion de sus pokemones
    ##pero solo le deberia amandar los ids
    ##supongamos que el usuario tiene 10 pokemones 
    if data[0] == chr(12):
        #deberia cerrar la sesion
        #pokemones_usuario = [1,3,5,2,25,100,105,104,103,101]
        pokemones_usuario = obtener_pokemones_capturados(vrs[2])
        return chr(24) + chr(len(pokemones_usuario)) + ", ".join((map(lambda x : str(x),pokemones_usuario)))
    if data[0] == chr(31):
        return chr(32)
    else:  
        print("codigo incorrecto")
        return chr(40)

def manejar_conexion(connection):
    connection.setblocking(0)
    tiempo = 15
    #el primero es numero de pokebolas, el segundo es el id del pokemon, el tercero es el id del usuario y el ultimo el nombre del pokemon
    vrs = [5,0,0,""]
    while tiempo > 0:
        try:
            #thread_lock.acquire() 
            data = connection.recv(1024)
            #thread_lock.release()
            #si el tamano de los datos es mayor que 0
            if(len(data) != 0):
                ##reiniciar el tiempo 
                tiempo = 15
                print("{0}".format(data))
                resp= procesar_datos(connection,data,
                                     vrs)
                print("quedan {0} pokebolas".format(vrs[0]))
                #el estado -1 es el estado de error
                #y tendria que cerrar el socket 
                if resp == chr(32): 
                    break
                else:
                    thread_lock.acquire()
                    connection.sendall(resp)
                    thread_lock.release()
                    if (resp == chr(40)):
                        break
        except IOError as e:
            #print("IOError:")
            #print(e)
            #si no hay nada sigue revisando en la entrada
            if e.errno == errno.EWOULDBLOCK:
                pass
        sleep(1)
        print("esperando...")
        tiempo -= 1
    if tiempo == 0:
        print("timeout")
        connection.sendall(chr(42))
    print("cerrando socket")
    #thread_lock.release()
    connection.sendall(chr(32))
    connection.close()
    
thread_lock = threading.Lock()
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server_address = ('localhost',9999)
sock.bind(server_address)
sock.listen(1)
while True:
    connection , client_address = sock.accept()
    #thread_lock.acquire() 
    start_new_thread(manejar_conexion, (connection,)) 
    #manejar_conexion(connection)
sock.close()



