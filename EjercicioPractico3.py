# ============================================================================
# IMPORTACIONES
# ============================================================================
import threading  # Para crear y gestionar hilos
import time       # Para pausas y simulación de procesamiento lento
import random     # Para generar datos aleatorios en el fichero
from datetime import datetime  # Para mostrar fecha y hora

# ============================================================================
# VARIABLES GLOBALES
# ============================================================================
# Variable compartida que almacena el número de líneas con "ERROR"
# Esta variable será accedida tanto por el hilo principal como el secundario
contador_errores = 0

# Semáforo binario (valor inicial = 1) para proteger el acceso a contador_errores
# Solo un hilo puede acceder a la variable compartida a la vez
semaforo = threading.Semaphore(1)

# Bandera para indicar si el hilo secundario ha terminado su trabajo
hilo_terminado = False

# ============================================================================
# FUNCIÓN: Generar fichero de prueba
# ============================================================================
def generar_fichero_grande(nombre_archivo, num_lineas=5000):
    """
    Genera un fichero de texto simulando logs de una aplicación.
    
    Args:
        nombre_archivo: Nombre del fichero a crear
        num_lineas: Número de líneas a generar (por defecto 5000)
    """
    print(f"Generando fichero con {num_lineas} líneas...")
    
    # Lista de mensajes de log posibles (algunos contienen "ERROR")
    mensajes_posibles = [
        "INFO: Sistema iniciado correctamente",
        "ERROR: No se pudo conectar a la base de datos",
        "WARNING: Memoria baja disponible",
        "ERROR: Timeout en la petición",
        "INFO: Usuario autenticado",
        "DEBUG: Procesando solicitud",
        "ERROR: Archivo no encontrado",
        "INFO: Operación completada con éxito",
        "WARNING: Certificado SSL próximo a expirar",
        "ERROR: Permiso denegado"
    ]
    
    # Crear el fichero y escribir líneas aleatorias
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        for i in range(num_lineas):
            # Cada línea tiene un número y un mensaje aleatorio
            linea = f"[{i+1}] {random.choice(mensajes_posibles)}\n"
            f.write(linea)
    
    print(f"Fichero '{nombre_archivo}' generado correctamente.\n")

# ============================================================================
# FUNCIÓN: Contar errores (ejecutada por el HILO SECUNDARIO)
# ============================================================================
def contar_errores_en_fichero(nombre_archivo, palabra_clave="ERROR"):
    """
    Función que será ejecutada por el hilo secundario.
    Lee el fichero línea por línea y cuenta las ocurrencias de una palabra clave.
    
    Args:
        nombre_archivo: Ruta del fichero a procesar
        palabra_clave: Palabra a buscar en cada línea (por defecto "ERROR")
    """
    # Declarar que usaremos las variables globales
    global contador_errores, hilo_terminado
    
    print(f"🔄 Hilo secundario iniciado. Buscando '{palabra_clave}'...\n")
    
    # Contador local temporal (no compartido)
    contador_local = 0
    
    try:
        # Abrir el fichero para lectura
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            # Leer todas las líneas del fichero
            lineas = f.readlines()
            total_lineas = len(lineas)
            
            # Procesar cada línea del fichero
            for i, linea in enumerate(lineas):
                # SIMULAR PROCESAMIENTO LENTO
                # Esto hace que el hilo tarde varios segundos en completar
                time.sleep(0.001)  # Pausa de 1 milisegundo por línea
                
                # Verificar si la línea contiene la palabra clave
                if palabra_clave in linea:
                    contador_local += 1
                
                # Mostrar progreso cada 1000 líneas procesadas
                if (i + 1) % 1000 == 0:
                    print(f"    Progreso: {i+1}/{total_lineas} líneas procesadas")
        
        # ===================================================================
        # SECCIÓN CRÍTICA: Actualizar la variable compartida
        # ===================================================================
        # ADQUIRIR el semáforo (bloquear el acceso para otros hilos)
        semaforo.acquire()
        try:
            # Actualizar la variable compartida de forma segura
            contador_errores = contador_local
        finally:
            # LIBERAR el semáforo (permitir acceso a otros hilos)
            # El bloque finally garantiza que siempre se libere, incluso si hay error
            semaforo.release()
        # ===================================================================
        
        print(f"\n Hilo secundario terminado. Se encontraron {contador_local} ocurrencias de '{palabra_clave}'.\n")
    
    except Exception as e:
        # Capturar cualquier error durante la lectura del fichero
        print(f"\n Error en el hilo secundario: {e}\n")
    
    finally:
        # Marcar que el hilo ha terminado (siempre se ejecuta)
        hilo_terminado = True

# ============================================================================
# FUNCIONES DEL MENÚ PRINCIPAL
# ============================================================================

def mostrar_menu():
    """Muestra el menú de opciones disponibles"""
    print("\n" + "="*50)
    print("MENÚ PRINCIPAL")
    print("="*50)
    print("1. Mostrar hora actual")
    print("2. Mostrar mensaje de bienvenida")
    print("3. Mostrar estado del contador")
    print("4. Calcular suma de dos números")
    print("5. Salir")
    print("="*50)

