# -*- coding: utf-8 -*-
# @Author: ANDRES CAMILO GONZALEZ MUÑOZ
# @Date: 2026-11-20
# @Description: Módulo de Servicios - Clase abstracta Servicio y servicios especializados (Fase 4)

# Importamos ABC y abstractmethod para definir la clase abstracta Servicio
from abc import abstractmethod

# Reutilizamos la base, las excepciones y el logger del módulo 'clientes.py'
from clientes import EntidadSistema, DatoInvalidoError, OperacionFallidaError, GestorLogs


# ==========================================
# 1. EXCEPCIONES PERSONALIZADAS DE SERVICIOS
# Cumplimiento Anexo 3: servicios no disponibles y cálculos inconsistentes
# ==========================================
class ServicioNoDisponibleError(Exception):
    """Excepción lanzada cuando se intenta usar un servicio marcado como no disponible."""
    pass


class CalculoInconsistenteError(Exception):
    """Excepción lanzada cuando un cálculo de costos produce un resultado imposible."""
    pass


# ==========================================
# 2. CLASE ABSTRACTA SERVICIO
# Cumplimiento Anexo 3: Una clase abstracta Servicio de la que heredan servicios especializados
# ==========================================
class Servicio(EntidadSistema):
    """Plantilla abstracta de cualquier servicio que ofrece Software FJ."""

    def __init__(self, codigo, nombre, tarifa_base, disponible=True):
        # Atributos encapsulados (guion bajo), se llenan tras validar
        self._codigo = None
        self._nombre = None
        self._tarifa_base = None
        self._disponible = bool(disponible)

        # Validamos y asignamos los datos comunes a todos los servicios
        self.asignar_datos(codigo, nombre, tarifa_base)

    # ------------------------------------------
    # Validaciones reutilizables (las usan también las clases hijas)
    # ------------------------------------------
    def _validar_numero_positivo(self, valor, campo, entero=False):
        """Valida que 'valor' sea un número mayor que cero. Encadena la excepción si falla."""
        try:
            tipos = int if entero else (int, float)
            # bool es subclase de int en Python, por eso se excluye de forma explícita
            if isinstance(valor, bool) or not isinstance(valor, tipos) or valor <= 0:
                tipo_texto = "entero" if entero else "número"
                raise DatoInvalidoError(f"El campo '{campo}' debe ser un {tipo_texto} mayor que cero.")
        except DatoInvalidoError as e:
            GestorLogs.registrar_evento(f"Fallo de validación en servicio ('{campo}')", e)
            raise OperacionFallidaError(f"No se pudo crear el servicio: '{campo}' inválido.") from e
        else:
            return valor

    def _validar_texto(self, valor, campo, minimo=3):
        """Valida que 'valor' sea un texto con una longitud mínima. Encadena la excepción si falla."""
        try:
            if not isinstance(valor, str) or len(valor.strip()) < minimo:
                raise DatoInvalidoError(f"El campo '{campo}' debe ser un texto de al menos {minimo} caracteres.")
        except DatoInvalidoError as e:
            GestorLogs.registrar_evento(f"Fallo de validación en servicio ('{campo}')", e)
            raise OperacionFallidaError(f"No se pudo crear el servicio: '{campo}' inválido.") from e
        else:
            return valor.strip()

    def asignar_datos(self, codigo, nombre, tarifa_base):
        """Valida los datos comunes y los asigna usando try/except/else."""
        try:
            codigo = self._validar_texto(codigo, "código", minimo=2)
            nombre = self._validar_texto(nombre, "nombre")
            tarifa_base = self._validar_numero_positivo(tarifa_base, "tarifa base")
        except OperacionFallidaError:
            # Ya fue registrada en el log y encadenada por los validadores, solo la dejamos subir
            raise
        else:
            self._codigo = codigo
            self._nombre = nombre
            self._tarifa_base = tarifa_base
            GestorLogs.registrar_evento(f"Servicio '{self._nombre}' ({self._codigo}) creado correctamente.")

    # ------------------------------------------
    # Getters y estado (Encapsulación)
    # ------------------------------------------
    def get_codigo(self):
        return self._codigo

    def get_nombre(self):
        return self._nombre

    def get_tarifa_base(self):
        return self._tarifa_base

    def esta_disponible(self):
        return self._disponible

    def set_disponible(self, disponible):
        """Cambia la disponibilidad del servicio y deja constancia en el log."""
        self._disponible = bool(disponible)
        estado = "disponible" if self._disponible else "NO disponible"
        GestorLogs.registrar_evento(f"Servicio '{self._nombre}' ahora está {estado}.")

    # ------------------------------------------
    # Métodos abstractos: cada servicio los implementa a su manera (Polimorfismo)
    # ------------------------------------------
    @abstractmethod
    def unidad_duracion(self):
        """Retorna la unidad en la que se mide la duración (horas, días...)."""
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        """Valida la duración solicitada según las reglas propias del servicio."""
        pass

    @abstractmethod
    def calcular_costo_base(self, duracion):
        """Calcula el costo sin impuestos ni descuentos según las reglas propias del servicio."""
        pass

    @abstractmethod
    def describir_servicio(self):
        """Retorna una descripción propia de cada tipo de servicio."""
        pass

    # ------------------------------------------
    # Método SOBRECARGADO (Cumplimiento Anexo 3)
    # Python no tiene sobrecarga real, se simula con parámetros opcionales:
    #   calcular_costo(3)              -> costo base
    #   calcular_costo(3, 0.19)        -> con impuesto
    #   calcular_costo(3, 0.19, 0.10)  -> con impuesto y descuento
    #   calcular_costo(3, descuento=0.10) -> solo con descuento
    # ------------------------------------------
    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        """Calcula el costo final aplicando impuesto y descuento opcionales (fracciones: 0.19 = 19%)."""
        # Cada hija valida la duración a su manera (Polimorfismo)
        self.validar_parametros(duracion)

        if isinstance(impuesto, bool) or not isinstance(impuesto, (int, float)) or not 0 <= impuesto <= 1:
            raise DatoInvalidoError("El impuesto debe ser una fracción entre 0 y 1 (ej. 0.19).")
        if isinstance(descuento, bool) or not isinstance(descuento, (int, float)) or not 0 <= descuento < 1:
            raise DatoInvalidoError("El descuento debe ser una fracción mayor o igual a 0 y menor que 1.")

        subtotal = self.calcular_costo_base(duracion)
        total = subtotal * (1 - descuento) * (1 + impuesto)

        # Si el resultado no es un número positivo, el cálculo es inconsistente
        if total != total or total <= 0:
            raise CalculoInconsistenteError(f"El cálculo de '{self._nombre}' dio un valor inválido: {total}.")
        return round(total, 2)

    # Implementación del método abstracto de EntidadSistema (Polimorfismo)
    def obtener_informacion(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return f"{self.describir_servicio()} | Estado: {estado}"


# ==========================================
# 3. SERVICIOS ESPECIALIZADOS (Herencia + métodos sobrescritos)
# ==========================================

class ReservaSala(Servicio):
    """Reserva de salas. La tarifa base es por HORA."""

    def __init__(self, codigo, nombre, tarifa_base, capacidad, disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        self._capacidad = self._validar_numero_positivo(capacidad, "capacidad", entero=True)

    def get_capacidad(self):
        return self._capacidad

    def unidad_duracion(self):
        return "horas"

    def validar_parametros(self, duracion):
        # Sobrescrito: una sala se reserva entre 1 y 12 horas
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or not 1 <= duracion <= 12:
            raise DatoInvalidoError("Una sala se puede reservar por un mínimo de 1 y un máximo de 12 horas.")

    def calcular_costo_base(self, duracion):
        # Sobrescrito: tarifa por hora, con 15% de recargo en salas grandes (más de 20 personas)
        costo = self._tarifa_base * duracion
        if self._capacidad > 20:
            costo *= 1.15
        return costo

    def describir_servicio(self):
        return (f"Sala '{self._nombre}' ({self._codigo}) | Capacidad: {self._capacidad} personas | "
                f"Tarifa: ${self._tarifa_base:,.0f} por hora")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos. La tarifa base es por DÍA."""

    def __init__(self, codigo, nombre, tarifa_base, tipo_equipo, disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        self._tipo_equipo = self._validar_texto(tipo_equipo, "tipo de equipo")

    def get_tipo_equipo(self):
        return self._tipo_equipo

    def unidad_duracion(self):
        return "días"

    def validar_parametros(self, duracion):
        # Sobrescrito: un equipo se alquila por días completos, entre 1 y 30
        if isinstance(duracion, bool) or not isinstance(duracion, int) or not 1 <= duracion <= 30:
            raise DatoInvalidoError("Un equipo se alquila por días completos: mínimo 1 y máximo 30.")

    def calcular_costo_base(self, duracion):
        # Sobrescrito: tarifa por día, con 10% de descuento si el alquiler es de 7 días o más
        costo = self._tarifa_base * duracion
        if duracion >= 7:
            costo *= 0.90
        return costo

    def describir_servicio(self):
        return (f"Equipo '{self._nombre}' ({self._codigo}) | Tipo: {self._tipo_equipo} | "
                f"Tarifa: ${self._tarifa_base:,.0f} por día")


class Asesoria(Servicio):
    """Asesoría especializada. La tarifa base es por HORA y depende del nivel del asesor."""

    # Multiplicador de la tarifa según el nivel del asesor
    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, codigo, nombre, tarifa_base, especialidad, nivel="junior", disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        self._especialidad = self._validar_texto(especialidad, "especialidad")

        # Validamos el nivel del asesor con try/except y encadenamiento
        try:
            nivel_limpio = str(nivel).strip().lower()
            if nivel_limpio not in self.NIVELES:
                raise DatoInvalidoError(f"Nivel '{nivel}' inválido. Opciones: {', '.join(self.NIVELES)}.")
        except DatoInvalidoError as e:
            GestorLogs.registrar_evento("Fallo de validación en asesoría (nivel)", e)
            raise OperacionFallidaError("No se pudo crear la asesoría: nivel inválido.") from e
        else:
            self._nivel = nivel_limpio

    def get_especialidad(self):
        return self._especialidad

    def unidad_duracion(self):
        return "horas"

    def validar_parametros(self, duracion):
        # Sobrescrito: una asesoría dura entre 1 y 8 horas
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or not 1 <= duracion <= 8:
            raise DatoInvalidoError("Una asesoría debe durar entre 1 y 8 horas.")

    def calcular_costo_base(self, duracion):
        # Sobrescrito: tarifa por hora multiplicada por el nivel del asesor
        return self._tarifa_base * duracion * self.NIVELES[self._nivel]

    def describir_servicio(self):
        return (f"Asesoría '{self._nombre}' ({self._codigo}) | Especialidad: {self._especialidad} | "
                f"Nivel: {self._nivel} | Tarifa: ${self._tarifa_base:,.0f} por hora")


# ==========================================
# 4. SIMULACIÓN Y PRUEBAS SECUENCIALES LOCALES
# ==========================================
if __name__ == "__main__":
    print("Iniciando pruebas del módulo de Servicios...\n")

    # Prueba 1: creación válida de los tres servicios y polimorfismo
    try:
        sala = ReservaSala("SAL-01", "Sala Ejecutiva", 50000, 10)
        equipo = AlquilerEquipo("EQU-01", "Portátil Gamer", 30000, "Computador")
        asesoria = Asesoria("ASE-01", "Asesoría en Python", 80000, "Programación", "senior")
        print("Prueba 1 Exitosa - Polimorfismo (obtener_informacion):")
        for s in (sala, equipo, asesoria):
            print("  -", s.obtener_informacion())
    except Exception as e:
        print(f"Error inesperado en prueba 1: {e}")

    # Prueba 2: método sobrecargado con distintas variantes de parámetros
    try:
        print("\nPrueba 2 Exitosa - calcular_costo sobrecargado (sala, 3 horas):")
        print("  Solo base:            ", sala.calcular_costo(3))
        print("  Con IVA 19%:          ", sala.calcular_costo(3, 0.19))
        print("  Con IVA y desc. 10%:  ", sala.calcular_costo(3, 0.19, 0.10))
        print("  Solo descuento 10%:   ", sala.calcular_costo(3, descuento=0.10))
        print("  Equipo 7 días (desc. automático):", equipo.calcular_costo(7))
        print("  Asesoría senior 2 h:  ", asesoria.calcular_costo(2))
    except Exception as e:
        print(f"Error inesperado en prueba 2: {e}")

    # Prueba 3: tarifa inválida (Debe fallar y encadenar la excepción)
    try:
        ReservaSala("SAL-02", "Sala Rota", -100, 5)
    except OperacionFallidaError as e:
        print(f"\nPrueba 3 Fallida (Esperada - Tarifa): {e}")
        print(f"  Causa original: {e.__cause__}")

    # Prueba 4: duración fuera de rango
    try:
        sala.calcular_costo(50)
    except DatoInvalidoError as e:
        print(f"\nPrueba 4 Fallida (Esperada - Duración): {e}")

    # Prueba 5: nivel de asesor inválido
    try:
        Asesoria("ASE-02", "Asesoría Falsa", 80000, "Redes", "gurú")
    except OperacionFallidaError as e:
        print(f"\nPrueba 5 Fallida (Esperada - Nivel): {e}")
        print(f"  Causa original: {e.__cause__}")

    # Prueba 6: descuento imposible
    try:
        equipo.calcular_costo(2, descuento=1.5)
    except DatoInvalidoError as e:
        print(f"\nPrueba 6 Fallida (Esperada - Descuento): {e}")

    print("\nValidación completada. Revisa 'sistema_errores.log'.")
