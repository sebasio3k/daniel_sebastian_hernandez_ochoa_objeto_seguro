# daniel_sebastian_hernandez_ochoa_objeto_seguro
Proyecto Final Intel

Buen día, mis dudas son las siguientes:

1.- con respecto al diagrama: 

<img width="744" alt="Captura de Pantalla 2021-12-08 a la(s) 19 27 11" src="https://user-images.githubusercontent.com/39862006/145317649-52fc59dd-3d8c-441c-a4b0-b649bc25610f.png">

En el apartado "Cifrado de un mensaje con una llave pública", el proceso indica que se recibe un texto plano y una llave pública, después se codifica el mensaje (Texto plano), para después ser cifrado mediante la llave pública del destinatario, para así obtener un cifrado en formato bytes

Seguidamente en el apartado "Descifrado de un mensaje con la llave privada" se recibe el cifrado anterior en formato bytes para realizar el descifrado con la llave privada del receptor, a continuación se decodifica el descifrado, y en este caso se obtendría un texto en formato str (Texto plano).

Hasta aquí todo bien, pero el proceso de los diagramas no corresponde a la declaración de la función descifrar_msj, donde retorna bytes:

<img width="601" alt="Captura de Pantalla 2021-12-08 a la(s) 19 31 55" src="https://user-images.githubusercontent.com/39862006/145318069-4aad56b0-f522-4c07-a41f-efd379d8e761.png">

Mi duda es si tengo que hacerle caso al diagrama retornando un str o a la declaración de la funcion descifrar_msj, retornando bytes
