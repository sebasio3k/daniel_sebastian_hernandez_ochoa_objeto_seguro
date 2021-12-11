import Objeto_seguro_P1 as Obj_s
import logging

logging.basicConfig(level=logging.DEBUG, format="\n%(asctime)s - %(message)s")

# Creación de objetos seguros
# Alice
objeto1_nombre = "Alice"
objeto1_mensaje = "Hola soy Alice como estas?"
objeto1 = Obj_s.ObjetoSeguro(objeto1_nombre)
objeto1_llave_publica = objeto1.llave_publica
# Sebastian
objeto2_nombre = "Sebastian"
objeto2_mensaje = "Hola soy Sebastian, Bien, y tu?"
objeto2 = Obj_s.ObjetoSeguro(objeto2_nombre)
objeto2_llave_publica = objeto2.llave_publica

# Intercambio de llaves
logging.debug("INTERCAMBIO DE LLAVES".center(50, '-'))
objeto1.intercambio_llave_publica(objeto2_llave_publica, objeto2_nombre)
logging.debug(f'OBJ 1 (Alice); Llave Publica destinatario: {objeto1.llave_publica_destinatario}')
objeto2.intercambio_llave_publica(objeto1_llave_publica, objeto1_nombre)
logging.debug(f'OBJ 2; (Sebastian) Llave Publica destinatario: {objeto2.llave_publica_destinatario}')

# HandShake
logging.debug("COMIENZA COMUNICACIÓN ENTRE OBJETOS SEGUROS".center(50, '-'))
logging.debug("SALUDO DE OBJ1 A OBJ2...".center(100, '-'))
# Objeto 1 genera su saludo:
saludo_de_obj1 = objeto1.saludar(objeto1_nombre, objeto1_mensaje)
# Objeto 2 está a la espera de un mensaje:
objeto2.esperar_respuesta(saludo_de_obj1)
# Se consulta el mensaje almacenado en archivo mensajes.txt
consulta = objeto2.consultar_msj(0)
logging.debug(f'Consulta: {consulta}')

logging.debug("RESPUESTA OBJ2 A OBJ1".center(50, '-'))
# Objeto 2 genera su saludo:
obj2_respuesta = objeto2.responder(objeto2_mensaje)
# Objeto 1 está a la espera de un mensaje:
objeto1.esperar_respuesta(obj2_respuesta)
# Se consulta el mensaje alamacenado en erchivo mensajes.txt
consulta2 = objeto1.consultar_msj(1)
logging.debug(f'Consulta: {consulta2}')

obj1_respuesta = objeto1.responder("Muy Bien, que haces?")
objeto2.esperar_respuesta(obj1_respuesta)
consulta = objeto2.consultar_msj(2)
logging.debug(f'Consulta: {consulta}')

obj2_respuesta = objeto2.responder("nada, y tu jeje?")
objeto1.esperar_respuesta(obj2_respuesta)
consulta2 = objeto1.consultar_msj(3)
logging.debug(f'Consulta: {consulta2}')
