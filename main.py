# -*- coding: utf-8 -*-
# @Author: FABIAN MUÑOZ BOLAÑOS
# @Date:   2026-11-22 9:32:51
# @Last Modified by:   FABIAN MUÑOZ BOLAÑOS
# @Last Modified time: 2026-11-22 11:59:08
# @Description: Archivo principal (main.py) - Simulación integral del sistema Software FJ

# Importamos todos los módulos desarrollados colaborativamente
from clientes import Cliente, OperacionFallidaError, GestorLogs
from servicios import ReservaSala, AlquilerEquipo, Asesoria
from reservas import Reserva
from gestor import GestorSistema, RecursoNoEncontradoError


def ejecutar_simulacion():
    """Ejecuta 12 operaciones completas demostrando estabilidad y tolerancia a fallos."""
    print("=" * 75)
    print("SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ (SIMULACIÓN DE OPERACIONES)")
    print("=" * 75)

    # Inicializamos el gestor en memoria (sin base de datos)
    gestor = GestorSistema()

    # =========================================================================
    # BLOQUE 1: GESTIÓN DE CLIENTES (Operaciones 1 a 3)
    # =========================================================================
    print("\n--- BLOQUE 1: REGISTRO DE CLIENTES ---")

    # OPERACIÓN 1: Registro válido de cliente 1
    try:
        c1 = Cliente("1083919802", "Fabian Muñoz", "fabian@unad.edu.co")
        gestor.registrar_cliente(c1)
        print("[OP 1 - ÉXITO] Cliente registrado:", c1.obtener_informacion())
    except Exception as e:
        print(f"[OP 1 - ERROR INESPERADO]: {e}")

    # OPERACIÓN 2: Registro válido de cliente 2
    try:
        c2 = Cliente("1075234890", "Andrés Camilo González", "andres.gonzalez@unad.edu.co")
        gestor.registrar_cliente(c2)
        print("[OP 2 - ÉXITO] Cliente registrado:", c2.obtener_informacion())
    except Exception as e:
        print(f"[OP 2 - ERROR INESPERADO]: {e}")

    # OPERACIÓN 3: Registro INVÁLIDO de cliente (correo sin @ y duplicado)
    try:
        c_invalido = Cliente("9999999", "Lu", "correo_invalido.com")
        gestor.registrar_cliente(c_invalido)
    except OperacionFallidaError as e:
        print(f"[OP 3 - FALLO CONTROLADO] {e} | Causa: {e.__cause__}")

    # =========================================================================
    # BLOQUE 2: CREACIÓN DE SERVICIOS ESPECIALIZADOS (Operaciones 4 a 7)
    # =========================================================================
    print("\n--- BLOQUE 2: CATÁLOGO DE SERVICIOS ---")

    # OPERACIÓN 4: Creación válida de Reserva de Sala
    try:
        sala_juntas = ReservaSala("SAL-101", "Sala de Juntas Principal", 60000, 25)
        gestor.registrar_servicio(sala_juntas)
        print("[OP 4 - ÉXITO] Servicio creado:", sala_juntas.obtener_informacion())
    except Exception as e:
        print(f"[OP 4 - ERROR INESPERADO]: {e}")

    # OPERACIÓN 5: Creación válida de Alquiler de Equipo
    try:
        servidor_portatil = AlquilerEquipo("EQU-202", "Estación de Trabajo Dell", 45000, "Workstation")
        gestor.registrar_servicio(servidor_portatil)
        print("[OP 5 - ÉXITO] Servicio creado:", servidor_portatil.obtener_informacion())
    except Exception as e:
        print(f"[OP 5 - ERROR INESPERADO]: {e}")

    # OPERACIÓN 6: Creación válida de Asesoría Especializada
    try:
        asesoria_arq = Asesoria("ASE-303", "Arquitectura Cloud", 90000, "Infraestructura", "experto")
        gestor.registrar_servicio(asesoria_arq)
        print("[OP 6 - ÉXITO] Servicio creado:", asesoria_arq.obtener_informacion())
    except Exception as e:
        print(f"[OP 6 - ERROR INESPERADO]: {e}")

    # OPERACIÓN 7: Creación INVÁLIDA de Servicio (tarifa negativa)
    try:
        servicio_roto = ReservaSala("SAL-ERR", "Sala Fantasma", -50000, 10)
        gestor.registrar_servicio(servicio_roto)
    except OperacionFallidaError as e:
        print(f"[OP 7 - FALLO CONTROLADO] {e} | Causa: {e.__cause__}")

    # =========================================================================
    # BLOQUE 3: PROCESAMIENTO DE RESERVAS (Operaciones 8 a 12)
    # =========================================================================
    print("\n--- BLOQUE 3: GESTIÓN Y PROCESAMIENTO DE RESERVAS ---")

    # OPERACIÓN 8: Reserva exitosa de Sala con IVA del 19% (Polimorfismo + Sobrecarga)
    try:
        res_1 = Reserva(c1, sala_juntas, 4)
        res_1.procesar(impuesto=0.19)
        gestor.registrar_reserva(res_1)
        print("[OP 8 - ÉXITO] Reserva procesada:", res_1.obtener_informacion())
    except Exception as e:
        print(f"[OP 8 - ERROR INESPERADO]: {e}")

    # OPERACIÓN 9: Reserva exitosa de Equipo por 8 días (Aplica descuento automático + IVA)
    try:
        res_2 = Reserva(c2, servidor_portatil, 8)
        res_2.procesar(impuesto=0.19, descuento=0.05)
        gestor.registrar_reserva(res_2)
        print("[OP 9 - ÉXITO] Reserva procesada:", res_2.obtener_informacion())
    except Exception as e:
        print(f"[OP 9 - ERROR INESPERADO]: {e}")

    # OPERACIÓN 10: Intento de Reserva INVÁLIDA (Duración excede el máximo de 8h de asesoría)
    try:
        res_invalida = Reserva(c1, asesoria_arq, 15)
        gestor.registrar_reserva(res_invalida)
    except OperacionFallidaError as e:
        print(f"[OP 10 - FALLO CONTROLADO] {e} | Causa: {e.__cause__}")

    # OPERACIÓN 11: Intento de Reserva sobre servicio NO DISPONIBLE
    try:
        asesoria_arq.set_disponible(False)
        res_no_disp = Reserva(c2, asesoria_arq, 2)
        res_no_disp.procesar(impuesto=0.19)
    except OperacionFallidaError as e:
        print(f"[OP 11 - FALLO CONTROLADO] {e} | Causa: {e.__cause__}")
    finally:
        # Restauramos disponibilidad para no afectar futuras operaciones
        asesoria_arq.set_disponible(True)

    # OPERACIÓN 12: Cancelación válida y tentativa de doble cancelación (Operación no permitida)
    try:
        res_1.cancelar("Reprogramación solicitada por el cliente")
        print(f"[OP 12A - ÉXITO] Reserva {res_1.get_codigo()} cancelada correctamente.")
        # Intentamos cancelar nuevamente la misma reserva para forzar excepción
        res_1.cancelar("Segundo intento")
    except OperacionFallidaError as e:
        print(f"[OP 12B - FALLO CONTROLADO] {e} | Causa: {e.__cause__}")

    # =========================================================================
    # RESUMEN FINAL EN MEMORIA
    # =========================================================================
    print("\n" + "=" * 75)
    print("RESUMEN DEL ESTADO EN MEMORIA (SIN BASE DE DATOS)")
    print("=" * 75)
    print(f"Total Clientes activos:  {len(gestor.listar_clientes())}")
    print(f"Total Servicios activos: {len(gestor.listar_servicios())}")
    print(f"Total Reservas en lista: {len(gestor.listar_reservas())}")
    print("\nEl sistema finalizó las 12 operaciones sin detenerse ante los errores.")
    print("Todos los eventos y excepciones quedaron registrados en 'sistema_errores.log'.")
    GestorLogs.registrar_evento("Simulación completa de 12 operaciones finalizada con éxito.")


if __name__ == "__main__":
    ejecutar_simulacion()
