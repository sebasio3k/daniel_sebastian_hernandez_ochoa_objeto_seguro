from ecies.utils import generate_eth_key
from ecies import encrypt, decrypt
import base64
import binascii
from pathlib import Path
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format="\n%(asctime)s - %(message)s")


# Creación de un objeto seguro, se recibe el nombre en formato String.
class ObjetoSeguro:
    # Constructor
    def __init__(self, nombre_objeto):
        self._nombre = nombre_objeto
        self.__llave_privada, self.__llave_publica = self.__gen_llaves()
        logging.debug(f'Llave publica: {self._nombre}: {type(self.__llave_publica)}, {self.__llave_publica}')
        self.__llave_publica_destinatario = None
        self.__nombre_destinatario = None
        Path('./mensajes.txt').touch(exist_ok=True)  # crea archivo para almacenar mensajes

    # Para almacenar la llave publica y nombre del destinatario
    def intercambio_llave_publica(self, llave_p_destinatario, nombre_destiinatario):
        self.llave_publica_destinatario = llave_p_destinatario
        self.nombre_destinatario = nombre_destiinatario

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
        logging.debug(f'Saludando... Hola soy {name} y mi mensaje es: {binascii.hexlify(mensaje_cifrado)}')
        return mensaje_cifrado

    def responder(self, msj: str) -> bytes:
        logging.debug(f' {self._nombre} Respondiendo...')
        msj += " MensajeRespuesta"
        mensaje_cifrado = self.cifrar_msj(self.llave_publica_destinatario, msj)
        return mensaje_cifrado

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
        # b64_plain_message_b = cls.codificar64(msj)
        bytes_plain_message = msj.encode()
        logging.debug(f'msj_b: Tipo: {type(bytes_plain_message)}, {bytes_plain_message}')
        cypher_message = encrypt(pub_key, bytes_plain_message)
        logging.debug(f'cypher_message: Tipo: {type(cypher_message)}, {cypher_message}')
        cypher_message = binascii.hexlify(cypher_message)
        logging.debug(f'cypher_message_f: Tipo: {type(cypher_message)}, {cypher_message}')
        # cypher_message = cypher_message.decode()
        # cypher_message = cls.codificar64(cypher_message)
        # logging.debug(f'cypher_message: Tipo: {type(cypher_message)}, {cypher_message}')
        logging.debug('MENSAJE CIFRADO\n')
        return cypher_message  # el retorno es el mensaje cifrado.

    # Este método sirve para descifrar un mensaje cifrado
    def descifrar_msj(self, msj: bytes) -> bytes:
        logging.debug('DESCIFRANDO MENSAJE...')
        logging.debug(f'msj_b: Tipo: {type(msj)}, {msj}')
        # deco = msj.decode()
        msj = binascii.a2b_hex(msj)
        decrypted_message = decrypt(self.llave_privada, msj)
        decrypted_message = decrypted_message.decode()
        logging.debug(f'decrypted_message: Tipo: {type(decrypted_message)}, {decrypted_message}')
        # deco = self.decodificar64(decrypted_message)
        logging.debug('MENSAJE DESCIFRADO\n')
        descifrado_b64 = self.codificar64(decrypted_message)
        return descifrado_b64

    # Este método sirve para codificar un mensaje en texto plano en base64
    @staticmethod
    def codificar64(msj: str) -> bytes:
        logging.debug('CODIFICANDO BASE64')
        # msj_bytes = msj.encode('ascii')
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
        id = 0
        diccionario = {}
        if Path('./mensajes.txt').stat().st_size == 0:  # si esta vacio
            diccionario[f'{id}'] = {
                "ID: ": id,
                "Mensaje: ": msj,
                "De: ": self.nombre_destinatario,
                "Recibido el: ": str(datetime.now().strftime("%A, %d of %B %Y at %I:%M %p")),
                "Recibido por: ": self._nombre
            }
            with open('./mensajes.txt', 'r+', encoding="utf-8") as f:
                json.dump(diccionario, f, sort_keys=True, indent=4)  # escribe diccionario en archivo .txt
                d = {'ID': id}
                return d
        else:
            # leer archivo
            with open('./mensajes.txt', 'r', encoding="utf-8") as mensajes:
                diccionario = json.load(mensajes)  # guarda contenido de archivo en un diccionario
                logging.debug(f'diccionario: {diccionario}')
                claves = list(diccionario)  # recupera claves de diccionario
                id = int(claves[-1]) + 1  # actualiza el id con respecto a la ultima clave del diccionario
            # Escribir archivo
            with open('./mensajes.txt', 'w', encoding="utf-8") as m:
                diccionario[f'{id}'] = {
                    "ID: ": id,
                    "Mensaje: ": msj,
                    "De: ": self.nombre_destinatario,
                    "Recibido el: ": str(datetime.now().strftime("%A, %d of %B %Y at %I:%M %p")),
                    "Recibido por: ": self._nombre
                }
                json.dump(diccionario, m, sort_keys=True, indent=4)  # escribe diccionario en archivo txt
                d = {'ID': id}
                return d

    @staticmethod
    def consultar_msj(id: int) -> dict:
        logging.debug(f'CONSULTANDO MENSAJE EN REGISTRO... ')
        logging.debug(f'consulta ID: {id}')
        if Path('./mensajes.txt').stat().st_size == 0:  # si esta vacio
            d = {'ID': 'Null',
                 'Mensaje:': 'EL Registro está vacio...'}
            return d  # retorna dicionario que indica que el archivo esta vacio
        else:  # si no esta vacio
            # leer archivo
            with open('./mensajes.txt', 'r', encoding='utf-8') as mensajes:
                diccionario = json.load(mensajes)  # recupera diccionario
                consulta = diccionario[f'{id}']  # consulta el valor con la clave id
                return consulta  # retorna la consulta

    # Espera respuesta e invoca funcion para almacenar mensaje
    def esperar_respuesta(self, msj: bytes):
        logging.debug(f'{self._nombre} Esperando respuesta...')
        respuesta_descifrada = self.descifrar_msj(msj)
        # respuesta_texto_plano = respuesta_descifrada.decode('utf-8')
        respuesta_texto_plano = self.decodificar64(respuesta_descifrada)
        logging.debug(f'respuesta_texto_plano {respuesta_texto_plano}')
        self.__almacenar_msj(respuesta_texto_plano)
