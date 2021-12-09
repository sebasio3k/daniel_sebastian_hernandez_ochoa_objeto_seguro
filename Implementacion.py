import sandbox as obj_s
import logging

logging.basicConfig(level=logging.DEBUG, format="\n%(asctime)s - %(message)s")

# Creación de objetos seguros
objeto1_nombre = "Alice"
objeto1_mensaje = "¿Hola soy Alice cómo estas?"
objeto1 = obj_s.ObjetoSeguro(objeto1_nombre)
objeto1_llave_publica = objeto1.llave_publica

objeto2_nombre = "Sebastian"
objeto2_mensaje = "Hola soy Sebastian, Bien, ¿y tú?"
objeto2 = obj_s.ObjetoSeguro(objeto2_nombre)
objeto2_llave_publica = objeto2.llave_publica

# Intercambio de llaves
logging.debug("INTERCAMBIO DE LLAVES".center(50, '-'))
objeto1.intercambio_llave_publica(objeto2_llave_publica, objeto2_nombre)
logging.debug(f'OBJ 1 Llave Publica destinatario: {objeto1.llave_publica_destinatario}')
objeto2.intercambio_llave_publica(objeto1_llave_publica, objeto1_nombre)
logging.debug(f'OBJ 2 Llave Publica destinatario: {objeto2.llave_publica_destinatario}')

# HandShake
logging.debug("SALUDO OBJ1".center(50, '-'))
saludo_de_obj1 = objeto1.saludar(objeto1_nombre, objeto1_mensaje)
objeto2.esperar_respuesta(saludo_de_obj1)
consulta = objeto2.consultar_msj(0)
logging.debug(f'Consulta: {consulta}')

logging.debug("RESPUESTA OBJ2".center(50, '-'))
obj2_respuesta = objeto2.responder(objeto2_mensaje)
objeto1.esperar_respuesta(obj2_respuesta)
consulta2 = objeto1.consultar_msj(1)
logging.debug(f'Consulta: {consulta2}')

obj1_respuesta = objeto1.responder("Muy Bien, ¿qué haces?")
objeto2.esperar_respuesta(obj1_respuesta)
consulta = objeto2.consultar_msj(2)
logging.debug(f'Consulta: {consulta}')

obj2_respuesta = objeto2.responder("nada, ¿y tú jeje?")
objeto1.esperar_respuesta(obj2_respuesta)
consulta2 = objeto1.consultar_msj(3)
logging.debug(f'Consulta: {consulta2}')
