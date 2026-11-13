# @Author: FABIAN MUÑOZ BOLAÑOS
# @Date: 2026-11-12
# @Description: Módulo base - Gestión de Clientes, Excepciones y Logs (Fase 4)

# Importamos datetime para registrar la fecha y hora exacta en los logs
import datetime
# Importamos ABC (Abstract Base Classes) y abstractmethod para crear clases abstractas puras
from abc import ABC, abstractmethod

# ==========================================
# 1. EXCEPCIONES PERSONALIZADAS
# Cumplimiento Anexo 3: Manejo robusto de excepciones y excepciones personalizadas
# ==========================================

# Creamos una excepción específica para cuando los datos del cliente son incorrectos
class DatoInvalidoError(Exception):
    """Excepción lanzada cuando un dato no cumple con las validaciones de negocio."""
    pass

# Creamos una excepción general para fallos críticos que detendrían una operación
class OperacionFallidaError(Exception):
    """Excepción lanzada para encapsular errores graves mediante encadenamiento."""
    pass


# ==========================================
# 2. GESTOR DE LOGS (Manejo de archivos)
# Cumplimiento Anexo 3: Archivo de logs donde se registren errores y eventos relevantes
# ==========================================

class GestorLogs:
    # Usamos staticmethod para poder llamar a la función sin instanciar la clase
    @staticmethod
    def registrar_evento(mensaje, excepcion=None):
        """Registra errores y eventos en un archivo .log manteniendo la aplicación estable."""
        
        # Bloque TRY: Intentamos abrir el archivo en modo 'a' (append) para agregar texto sin borrar lo anterior
        try:
            archivo = open("sistema_errores.log", "a", encoding="utf-8")
            # Obtenemos la fecha y hora actual formateada como Año-Mes-Día Hora:Minuto:Segundo
            fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Si se pasó una excepción como parámetro, estructuramos un mensaje de ERROR
            if excepcion:
                registro = f"[{fecha_hora}] ERROR: {mensaje} | Detalle: {str(excepcion)}\n"
            # Si no hay excepción, estructuramos un mensaje puramente INFORMATIVO
            else:
                registro = f"[{fecha_hora}] INFO: {mensaje}\n"
                
            # Escribimos el mensaje estructurado dentro del archivo de texto
            archivo.write(registro)
            
        # Bloque EXCEPT: Capturamos errores del sistema de archivos (ej. permisos denegados)
        except IOError as e:
            # Imprimimos en consola para que el programa no se congele si falla el disco duro
            print(f"Error crítico al escribir en el log: {e}")
            
        # Bloque FINALLY: Exigido por la guía. Se ejecuta SIEMPRE, haya ocurrido un error o no
        finally:
            # Verificamos si la variable 'archivo' existe en la memoria local y si no está cerrada
            if 'archivo' in locals() and not archivo.closed:
                # Cerramos el archivo de forma segura para liberar memoria RAM
                archivo.close()


# ==========================================
# 3. CLASE ABSTRACTA BASE
# Cumplimiento Anexo 3: Una clase abstracta que represente entidades generales
# ==========================================

# Heredamos de ABC para convertir esta clase en una plantilla abstracta
class EntidadSistema(ABC):
    """Clase abstracta que representa entidades generales del sistema."""
    
    # Decorador que obliga a las clases hijas a implementar este método (Polimorfismo)
    @abstractmethod
    def obtener_informacion(self):
        """Método que deberá ser implementado obligatoriamente por las clases derivadas."""
        pass


# ==========================================
# 4. CLASE CLIENTE (Encapsulación y Validaciones)
# Cumplimiento Anexo 3: Clase Cliente con validaciones robustas y encapsulación
# ==========================================

