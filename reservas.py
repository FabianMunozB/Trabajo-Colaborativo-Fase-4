# -*- coding: utf-8 -*-
# @Author: ANDRES CAMILO GONZALEZ MUÑOZ
# @Date: 2026-11-21
# @Description: Módulo de Reservas - Integra cliente, servicio, duración y estado (Fase 4)

# Reutilizamos la base, las excepciones y el logger del módulo 'clientes.py'
from clientes import Cliente, EntidadSistema, DatoInvalidoError, OperacionFallidaError, GestorLogs
# Importamos los servicios y sus excepciones desde 'servicios.py'
from servicios import (Servicio, ReservaSala, AlquilerEquipo, Asesoria,
                       ServicioNoDisponibleError, CalculoInconsistenteError)


# ==========================================
# 1. EXCEPCIÓN PERSONALIZADA DE RESERVAS
# Cumplimiento Anexo 3: operaciones no permitidas
# ==========================================
class OperacionNoPermitidaError(Exception):
    """Excepción lanzada cuando se intenta un cambio de estado que no corresponde."""
    pass


# ==========================================
# 2. CLASE RESERVA
# Cumplimiento Anexo 3: integra cliente, servicio, duración y estado;
# implementa confirmación, cancelación y procesamiento con manejo de excepciones
# ==========================================
class Reserva(EntidadSistema):
    # Estados posibles de una reserva
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"

    # Contador compartido para generar códigos únicos (RES-001, RES-002...)
    _contador = 0

    def __init__(self, cliente, servicio, duracion):
        """Valida los datos de la reserva con try/except/else y encadenamiento de excepciones."""
        try:
            # Validación 1: el cliente debe ser una instancia de Cliente
            if not isinstance(cliente, Cliente):
                raise DatoInvalidoError("La reserva requiere un Cliente válido.")
            # Validación 2: el servicio debe ser una instancia de Servicio
            if not isinstance(servicio, Servicio):
                raise DatoInvalidoError("La reserva requiere un Servicio válido.")
            # Validación 3: la duración se valida con las reglas propias del servicio (Polimorfismo)
            servicio.validar_parametros(duracion)

        except DatoInvalidoError as e:
            GestorLogs.registrar_evento("Intento de reserva incorrecto", e)
            raise OperacionFallidaError("No se pudo crear la reserva por datos inválidos.") from e

        else:
            # Solo si todo salió bien se asignan los atributos encapsulados
            Reserva._contador += 1
            self._codigo = f"RES-{Reserva._contador:03d}"
            self._cliente = cliente
            self._servicio = servicio
            self._duracion = duracion
            self._estado = Reserva.PENDIENTE
            self._total = None
            GestorLogs.registrar_evento(
                f"Reserva {self._codigo} creada: cliente {cliente.get_identificacion()} "
                f"- servicio '{servicio.get_nombre()}' - {duracion} {servicio.unidad_duracion()}.")

    # ------------------------------------------
    # Getters (Encapsulación)
    # ------------------------------------------
    def get_codigo(self):
        return self._codigo

    def get_estado(self):
        return self._estado

    def get_total(self):
        return self._total

    def get_cliente(self):
        return self._cliente

    def get_servicio(self):
        return self._servicio

    # ------------------------------------------
    # Confirmación
    # ------------------------------------------
    def confirmar(self):
        """Confirma la reserva si está pendiente y el servicio sigue disponible."""
        try:
            if self._estado != Reserva.PENDIENTE:
                raise OperacionNoPermitidaError(
                    f"No se puede confirmar la reserva {self._codigo}: está {self._estado}.")
            if not self._servicio.esta_disponible():
                raise ServicioNoDisponibleError(
                    f"El servicio '{self._servicio.get_nombre()}' no está disponible.")

        except (OperacionNoPermitidaError, ServicioNoDisponibleError) as e:
            GestorLogs.registrar_evento(f"Confirmación fallida de {self._codigo}", e)
            raise OperacionFallidaError(f"No se pudo confirmar la reserva {self._codigo}.") from e

        else:
            self._estado = Reserva.CONFIRMADA
            GestorLogs.registrar_evento(f"Reserva {self._codigo} confirmada.")

    # ------------------------------------------
    # Cancelación
    # ------------------------------------------
    def cancelar(self, motivo="Sin motivo especificado"):
        """Cancela la reserva si no estaba ya cancelada."""
        try:
            if self._estado == Reserva.CANCELADA:
                raise OperacionNoPermitidaError(f"La reserva {self._codigo} ya estaba cancelada.")

        except OperacionNoPermitidaError as e:
            GestorLogs.registrar_evento(f"Cancelación fallida de {self._codigo}", e)
            raise OperacionFallidaError(f"No se pudo cancelar la reserva {self._codigo}.") from e

        else:
            self._estado = Reserva.CANCELADA
            GestorLogs.registrar_evento(f"Reserva {self._codigo} cancelada. Motivo: {motivo}")

    # ------------------------------------------
    # Procesamiento (try/except/else/finally + encadenamiento)
    # ------------------------------------------
    def procesar(self, impuesto=0.0, descuento=0.0):
        """Calcula el costo y confirma la reserva. Retorna el total.

        Usa los parámetros opcionales del método sobrecargado calcular_costo()."""
        try:
            # Paso 1: revalidamos la duración y calculamos el costo (puede lanzar varios errores)
            self._servicio.validar_parametros(self._duracion)
            total = self._servicio.calcular_costo(self._duracion, impuesto, descuento)
            # Paso 2: confirmamos (verifica estado y disponibilidad)
            self.confirmar()

        except (DatoInvalidoError, CalculoInconsistenteError, OperacionFallidaError) as e:
            GestorLogs.registrar_evento(f"Procesamiento fallido de {self._codigo}", e)
            # Encadenamiento: el error original queda disponible en __cause__
            raise OperacionFallidaError(f"No se pudo procesar la reserva {self._codigo}.") from e

        else:
            # Solo si todo el TRY fue exitoso guardamos el total
            self._total = total
            GestorLogs.registrar_evento(f"Reserva {self._codigo} procesada. Total: ${total:,.2f}")
            return total

        finally:
            # Se ejecuta SIEMPRE, haya habido error o no
            GestorLogs.registrar_evento(f"Fin del procesamiento de la reserva {self._codigo}.")

    # Implementación del método abstracto de EntidadSistema (Polimorfismo)
    def obtener_informacion(self):
        total = f"${self._total:,.2f}" if self._total is not None else "Sin calcular"
        return (f"Reserva {self._codigo} | {self._cliente.obtener_informacion()} | "
                f"Servicio: {self._servicio.get_nombre()} | "
                f"Duración: {self._duracion} {self._servicio.unidad_duracion()} | "
                f"Estado: {self._estado} | Total: {total}")


