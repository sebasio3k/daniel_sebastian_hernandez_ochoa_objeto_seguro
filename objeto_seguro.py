from ecies.utils import generate_eth_key
from ecies import encrypt, decrypt
import base64
import binascii
from pathlib import Path
import json
import logging
from datetime import datetime
import psycopg2
import socket
import threading

logging.basicConfig(level=logging.DEBUG, format="\n%(asctime)s - %(message)s")


class SocketServer:
    def __init__(self, puerto_emisor):
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_and_ip = ('127.0.0.1', puerto_emisor)
        self.node.bind(port_and_ip)
        self.node.listen(5)
        self.connection, self.addr = self.node.accept()

    def receiver(self):
        msg = ""
        while msg != "exit":
            msg = self.connection.recv(1024).decode()
            print(f'<<< {msg}')


class SocketClient:
    def __init__(self, puerto_destino):
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_and_ip = ('127.0.0.1', puerto_destino)
        self.node.connect(port_and_ip)

    def send_sms(self, sms):
        self.node.send(sms)


# Metodos de utileria
def pide_nombre():
    while True:
        entrada = input('¿Cómo te llamas? ')
        if entrada.isalpha():
            return entrada
        else:
            print("La entrada es incorrecta, escribe un nombre")


# Creación de un objeto seguro, se recibe el nombre en formato String.
class ObjetoSeguro:
    # Constructor
    def __init__(self, nombre_objeto):
        self._nombre = nombre_objeto
        self.__llave_privada, self.__llave_publica = self.__gen_llaves()
        logging.debug(f'Llave publica: {self._nombre}: {type(self.__llave_publica)}, {self.__llave_publica}')
        self.__llave_publica_destinatario = None
        self.__nombre_destinatario = None
        # Pedir puerto de servidor
        self.puerto_e = int(input('¿Cuál será mi puerto? '))
        # Crea tablas en BD
        self.crea_tablas_bd(self.conecta_bd())
        # Almacenar la llave publlica de objeto seguro en BD
        sentencia = 'INSERT INTO persona(nombre_persona, llave_publica, puerto) VALUES(%s, %s, %s)'
        valores = (f'{self._nombre}', f'{self.__llave_publica}', f'{self.puerto_e}')
        self.inserta_bd(sentencia, valores, self.conecta_bd())
        # Pide puerto de desto para cliente:
        self.puerto_d = int(input('¿Cuál será el puerto del destinatario? '))
        # Intercambio de llaves publicas, consulta BD Y guarda registro correspondiente:
        self.intercambio_llave_publica(self.puerto_d)

    @staticmethod
    def conecta_bd():  # Conexion a BD
        conexion = psycopg2.connect(
            user='postgres',
            password='admin2236',
            host='127.0.0.1,',
            port='5432',
            database='mensajes')
        return conexion

    @staticmethod
    def crea_tablas_bd(conexion):  # Crea tablas persona y mensajes en BD
        try:
            with conexion:
                with conexion.cursor() as cursor:
                    sentencia = 'CREATE TABLE IF NOT EXISTS public.persona (id_persona serial NOT NULL, ' \
                                'nombre_persona character varying, ' \
                                'llave_publica character varying, ' \
                                'puerto bigint, PRIMARY KEY (id_persona))'
                    cursor.execute(sentencia)
                    sentencia = f'ALTER TABLE IF EXISTS public.persona OWNER to sebas'
                    cursor.execute(sentencia)

                    sentencia = 'CREATE TABLE IF NOT EXISTS public.mensajes (' \
                                'id_mensaje serial NOT NULL,' \
                                'mensaje character varying,' \
                                'emisor character varying,' \
                                'destinatario character varying,' \
                                'recibido character varying,' \
                                'PRIMARY KEY (id_mensaje))'
                    cursor.execute(sentencia)
                    sentencia = f'ALTER TABLE IF EXISTS public.mensajes OWNER to sebas'
                    cursor.execute(sentencia)
        except Exception as e:
            print(f'Ocurrió un error: {e}')
        finally:
            conexion.close()

    @staticmethod
    def elimina_tablas_bd():  # Elimina tablas persona y mensajes BD
        conexion = psycopg2.connect(
            user='postgres',
            password='admin2236',
            host='127.0.0.1,',
            port='5432',
            database='mensajes')
        try:
            with conexion:
                with conexion.cursor() as cursor:
                    sentencia = 'DROP TABLE persona'
                    cursor.execute(sentencia)
                    sentencia = f'DROP TABLE mensajes'
                    cursor.execute(sentencia)
        except Exception as e:
            print(f'Ocurrió un error: {e}')
        finally:
            conexion.close()

    @staticmethod
    def inserta_bd(sentencia, valores, conexion):  # Inserta registro en tabla mensajes
        try:
            with conexion:
                with conexion.cursor() as cursor:
                    cursor.execute(sentencia, valores)
                    registros_insertados = cursor.rowcount
                    # print(f'Inserta: {registros_insertados}')
        except Exception as e:
            print(f'Ocurrió un error: {e}')
        finally:
            conexion.close()

    @staticmethod
    def consulta_bd(sentencia, conexion):  # Consulta algun registro en la BD
        try:
            with conexion:
                with conexion.cursor() as cursor:
                    cursor.execute(sentencia)
                    registros = cursor.fetchone()
                    # print(f'Hola, mi nombre es {registros[0]} y mi llave publica es: {registros[1]}')
                    return registros
        except Exception as e:
            print(f'Ocurrió un error: {e}')
        finally:
            conexion.close()

    # Para almacenar la llave publica y nombre del destinatario
    def intercambio_llave_publica(self, puerto_destino):
        sentencia = f'SELECT nombre_persona, llave_publica FROM persona WHERE puerto = {puerto_destino}'
        registro = self.consulta_bd(sentencia, self.conecta_bd())
        self.nombre_destinatario = registro[0]
        self.llave_publica_destinatario = registro[1]

    # Genera la llave privada y su correspondiente llave pública.
    @staticmethod
    def __gen_llaves():
        # Llave Privada:
        privkey = generate_eth_key()
        llave_privada = privkey.to_hex()  # Dar formato a hexadecimal

        # Llave Publica
        llave_publica = privkey.public_key.to_hex()  # Dar formato a hexadecimal
        return llave_privada, llave_publica

    """ Método público accedido por el objeto que quiere comenzar
     la comunicación, los parámetros de entrada son el nombre del objeto
     que comienza la comunicación y el mensaje cifrado con la llave pública
     del destinatario."""

    def saludar(self, name: str, msj: str):
        mensaje_cifrado = self.cifrar_msj(self.llave_publica_destinatario, msj)
        # print(f'Saludando... Hola soy {name} y mi mensaje es: {binascii.hexlify(mensaje_cifrado)}')
        return mensaje_cifrado

    def responder(self, msj: str) -> bytes:
        logging.debug(f' {self._nombre} Respondiendo...')
        msj += " MensajeRespuesta"
        mensaje_cifrado = self.cifrar_msj(self.llave_publica_destinatario, msj)
        return mensaje_cifrado

    @property
    def nombre_obj_s(self) -> str:
        return self._nombre

    # Obtener llave pública del objeto seguro
    @property
    def llave_publica(self) -> str:
        return self.__llave_publica

    @property
    def llave_privada(self) -> str:
        return self.__llave_privada

    # Obtener llave pública del destinatario
    @property
    def llave_publica_destinatario(self) -> str:
        return self.__llave_publica_destinatario

    @llave_publica_destinatario.setter
    def llave_publica_destinatario(self, llave_p_d):
        self.__llave_publica_destinatario = llave_p_d

    # Obtener nombre del destinatario
    @property
    def nombre_destinatario(self) -> str:
        return self.__nombre_destinatario

    @nombre_destinatario.setter
    def nombre_destinatario(self, nombre_d):
        self.__nombre_destinatario = nombre_d

    # para cifrar un mensaje con la llave pública del destinatario
    @classmethod
    def cifrar_msj(cls, pub_key: str, msj: str) -> bytes:
        logging.debug(f'CIFRANDO MENSAJE...')
        logging.debug(f'msj: Tipo: {type(msj)}, {msj}')
        bytes_plain_message = msj.encode()
        logging.debug(f'msj_b: Tipo: {type(bytes_plain_message)}, {bytes_plain_message}')
        cypher_message = encrypt(pub_key, bytes_plain_message)
        logging.debug(f'cypher_message: Tipo: {type(cypher_message)}, {cypher_message}')
        cypher_message = binascii.hexlify(cypher_message)
        logging.debug(f'cypher_message_f: Tipo: {type(cypher_message)}, {cypher_message}')
        logging.debug('MENSAJE CIFRADO\n')
        return cypher_message  # el retorno es el mensaje cifrado.

    # Este método sirve para descifrar un mensaje cifrado
    def descifrar_msj(self, msj: bytes) -> bytes:
        logging.debug('DESCIFRANDO MENSAJE...')
        logging.debug(f'msj_b: Tipo: {type(msj)}, {msj}')
        msj = binascii.a2b_hex(msj)
        decrypted_message = decrypt(self.llave_privada, msj)
        decrypted_message = decrypted_message.decode()
        logging.debug(f'decrypted_message: Tipo: {type(decrypted_message)}, {decrypted_message}')
        logging.debug('MENSAJE DESCIFRADO\n')
        descifrado_b64 = self.codificar64(decrypted_message)
        return descifrado_b64

    # Este método sirve para codificar un mensaje en texto plano en base64
    @staticmethod
    def codificar64(msj: str) -> bytes:
        logging.debug('CODIFICANDO BASE64')
        msj_bytes = msj.encode("utf-8")
        logging.debug(f'msj_bytes: Tipo: {type(msj_bytes)}, {msj_bytes}')
        base64_bytes = base64.b64encode(msj_bytes)
        logging.debug(f'base64_bytes: Tipo: {type(base64_bytes)}, {base64_bytes}')
        logging.debug('MENSAJE CODIFICADO BASE64\n')
        return base64_bytes

    # Este método sirve para decodificar un mensaje en base64 un mensaje en texto plano
    @staticmethod
    def decodificar64(msj: bytes) -> str:
        logging.debug('DECODIFICANDO BASE64')
        logging.debug(f'msj: Tipo: {type(msj)}, {msj}')
        msj1 = msj.decode("utf-8")
        message_bytes = base64.b64decode(msj1)
        base64_message = message_bytes.decode()
        logging.debug(f'base63_deco: Tipo: {type(base64_message)}, {base64_message}')
        logging.debug('MENSAJE DECODIFICADO BASE64\n')
        return base64_message  # el retorno es el mensaje en texto plano.

    # Almacena mensaje en el archivo mensajes.txt
    def __almacenar_msj(self, msj: str) -> dict:
        logging.debug(f'ALMACENANDO MENSAJE EN REGISTRO...')
        sentencia = 'INSERT INTO mensajes(mensaje, emisor, destinatario, recibido) VALUES(%s, %s, %s, %s)'
        valores = (msj, f'{self.nombre_obj_s}', f'{self.nombre_destinatario}',
                   f'{str(datetime.now().strftime("%A, %d of %B %Y at %I:%M %p"))}')
        self.inserta_bd(sentencia, valores, self.conecta_bd())
        sentencia = 'SELECT * FROM mensajes ORDER BY id_mensaje DESC LIMIT 1'
        id = self.consulta_bd(sentencia, self.conecta_bd())
        d = {'ID': id[0]}
        return d

    @classmethod
    def consultar_msj(cls, id: int) -> dict:
        logging.debug(f'CONSULTANDO MENSAJE EN REGISTRO... ')
        logging.debug(f'consulta ID: {id}')
        sentencia = f'SELECT * FROM mensajes WHERE id_mensaje = {id}'
        consulta = {f'ID(\'{id})\'': f'{cls.consulta_bd(sentencia, cls.conecta_bd())}'}
        return consulta

    # Espera respuesta e invoca funcion para almacenar mensaje
    def esperar_respuesta(self, msj: bytes):
        logging.debug(f'{self._nombre} Esperando respuesta...')
        respuesta_descifrada = self.descifrar_msj(msj)
        # respuesta_texto_plano = respuesta_descifrada.decode('utf-8')
        respuesta_texto_plano = self.decodificar64(respuesta_descifrada)
        logging.debug(f'respuesta_texto_plano {respuesta_texto_plano}')
        print(f"<<< : {respuesta_texto_plano}")
        self.__almacenar_msj(respuesta_texto_plano)


