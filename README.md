

<h1>INSTALACION</h1>


1 - Instalar Python superior a la version 3.10
    Recomendamos la ultima que es 3.13.7 localizable en el sitio:

    https://www.python.org/downloads/

    Verifique que sea una version para Windows amd64 


2 - Instalar las librerias necesarias
    De todas las librerias que se utilizan, solo debes instalar "requests" que se utiliza 
    para enviar mensajes mediante Telegram. Para instalar la librería requests, puedes usar pip:
    En la consola de windows tecleas:

    pip install requests

    y esperas a que termine la instalacion. Si esta utilizando cortafuegos en su PC debe
    permitir que la consola de windows y pip accedan a Internet para descargar la librería.


3 - Descomprimir el ZIP que contiene los ficheros del sistema. 
    Cualquier localizacion debería funcionar, pero para hacerlo mas sencillo recomendamos la raíz C:/


4 - Ejecutar el fichero "server.py" dandole doble clic encima.
    Si no se ejecuta con doble clic debe primero comprobar que Python este instalado.
    Si Python esta instalado, pruebe ejecutar el fichero desde la consola de windows.
    Si no sabe ejecutar desde la consola de Windows, consulte al especialista.


5 - Ahora en el navegador Firefox acceda a la dirección http://localhost:8000/
    Debebe abrirse la pagina web del sistema y ya podrá explorar las funcionalidades.


6 - Para verificar que el EndPoint del Bot este funcionando correctamente solo debe
    abrir una nueva pagina en el navegador y colocar la URL:

    http://localhost:8000/api/check_account?account_id=123456789

    En este caso debe responde False porque la cuenta 123456789 no esta agregada a 
    ningun usuario activo. Luego puede probar con un numero de cuenta que si este 
    agregado en un usuario activo y debe devolver True.

    


<h1>PROCESO DE CREACION</h1>


*******  Ejemplo de PROMT para IA DeepSeek donde se explica el funcionamiento del sistema ********

Debes hacer un sistema web para controlar el uso de un bot de trading para Metatrader. 
De forma general, el sistema consiste en una web donde los usuarios se registran y un administrador les asigna un tiempo de uso del bot ("expiration_date"). 
Cada vez que el bot del usuario se ejecuta, consulta un endpoint del sistema que le dice si se puede ejecutar en la cuenta especificada.

Quiero que el sistema tenga las siguientes caracteristicas: 

La web debe componerse de un solo fichero HTML donde contenga todo el codigo HTML, CSS y JAVASCRIPT.
En la web no debes utilizar frameworks de terceros y solo utilizar HTML, CSS y JAVASCRIPT de forma nativa.
El codigo de la web debe poder ejecutarse lo mismo en un server que de forma local sin problemas para acceder a los endpoints.
El diseño de la web debe ser de estilo que trasmita confianza y sea practico para los usuarios.
Debes tener en cuenta que es para usuarios que trabajan el trading mediante BOTS de automatizacion.

El backend debe componerse de un solo fichero Python que se encarga de implementar el servicio web de los endpoints.
Los endpoints deben ser implementados de forma tal que luego el backend pueda ser convertido a codigo C# cuando sea necesario.
En el codigo del backend coloca todos los comentarios y notas que sean necesarias para entender las diferentes partes del codigo y su funcionamiento.
El sistema de bases de datos debe ser mediante ficheros locales tipo JSON.
El backend tiene una constante donde se declara la ruta y nombre de la carpeta local donde se guardan los ficheros del sistema de base de datos.
En el backend se lleva una lista en memoria de los tokens de usuarios autenticados y se sabe cuales estan autenticados como administradores.
El privilegio de administracion se asigna al Token en la lista y no al username, para que al cerrar la sesion ya el usuario no sea administrador.
Si un token de usuario esta autenticado como administrador, este puede acceder a todas las funcionalidades de ver y modificar datos.
La password de administradores se declara en un fichero JSON local llamado "config.json" que se lee cada vez que se autentica un usuario antes de comprobar si su password es de administrador.
En este fichero tambien se guarda el ID de Telegram del usuario administrador y el Token del Bot de Telegram que se utiliza para enviar los datos.
La estructura del fichero de "config.json" es la siguiente:

{
    "admin_password": "admin123",
    "telegram_bot_token": "TU_BOT_TOKEN_AQUI",
    "telegram_chat_id": "TU_CHAT_ID_AQUI"
}

Sistema de base de datos mediante ficheros locales JSON:
Existe una carpeta local donde se guardan los ficheros del sistema de base de datos.
Por cada usuario nuevo que se crea, se crea un fichero JSON con sus datos.
Si un fichero JSON es eliminado se perderan los datos del usuario.
El nombre de cada fichero JSON es el username del usuario, por lo que si este cambia su username, se debe crear un nuevo fichero con el nuevo username que conserve los datos del usuario.
Para encontrar los datos de un usuario, se utiliza el username para acceder al fichero, por lo que los usernames de usuarios no pueden contener caracteres extraños que no sean aceptados como nombres de ficheros.
El sistema de base de datos debe ser implementado utilizando las funcionalidades nativas para JSON y no empleando librerias de terceros, para que luego puede ser reescrito en C#.
Al iniciar el sistema se debe verificar si la carpeta local declarada en el codigo del backend existe y en caso de no existir se debe crear.

