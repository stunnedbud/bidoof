# -*- coding: UTF-8 -*-

import struct
import socket
import sys
#from PIL import Image

def procesar_respuesta(respuesta,sock):
        if respuesta[0] == chr(20):
                print("Un {0} salvaje ha aparecido! ".format(respuesta[1:]))
                while(True):
                        dec = raw_input("¿Intentar atraparlo? (\"si\" o \"no\") ")
                        if dec == "si":
                                return '\x1e'
                        elif dec == "no":
                                return '\x1f'
                        else: 
                                print("ERROR: Cadena incorrecta.")
        ##mensaje tipo 21
        if respuesta[0] == chr(21):
                print("No atrapaste al pokemon!")
                print("Tienes {0} intentos restantes. ".format(ord(respuesta[2])))
                while(True):
                        dec = raw_input("¿Volver a intentar? ")
                        if dec == "si":
                                #mensaje 30
                                return chr(30)
                        elif dec == "no":
                                #mensaje 32 
                                return chr(31)
                        else:
                                print("ERROR: Cadena incorrecta.")
                print("¿Quieres intentar de nuevo?")
        if respuesta[0] == chr(23):
                print("Se te acabaron las pokebolas!")
                return chr(32)
        if respuesta[0] == chr(22):
                cantidad_recibida = len(data) - 6
                info_imagen = data[6:]
                tam_imagen = struct.unpack("I",respuesta[2:6])[0]
                file = open("PokemonCapturado.png","wb")
                file.write(info_imagen)
                while(cantidad_recibida < tam_imagen):
                        info_imagen = sock.recv(1024)
                        cantidad_recibida+= len(info_imagen)
                        file.write(info_imagen)
                #img = Image.open('PokemonCapturado.png')
                #img.show() 
                print("¡Lo atrapaste!")
                print("El pokemon se guardó como \"PokemonCapturado.png\"!")
                print("la imagen tiene tamaño " + str(struct.unpack("I",respuesta[2:6])[0]))
        if respuesta[0] == chr(25):
                print("Bienvenido "+str(respuesta[1:])+"!")
                print("¿Que quieres hacer?")
                print("1. Atrapar pokemon.")
                print("2. Ver tus pokemones.")
                print("3. Salir.")
                while(True):
                        resp = int(raw_input("(introduce 1,2 o 3) "))
                        if resp == 1:
                                return chr(10)
                        elif resp == 2:
                                return chr(12)
                        elif resp == 3:
                                return chr(32)
                        else:
                            print("ERROR: No es una opción valida.")
        ##deberia imprimir los pokemones 
        if respuesta[0] == chr(24):
                cantidad_recibida = len(data) - 2
                pks = data[2:]
                #print("Tus pokemones son: {0}".format(map(lambda x : str(x),pks)))
                print("Pokemones capturados: {0}".format(str(pks)))
                ##mandar el codigo de fin de sesion
                return chr(32)
        #else
        #codigos de error
        if respuesta[0] == chr(40):
            print("ERROR: Ocurrió un error no especificado.");
        if respuesta[0] == chr(41):
            print("ERROR: El id de usuario es incorrecto.");
        if respuesta[0] == chr(42):
            print("TIMEOUT: Se agotó el tiempo de espera.");
            return chr(42);
        print("Confirmando fin de sesion.")
        return chr(32); 


sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server_address = ('localhost',9999)
sock.connect(server_address)
#inciando conexion con el codigo 11
#que es el codigo para iniciar la sesion
# el segundo 1 es el id del usuario
id_user = int(raw_input("Introduce tu id de usuario: "))
sock.sendall(chr(11) + chr(id_user))
while(True): 
        data = sock.recv(1024)
        #print(data)
        if len(data) != 0:
                peticion = procesar_respuesta(data,sock)
                if peticion[0] == chr(42): #timeout  
                        break;
                sock.sendall(peticion)
                if peticion[0] == chr(32) or peticion[0] == chr(31):
                        print("Terminando sesion.")
                        break 
print("Cerrando socket.")
sock.close()