# ==========================================
# 3. SIMULACIÓN Y PRUEBAS SECUENCIALES LOCALES
# ==========================================
if __name__ == "__main__":
    print("Iniciando pruebas del módulo de Reservas...\n")

    cliente = Cliente("1083919802", "Fabian Muñoz", "fabian@unad.edu.co")
    sala = ReservaSala("SAL-01", "Sala Ejecutiva", 50000, 10)
    equipo = AlquilerEquipo("EQU-01", "Portátil Gamer", 30000, "Computador")
    asesoria = Asesoria("ASE-01", "Asesoría en Python", 80000, "Programación", "senior")

    # Prueba 1: reserva exitosa procesada con IVA
    try:
        r1 = Reserva(cliente, sala, 3)
        r1.procesar(impuesto=0.19)
        print("Prueba 1 Exitosa:", r1.obtener_informacion())
    except Exception as e:
        print(f"Error inesperado en prueba 1: {e}")

    # Prueba 2: duración inválida al crear la reserva
    try:
        Reserva(cliente, equipo, 100)
    except OperacionFallidaError as e:
        print(f"\nPrueba 2 Fallida (Esperada - Duración): {e}")
        print(f"  Causa original: {e.__cause__}")

    # Prueba 3: cliente inválido
    try:
        Reserva("no soy un cliente", sala, 2)
    except OperacionFallidaError as e:
        print(f"\nPrueba 3 Fallida (Esperada - Cliente): {e}")
        print(f"  Causa original: {e.__cause__}")

    # Prueba 4: servicio no disponible
    try:
        equipo.set_disponible(False)
        r4 = Reserva(cliente, equipo, 5)
        r4.procesar()
    except OperacionFallidaError as e:
        print(f"\nPrueba 4 Fallida (Esperada - No disponible): {e}")
        print(f"  Causa original: {e.__cause__}")
        print(f"  Causa más profunda: {e.__cause__.__cause__}")
    finally:
        equipo.set_disponible(True)

    # Prueba 5: confirmar dos veces la misma reserva
    try:
        r1.confirmar()
    except OperacionFallidaError as e:
        print(f"\nPrueba 5 Fallida (Esperada - Ya confirmada): {e}")
        print(f"  Causa original: {e.__cause__}")

    # Prueba 6: cancelar y luego intentar cancelar de nuevo
    try:
        r1.cancelar("El cliente cambió de planes")
        print(f"\nPrueba 6 Exitosa - Estado tras cancelar: {r1.get_estado()}")
        r1.cancelar()
    except OperacionFallidaError as e:
        print(f"  Segundo intento (Esperado): {e}")
        print(f"  Causa original: {e.__cause__}")

    # Prueba 7: procesar con descuento inválido
    try:
        r7 = Reserva(cliente, asesoria, 2)
        r7.procesar(descuento=2)
    except OperacionFallidaError as e:
        print(f"\nPrueba 7 Fallida (Esperada - Descuento): {e}")
        print(f"  Causa original: {e.__cause__}")

    # Prueba 8: la reserva r7 sigue pendiente y puede procesarse bien después
    try:
        total = r7.procesar(impuesto=0.19, descuento=0.10)
        print(f"\nPrueba 8 Exitosa - El sistema sigue estable: {r7.obtener_informacion()}")
    except Exception as e:
        print(f"Error inesperado en prueba 8: {e}")

    print("\nValidación completada. Revisa 'sistema_errores.log'.")