# La clase Cliente hereda de la clase abstracta EntidadSistema
class Cliente(EntidadSistema):
    # Constructor de la clase
    def __init__(self, identificacion, nombre, correo):
        # Encapsulamos los atributos usando un guion bajo (_)
        self._identificacion = identificacion
        # Inicializamos en None antes de validarlos
        self._nombre = None
        self._correo = None
        
        # Llamamos al método de validación durante la creación del objeto
        self.asignar_datos(nombre, correo)

    # Método para validar e inyectar los datos de forma segura
    def asignar_datos(self, nombre, correo):
        """Uso de try/except/else y encadenamiento de excepciones exigido en la guía."""
        
        # Bloque TRY: Ejecutamos las validaciones lógicas
        try:
            # Verificamos que el nombre no esté vacío y tenga al menos 3 caracteres
            if not nombre or len(nombre.strip()) < 3:
                # Lanzamos nuestra excepción personalizada si falla la condición
                raise DatoInvalidoError("El nombre del cliente debe tener al menos 3 caracteres.")
            
            # Verificamos que el correo contenga el símbolo arroba
            if "@" not in correo:
                # Lanzamos la excepción si el correo es inválido
                raise DatoInvalidoError("El formato del correo electrónico es inválido.")
                
        # Bloque EXCEPT: Atrapamos la excepción personalizada que lanzamos arriba
        except DatoInvalidoError as e:
            # Escribimos el error en el archivo de logs utilizando la clase GestorLogs
            GestorLogs.registrar_evento(f"Fallo de validación para ID {self._identificacion}", e)
            
            # Encadenamiento de excepciones (raise ... from ...): Exigido por el Anexo 3
            # Lanzamos un error grave de operación, manteniendo el rastro del error original (DatoInvalidoError)
            raise OperacionFallidaError("No se pudo registrar el cliente debido a datos corruptos.") from e
            
        # Bloque ELSE: Exigido por la guía. Solo se ejecuta si el bloque TRY fue 100% exitoso
        else:
            # Limpiamos espacios en blanco a los lados y asignamos a los atributos encapsulados
            self._nombre = nombre.strip()
            self._correo = correo.strip()
            # Registramos en el log que el cliente se creó sin problemas
            GestorLogs.registrar_evento(f"Cliente {self._nombre} validado y registrado exitosamente.")
            
    # Sobrescribimos el método abstracto obligatorio (Polimorfismo)
    def obtener_informacion(self):
        # Retornamos una cadena formateada con los datos del cliente
        return f"Cliente: {self._nombre} | ID: {self._identificacion} | Contacto: {self._correo}"

    # Getter: Método público para acceder a la identificación encapsulada
    def get_identificacion(self):
        return self._identificacion


# ==========================================
# 5. SIMULACIÓN Y PRUEBAS SECUENCIALES LOCALES
# Cumplimiento Guía: Ejecutar de forma secuencial cada segmento para validar
# ==========================================

# Este bloque solo se ejecuta si corremos este archivo directamente en Visual Studio Code
if __name__ == "__main__":
    print("Iniciando pruebas del módulo base de Clientes...")
    
    # Prueba 1: Cliente con datos correctos
    try:
        # Instanciamos un cliente válido
        cliente_valido = Cliente("1083919802", "Fabian Muñoz", "fabian@unad.edu.co")
        # Imprimimos la información para verificar que se creó bien
        print("Prueba Exitosa:", cliente_valido.obtener_informacion())
    except Exception as e:
        # Atrapamos cualquier error inesperado
        print(f"Error inesperado en prueba 1: {e}")

    # Prueba 2: Cliente con datos incorrectos para forzar el encadenamiento de excepciones
    try:
        # Instanciamos un cliente con nombre corto y correo sin arroba
        cliente_invalido = Cliente("999999", "A", "correosin_arroba.com")
    # Atrapamos el error de capa superior (OperacionFallidaError)
    except OperacionFallidaError as e:
        print(f"Prueba Fallida (Esperada) - Capturado correctamente: {e}")
        # Accedemos a __cause__ para demostrar el encadenamiento de excepciones exigido
        print(f"Causa original del fallo (Encadenamiento): {e.__cause__}")
        
    print("\nRevisa el archivo 'sistema_errores.log' en tu carpeta para ver los registros.")