if __name__ == '__main__':
    # Instancia objeto seguro, guarda llave publica en bd y recupera la llave publica del destinatario
    obj1 = ObjetoSeguro(pide_nombre())


    def cliente(mensaje):
        host = '127.0.0.1'
        port = obj1.puerto_d
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(mensaje)
            s.close()


    def recepcion():
        host = '127.0.0.1'  # Standard loopback interface address (localhost)
        port = obj1.puerto_e
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f'Nombre: {obj1.nombre_obj_s}, Llave pública: {obj1.llave_publica}')
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    else:
                        print(f"<<< Se recibe mensaje cifrado: {data}")
                        obj1.esperar_respuesta(data)
                        print(">>> ")


    def conversacion():
        # print('Entra thread Conversacion')
        thread_recepcion = threading.Thread(target=recepcion)  # hilo para escuchar mensajes
        thread_recepcion.start()
        # Saludo:
        mensaje = input(">>> ")
        # mensaje += f'{mensaje}, soy: {obj1.nombre_obj_s} y mi llave publica es: {obj1.llave_publica}'
        mensaje2 = obj1.saludar(obj1.nombre_obj_s, mensaje)
        host = '127.0.0.1'
        port = obj1.puerto_d
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  # Abre socket cliente para enviar
            s.connect((host, port))
            s.sendall(mensaje2)
            while True:
                # print('Entra bucle')
                mensaje = input(">>> ")
                if mensaje == 'adios':
                    mensaje_s = obj1.responder('adios')
                    s.sendall(mensaje_s)
                    salida = input('Salir? s/n: ')
                    if salida == 's':
                        s.close()
                        obj1.elimina_tablas_bd()
                        exit()
                    # break
                    # s.sendall(b'')
                else:
                    mensajeb = obj1.responder(mensaje)
                    s.send(mensajeb)


    # Concersacion:
    thread_conversacion = threading.Thread(target=conversacion)  # Hilo para conversacion
    print('Inicia Conversacion')
    thread_conversacion.start()
    # thread_conversacion.join()