def mostrar_hora_actual():
    """Muestra la hora y fecha actual del sistema"""
    hora = datetime.now().strftime("%H:%M:%S")
    fecha = datetime.now().strftime("%d/%m/%Y")
    print(f"\n Hora actual: {hora}")
    print(f" Fecha: {fecha}\n")

def mostrar_mensaje():
    """Muestra un mensaje motivacional aleatorio"""
    mensajes = [
        "¡Que tengas un excelente día!",
        "El trabajo duro siempre da sus frutos",
        "Sigue aprendiendo Python, ¡vas muy bien!",
        "Recuerda hacer pausas mientras programas",
        "La práctica hace al maestro"
    ]
    print(f"\n {random.choice(mensajes)}\n")

def mostrar_estado_contador():
    """
    Muestra el estado actual del contador de forma segura.
    Usa el semáforo para acceder a la variable compartida sin conflictos.
    """
    # ADQUIRIR el semáforo antes de leer la variable compartida
    semaforo.acquire()
    try:
        # Leer la variable compartida de forma segura
        if hilo_terminado:
            print(f"\n El conteo ha finalizado: {contador_errores} ocurrencias encontradas.\n")
        else:
            print(f"\n El hilo está procesando... Contador actual: {contador_errores}\n")
    finally:
        # LIBERAR el semáforo
        semaforo.release()

def calcular_suma():
    """Solicita dos números al usuario y muestra su suma"""
    try:
        num1 = float(input("Ingresa el primer número: "))
        num2 = float(input("Ingresa el segundo número: "))
        resultado = num1 + num2
        print(f"\n {num1} + {num2} = {resultado}\n")
    except ValueError:
        print("\n Error: Debes ingresar números válidos.\n")

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================
def main():
    """
    Función principal del programa.
    - Genera el fichero de prueba
    - Crea y lanza el hilo secundario
    - Muestra el menú principal y gestiona las opciones
    - Al salir, espera a que el hilo termine y muestra el resultado final
    """
    print("\n" + " PROGRAMA DE CONTEO DE PALABRAS CON HILOS ".center(50))
    print("="*50 + "\n")
    
    # ========================================================================
    # CONFIGURACIÓN INICIAL
    # ========================================================================
    nombre_archivo = "log_grande.txt"  # Nombre del fichero a crear
    palabra_clave = "ERROR"            # Palabra a buscar en el fichero
    num_lineas = 5000                  # Número de líneas a generar
    
    # ========================================================================
    # PASO 1: Generar el fichero de prueba
    # ========================================================================
    generar_fichero_grande(nombre_archivo, num_lineas)
    
    # ========================================================================
    # PASO 2: Crear y lanzar el HILO SECUNDARIO
    # ========================================================================
    # threading.Thread() crea un nuevo hilo
    # target: función que ejecutará el hilo
    # args: argumentos que se pasarán a la función
    hilo = threading.Thread(
        target=contar_errores_en_fichero, 
        args=(nombre_archivo, palabra_clave)
    )
    
    # start() inicia la ejecución del hilo
    # A partir de aquí, el hilo secundario trabaja en paralelo
    hilo.start()
    
    # ========================================================================
    # PASO 3: BUCLE PRINCIPAL DEL MENÚ (HILO PRINCIPAL)
    # ========================================================================
    # Este bucle se ejecuta en el hilo principal mientras el hilo secundario
    # procesa el fichero en segundo plano
    while True:
        mostrar_menu()
        opcion = input("Elige una opción (1-5): ").strip()
        
        # Procesar la opción seleccionada por el usuario
        if opcion == "1":
            mostrar_hora_actual()
        elif opcion == "2":
            mostrar_mensaje()
        elif opcion == "3":
            mostrar_estado_contador()
        elif opcion == "4":
            calcular_suma()
        elif opcion == "5":
            print("\n Saliendo del programa...")
            
            # Si el hilo aún no ha terminado, esperamos a que finalice
            if not hilo_terminado:
                print(" Esperando a que el hilo secundario termine...\n")
                # join() bloquea el hilo principal hasta que el secundario termine
                hilo.join()
            break  # Salir del bucle while
        else:
            print("\n❌ Opción no válida. Intenta de nuevo.\n")
        
        # Pequeña pausa para mejorar la legibilidad de la salida
        time.sleep(0.5)
    
    # ========================================================================
    # PASO 4: Mostrar RESULTADO FINAL
    # ========================================================================
    print("\n" + "="*50)
    print("RESULTADO FINAL".center(50))
    print("="*50)
    
    # Acceder a la variable compartida de forma segura con el semáforo
    semaforo.acquire()
    try:
        print(f" Total de líneas con '{palabra_clave}': {contador_errores}")
    finally:
        semaforo.release()
    
    print("="*50 + "\n")
    print("Programa finalizado. ¡Hasta pronto! \n")

# ============================================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# ============================================================================
if __name__ == "__main__":
    # Este bloque solo se ejecuta si el archivo se ejecuta directamente
    # (no si se importa como módulo)
    main()