# Guia Rapida de la Aplicación

Esta aplicación permite subir una imagen, escribir un texto y colocar
ese texto en la imagen en las coordenadas que elijas.



------------------------------------------------------------------------
# Requerimientos iniciales 
Necesitaras hacer instalar unas dependencias, por conveniencia se 
encuentran el el archivo "requirements.txt" 
- usa el comando "pip install -r requirements.txt" 

Esta integracion es una prueba y por lo tanto fue diseñada para usarse 
utilizando XAMPP:
https://www.apachefriends.org/es/index.html

------------------------------------------------------------------------
## Setup inicial 
ve a C:\xampp\htdocs\ y coloca los archivos del repositorio 
tambien puedes ponerlos en una carpeta adicional si lo deseas 
para esta guia asumiremos que la ruta completa es C:\xampp\htdocs\Procesador

Antes de poder usar la pagina necesitasa hacer preparaciones:
1.Abre XAMPP y empieza el modulo apache
2.inicia el servidor unicorn 
- si ya estas en el directorio de la carpeta puedes usar "python dev.py" en terminal
- alternativamente puedes iniciarlo manualmente "uvicorn main:app --reload --host 0.0.0.0 --port 8000"

Una vez realizado esto ya deberias poder acceder a la pagina 
ve a http://localhost/index.html 
si creaste una carpeta en htdocs para guardar los archivos el enlace seria asi
http://localhost/(tu_carpeta)/index.html

en mi caso se veria como http://localhost/Procesador/index.html

esto te llevara a la pagina principal 

------------------------------------------------------------------------



## 1. Subir imagen

-   Elige cualquier archivo de imagen (PNG, JPG, etc.).


------------------------------------------------------------------------

## 2. Escribir el texto que deseas añadir

-   En el campo **"Texto a agregar"**, escribe lo que quieras que
    aparezca sobre la imagen.

------------------------------------------------------------------------

## 3. Elegir las coordenadas

-   Ingresa los valores de **X** y **Y**.
-   Estas coordenadas indican dónde se dibujara el texto sobre la
    imagen.

------------------------------------------------------------------------

## 4. Procesar

-   Da clic en **"Procesar"**.
-   La aplicación genera una copia de la imagen con el texto incrustado.


------------------------------------------------------------------------

## 5. Descargar 

-   Si lo deseas, puedes guardar la imagen final usando el boton de
    descarga.

------------------------------------------------------------------------