La pagina del perfil de usuario debe tener la siguiente estructura:
En el primer panel deben aparecer los datos Nombre de usuario, Email, Telefono, Fecha de expiracion.
Todos los campos son de solo lectura. 
En el segundo panel se encuentra la lista de cuentas y los botones para agregar y eliminar las cuentas.
El tercer panel es desplegable y se llama "Editar datos". 
Al desplegarse el panel, este muestra los datos controles de edicion para los Nombre de usuario, Email, Telefono, nueva contraseña, confirmacion de nueva contraseña y Fecha de expiracion. En el caso de la fecha de expiracion, solo se aparece el control de edicion si el usuario se ha autenticado como administrador. 
Si se cambia el nombre de usuario, inmediatamente se crea un nuevo fichero JSON para el nuevo nombre de usuario con los datos del usuario.
Si el usuario se logea con passord de administrador y obtiene un token de administrador, entonces el campo Fecha de expiracion es editable con un calendario.
Al final del panel hay un boton para guardar los datos editados.




A continuacion te pongo los posibles endpoints que se deben implementar en el backend y que deben ser consultados desde el frontend.
Puedes cambiar lo que sea necesario, siempre y cuendo el sistema mantenga la funcionalidad basica que se ha explicado.

ENDPOINTS DE LOS USUARIOS CLIENTES

Caso de uso #1
El cliente se registra por primera vez en la web insertando estos parámetros:
- username (obligatorio)
- email (obligatorio)
- phone (opcional)
- password (obligatorio)
- repeat password (obligatorio)
El EndPoint recibe todos esos parametros y verifica que el username no este utilizado.
Si el username esta siendo utilizado, devuelve string vacio y si esta disponible, crea la cuenta y devuelve el token del usuario.
No es necesario verificar la cuenta porque si el usuario pierde la password puede contactar al administrador o crearse una nueva cuenta con otro username.
El parametro interno llamado "expiration_date" tiene la fecha 1ro de enero de 2000.
Este parametro "expiration_date" determina si el usuario puede utilizar el BOT y su utilizacion se explicara mas adelante.
Para mantener seguridad en el sistema, la password del usuario debe guardarse como hash (SHA-256).
Al terminar el registro se envía un mensaje "NUEVO USUARIO" por Telegram al administrador con los datos del usario:
username, email, phone, telegram user alias


Caso de uso #2
El cliente se autentica para entrar a la cuenta y ver o modificar algo. 
Inserta los parámetros:
- username
- password
El EndPoint recibe como parámetros el email y password y devuelve el token del usuario si el usuario y password son correctos.
Si el usuario o password son incorrectos, devuelve cadena vacia.
Como la password almacenada es un Hash de la original, el endpoint debe hacer un hash (SHA-256) de la password entrante para compararla con el hash almacenado.
Al terminar el login se envía un mensaje "LOGUIN DE USUARIO" por Telegram al administrador con los datos del usario:
username
Importante, si la password es la password de administracion (esta se define en el sistema mediante un fichero local) entonces se devuelve el token del usuario, pero el usuario se considera administrador y puede ver y modificar todos los datos.
Eso se maneja internamente en la lista de tokensa de usuarios, donde se marca el token como administrador para que este tenga derecho a ver y modificar todo.


Caso de uso #3
El cliente pide los datos del usuario para mostrar en la pagina. 
Inserta los parámetros:
- token de usuario
El EndPoint recibe como parámetros el token de usuario y devuelve un JSON con los datos del usuario que se deben mostrar en la pagina, ecepto la password.
Al obtener los datos del usuario, la pagina debe mostrar el perfil del usuario con la lista de cuentas agregadas y con los controles que permitan modificar los datos del usuario y cambiar la password.
Si el token es administrador porque el usuario se autentico con password de administrador, entonces la pagina debe permitir modificar el "expiration_date".
Si el token no es administrador, entonces el "expiration_date" solo se muestra como readonly.


Caso de uso #4
El cliente estando autenticado, puede agregar las cuentas que va a usar. 
Inserta los parámetros:
- token de usuario
- ID de cuenta a agregar
Las cuentas son ID numéricos pero los trataremos como strings. 
Las cuentas agregadas se muestran en el perfil del usuario como una lista de identificadores de cuentas.
El EndPoint recibe como parámetros el token de usuario y el identificador de una cuenta. 
Devuelve True si se pudo agregar el identificador de la cuenta para agregar. 
Devuelve False si no se puede agregar el identificador.
Al agregar una cuenta se envía un mensaje "USUARIO AGREGO CUENTA" por Telegram al administrador con los datos del usario:
- username
- ID de la cuenta agregada


