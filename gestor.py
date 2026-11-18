# -*- coding: utf-8 -*-
# @Author: FABIAN MUÑOZ BOLAÑOS
# @Date:   2026-11-18 18:00:12
# @Last Modified by:   FABIAN MUÑOZ BOLAÑOS
# @Last Modified time: 2026-11-18 18:00:32

# Importamos las clases y excepciones desde nuestro módulo base 'clientes.py'
from clientes import Cliente, DatoInvalidoError, OperacionFallidaError, GestorLogs

# ==========================================
# EXCEPCIÓN PERSONALIZADA DEL GESTOR
# Cumplimiento Anexo 3: Manejo robusto de excepciones personalizadas
# ==========================================
class RecursoNoEncontradoError(Exception):
    """Excepción lanzada cuando se busca un cliente, servicio o reserva que no existe en las listas."""
    pass


# ==========================================
# CLASE GESTORSISTEMA (Repositorio en Memoria)
# Cumplimiento Anexo 3: Gestión mediante objetos y listas internas sin base de datos
# ==========================================
class GestorSistema:
    def __init__(self):
        # Encapsulamos las listas internas (guion bajo) que simularán nuestra base de datos en RAM
        self._lista_clientes = []
        self._lista_servicios = []
        self._lista_reservas = []
        
        # Registramos el inicio del gestor en el archivo de logs
        GestorLogs.registrar_evento("GestorSistema inicializado en memoria correctamente.")

    # ------------------------------------------
    # 1. GESTIÓN DE CLIENTES
    # ------------------------------------------
    def registrar_cliente(self, cliente):
        """Valida e inserta un objeto Cliente en la lista interna usando try/except/else."""
        try:
            # Validación 1: Verificar que el objeto recibido sea realmente una instancia de Cliente
            if not isinstance(cliente, Cliente):
                raise DatoInvalidoError("El objeto proporcionado no corresponde a un Cliente válido.")

            # Validación 2: Evitar clientes duplicados recorriendo la lista interna por identificación
            for c in self._lista_clientes:
                if c.get_identificacion() == cliente.get_identificacion():
                    raise DatoInvalidoError(f"Ya existe un cliente registrado con el ID {cliente.get_identificacion()}.")

        except DatoInvalidoError as e:
            # Registramos la advertencia o error en el archivo de logs
            GestorLogs.registrar_evento("Error al intentar almacenar cliente en GestorSistema", e)
            # Encadenamos la excepción para notificar a la capa superior sin perder el rastro original
            raise OperacionFallidaError("No se pudo completar el registro del cliente en el sistema.") from e

        else:
            # Bloque ELSE: Solo se ejecuta si las validaciones del TRY pasaron sin errores
            self._lista_clientes.append(cliente)
            GestorLogs.registrar_evento(f"Cliente ID {cliente.get_identificacion()} almacenado en lista interna.")

    def buscar_cliente(self, identificacion):
        """Busca un cliente por su ID y lanza excepción controlada si no existe."""
        try:
            # Recorremos la lista de clientes buscando coincidencia exacta
            for cliente in self._lista_clientes:
                if cliente.get_identificacion() == identificacion:
                    return cliente
            
            # Si termina el ciclo y no lo encuentra, lanzamos nuestra excepción personalizada
            raise RecursoNoEncontradoError(f"No se encontró ningún cliente con identificación '{identificacion}'.")
            
        except RecursoNoEncontradoError as e:
            # Documentamos la búsqueda fallida en el log y relanzamos el error
            GestorLogs.registrar_evento("Búsqueda de cliente sin resultados", e)
            raise

    def listar_clientes(self):
        """Retorna una lista con la información formateada de todos los clientes registrados."""
        # Uso de polimorfismo llamando a obtener_informacion() de cada objeto
        return [cliente.obtener_informacion() for cliente in self._lista_clientes]

    # ------------------------------------------
    # 2. GESTIÓN DE SERVICIOS (Preparado para integrar con servicios.py)
    # ------------------------------------------
    def registrar_servicio(self, servicio):
        """Almacena un objeto de tipo Servicio en la lista interna."""
        try:
            # Validamos que el objeto no sea nulo antes de guardarlo
            if servicio is None:
                raise DatoInvalidoError("No se puede registrar un servicio nulo o vacío.")
                
        except DatoInvalidoError as e:
            GestorLogs.registrar_evento("Fallo al registrar servicio en memoria", e)
            raise OperacionFallidaError("Error de integridad al guardar el servicio.") from e
            
        else:
            self._lista_servicios.append(servicio)
            GestorLogs.registrar_evento("Servicio almacenado exitosamente en lista interna.")

    def listar_servicios(self):
        """Retorna la lista de objetos de servicios almacenados."""
        return self._lista_servicios

    # ------------------------------------------
    # 3. GESTIÓN DE RESERVAS (Preparado para integrar con reservas.py)
    # ------------------------------------------
    def registrar_reserva(self, reserva):
        """Almacena un objeto de tipo Reserva en la lista interna."""
        try:
            # Validamos que la reserva no sea nula
            if reserva is None:
                raise DatoInvalidoError("No se puede registrar una reserva nula o vacía.")
                
        except DatoInvalidoError as e:
            GestorLogs.registrar_evento("Fallo al registrar reserva en memoria", e)
            raise OperacionFallidaError("Error de integridad al guardar la reserva.") from e
            
        else:
            self._lista_reservas.append(reserva)
            GestorLogs.registrar_evento("Reserva almacenada exitosamente en lista interna.")

    def listar_reservas(self):
        """Retorna la lista de objetos de reservas almacenados."""
        return self._lista_reservas


# ==========================================
# 4. SIMULACIÓN Y PRUEBAS SECUENCIALES LOCALES
# Cumplimiento Guía: Ejecutar de forma secuencial cada segmento para validar
# ==========================================
if __name__ == "__main__":
    print("Iniciando pruebas del módulo GestorSistema (Almacenamiento en Memoria)...")
    
    # Instanciamos el gestor
    gestor = GestorSistema()

    # Prueba 1: Registro exitoso de un cliente en memoria
    try:
        cliente_1 = Cliente("1083919802", "Fabian Muñoz", "fabian@unad.edu.co")
        gestor.registrar_cliente(cliente_1)
        print("Prueba 1 Exitosa - Clientes en memoria:", gestor.listar_clientes())
    except Exception as e:
        print(f"Error inesperado en Prueba 1: {e}")

    # Prueba 2: Intento de registrar cliente duplicado (Debe fallar y encadenar error)
    try:
        cliente_duplicado = Cliente("1083919802", "Fabian Clon", "otro@unad.edu.co")
        gestor.registrar_cliente(cliente_duplicado)
    except OperacionFallidaError as e:
        print(f"Prueba 2 Fallida (Esperada - Duplicado): {e}")
        print(f"Causa original del fallo: {e.__cause__}")

    # Prueba 3: Búsqueda de un cliente inexistente (Debe lanzar RecursoNoEncontradoError)
    try:
        gestor.buscar_cliente("00000000")
    except RecursoNoEncontradoError as e:
        print(f"Prueba 3 Fallida (Esperada - Búsqueda): {e}")

    print("\nValidación completada. Verifica los nuevos registros en 'sistema_errores.log'.")