Caso de uso #5
El cliente estando autenticado, puede eliminar cuentas de la Lista de Identificadores de Cuentas. 
Inserta los parámetros:
- token de usuario
- ID de cuenta a eliminar
El EndPoint recibe como parámetros el token de usuario y el identificador de una cuenta para eliminar. 
Devuelve True si se pudo eliminar el identificador de la cuenta. 
Devuelve False si no se puede eliminar el identificador.
Al eliminar una cuenta se envía un mensaje "USUARIO ELIMINO CUENTA" por Telegram al administrador con los datos del usario:
- username
- ID de la cuenta eliminada


Casos de uso #6, #7, #8, #9
El cliente estando autenticado, puede modificar datos de usuario como son username, email, phone, password, etc.
Se deben crear los endpoints necesarios para cada una de estas modificaciones y no se deben aceptar vacios.
los endpoints reciben los parámetros:
- token de usuario
- nuevo valor que va a sustituir el actual (depende del endpoint)
Devuelve True si se pudo modificar el dato del usuario. 
Devuelve False si no se pudo modificar el dato del usuario. 
Al modificar una dato del usuario se envía un mensaje "MODIFICACION DE USUARIO" por Telegram al administrador con los datos del usario:
- username
- dato modificado
- nuevo valor


Caso de uso #10
El cliente estando autenticado, puede eliminar todas las cuentas de la Lista de Identificadores de Cuentas. 
Inserta los parámetros:
- token de usuario
El EndPoint recibe como parámetros el token de usuario. 
Devuelve True si se pudo eliminar todas las cuentas. 
Devuelve False si no se pudo eliminar todas las cuentas.
Al eliminar una cuenta se envía un mensaje "USUARIO ELIMINO TODAS LAS CUENTAS" por Telegram al administrador con los datos del usario:
- username



Casos de uso #11
El cliente estando autenticado como administrador, puede modificar el parametro "expiration_date".
El endpoint recibe los parámetros:
- token de usuario
- nuevo valor de "expiration_date"
Devuelve True si se pudo modificar el valor. 
Devuelve False si no se pudo modificar el valor. 
Al modificar una dato del usuario se envía un mensaje "MODIFICACION DE EXPIRATION DATE" por Telegram al administrador con los datos del usario:
- username
- nuevo valor del "expiration_date"



ENDPOINTS QUE UTILIZAN LOS BOTS

Caso de uso #1
Existe un EndPoint que permite consultar si una cuenta está agregada por un usuario autorizado. 
Cada usuario tiene un parametro llamado "expiration_date" que es la fecha de expiracion del uso del BOT.
Al crearse el usuario, este dato por defecto tiene la fecha 1ro de enero de 2000 la cual se considera expirada porque es menor que la fecha actual y por tanto es un usuario no autorizado.
El administrador del sistema es el unico usuario que puede modificar la fecha de expiracion de los usuarios.
Recibe como parámetros el identificador de una cuenta. 
Devuelve True si la cuenta pertenece a un usuario activo y la fecha del sistema es menor que la fecha "expiration_date" asignada al usuario. 
Devuelve False si la cuenta no ha sido agregada por ningún usuario o si está agregada por un usuario inactivo o si la fecha del sistema es mayor o igual que la fecha "expiration_date" asignada al usuario.


OTRAS ESPECIFICACIONES

Asegurate de implementar el servidor de forma que sirva el archivo HTML cuando se acceda a la raíz (/).
Cuando se acceda a http://localhost:8000, el servidor debería servir correctamente el archivo HTML y el frontend funcionar adecuadamente.
Agrega manejo de codificación UTF-8 para el archivo HTML.
Ten en cuenta que el navegador puede bloquear las peticiones CORS. 
Necesito que el backend maneje adecuadamente las solicitudes CORS para evitar errores como este:

"Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource at localhost:8000/login. 
(Reason: CORS request not http)"

Los mensajes de Telegram deben indicar si las operaciones son realizadas por un administrador.
El estado de administrador es temporal (dura solo durante la sesión del token).
Quiero que las fechas de expiracion y todas en general se muestren en formato dd/mm/yyyy.
Añade comprobaciones para todos los document.getElementById() para asegurarte de que el elemento existe antes de usarlo.
Añade un event listener para DOMContentLoaded que asegura que todo el DOM esté cargado antes de ejecutar el código JavaScript.
Añade otras comprobaciones de errores y mensajes de consola para facilitar la depuración.


Al terminar, creame una lista sencilla con ejemplos de las llamadas a los endpoints.



<H3>Si necesitas hacer un bot de trading con tu propia estrategia, hacer backtesting, analisis de datos de mercados, o necesitas acesoramiento sobre bots de trading y automatización en exchanges de criptomonedas... escríbeme!</H3>

Santiago Orellana <br>
Email: <a href="mailto:codechago@gmail.com?Subject=Quiero%20un%20bot%20de%20trading">codechago@gmail.com</a><br>
Whatsapp: <a href="https://wa.me/5354635944?text=Quiero contratar tus servicios">+5354635944</a>
