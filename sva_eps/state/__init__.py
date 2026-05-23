import reflex as rx
from typing import Optional
from ..models import ExpedienteSolicitud, EstadoExpediente, TipoPrograma, NivelEducativo
from ..services import consultar_renapo, consultar_sat, agregar_curp_lista_negra

EDAD_MINIMA_ADULTO_MAYOR = 65
UMBRAL_BIOMETRICO_APROBACION = 80.0
UMBRAL_BIOMETRICO_REVISION = 60.0

MONTO_ADULTOS_MAYORES = 6000.0
MONTO_BASE_RITA_CETINA = 1900.0
MONTO_EXTRA_ESTUDIANTE_RITA_CETINA = 700.0
MONTO_MEDIA_SUPERIOR = 920.0
MONTO_SUPERIOR = 2800.0

CURPS_REGISTRADAS: set[str] = set()

PROGRAMAS_OPCIONES = [
    TipoPrograma.ADULTOS_MAYORES,
    TipoPrograma.BECA_RITA_CETINA,
    TipoPrograma.BECA_MEDIA_SUPERIOR,
    TipoPrograma.BECA_SUPERIOR,
]


class AppState(rx.State):
    expedientes: list[dict] = []

    curp_input: str = ""
    rfc_input: str = ""
    nombre_input: str = ""
    edad_input: str = ""
    cp_input: str = ""
    puntaje_biometrico_input: str = ""
    tipo_programa_input: str = TipoPrograma.ADULTOS_MAYORES
    nivel_educativo_input: str = NivelEducativo.SECUNDARIA
    estudiantes_adicionales_input: str = "0"

    procesando: bool = False
    mensaje_resultado: str = ""
    tipo_mensaje: str = ""

    filtro_estado: str = "Todos"

    @rx.var
    def es_programa_educativo(self) -> bool:
        return self.tipo_programa_input in [
            TipoPrograma.BECA_RITA_CETINA,
            TipoPrograma.BECA_MEDIA_SUPERIOR,
            TipoPrograma.BECA_SUPERIOR,
        ]

    @rx.var
    def es_rita_cetina(self) -> bool:
        return self.tipo_programa_input == TipoPrograma.BECA_RITA_CETINA

    @rx.var
    def niveles_educativos_permitidos(self) -> list[str]:
        """Devuelve solo los niveles válidos según el programa seleccionado."""
        if self.tipo_programa_input == TipoPrograma.BECA_RITA_CETINA:
            return [NivelEducativo.PRIMARIA, NivelEducativo.SECUNDARIA]
        elif self.tipo_programa_input == TipoPrograma.BECA_MEDIA_SUPERIOR:
            return [NivelEducativo.PREPARATORIA]
        elif self.tipo_programa_input == TipoPrograma.BECA_SUPERIOR:
            return [NivelEducativo.UNIVERSIDAD]
        return []

    @rx.var
    def expedientes_filtrados(self) -> list[dict]:
        if self.filtro_estado == "Todos":
            return self.expedientes
        return [e for e in self.expedientes if e["estado"] == self.filtro_estado]

    @rx.var
    def total_aprobados(self) -> int:
        return sum(1 for e in self.expedientes if e["estado"] == EstadoExpediente.APROBADO_AUTOMATICO)

    @rx.var
    def total_rechazados(self) -> int:
        return sum(1 for e in self.expedientes if e["estado"] == EstadoExpediente.RECHAZADO_AUTOMATICO)

    @rx.var
    def total_revision(self) -> int:
        return sum(1 for e in self.expedientes if e["estado"] == EstadoExpediente.PENDIENTE_REVISION)

    @rx.var
    def monto_total_comprometido(self) -> float:
        return sum(e.get("monto_asignado", 0.0) for e in self.expedientes if e["estado"] == EstadoExpediente.APROBADO_AUTOMATICO)

    # --- Setters explícitos (Reflex 0.9+ ya no autogenera set_*) ---
    def set_curp_input(self, valor: str):
        self.curp_input = valor

    def set_rfc_input(self, valor: str):
        self.rfc_input = valor

    def set_nombre_input(self, valor: str):
        self.nombre_input = valor

    def set_edad_input(self, valor: str):
        self.edad_input = valor

    def set_cp_input(self, valor: str):
        self.cp_input = valor

    def set_puntaje_biometrico_input(self, valor: str):
        self.puntaje_biometrico_input = valor

    def set_nivel_educativo_input(self, valor: str):
        self.nivel_educativo_input = valor

    def set_estudiantes_adicionales_input(self, valor: str):
        self.estudiantes_adicionales_input = valor

    def set_filtro(self, valor: str):
        self.filtro_estado = valor

    def set_tipo_programa_input(self, valor: str):
        self.tipo_programa_input = valor
        self.estudiantes_adicionales_input = "0"
        # Ajustar nivel educativo al primer nivel válido del programa
        if valor == TipoPrograma.BECA_RITA_CETINA:
            self.nivel_educativo_input = NivelEducativo.PRIMARIA
        elif valor == TipoPrograma.BECA_MEDIA_SUPERIOR:
            self.nivel_educativo_input = NivelEducativo.PREPARATORIA
        elif valor == TipoPrograma.BECA_SUPERIOR:
            self.nivel_educativo_input = NivelEducativo.UNIVERSIDAD
        else:
            self.nivel_educativo_input = NivelEducativo.SECUNDARIA

    def _validar_curp(self, curp: str) -> Optional[str]:
        if len(curp) != 18:
            return "CURP debe tener exactamente 18 caracteres."
        if curp in CURPS_REGISTRADAS:
            return "Esta CURP ya tiene un expediente registrado en este programa."
        return None

    def _validar_rfc(self, rfc: str) -> Optional[str]:
        if len(rfc) != 13:
            return "RFC debe tener exactamente 13 caracteres."
        return None

    def _calcular_edad_desde_curp(self, curp: str) -> Optional[int]:
        try:
            anio_str = curp[4:6]
            anio = int(anio_str)
            anio_completo = 2000 + anio if anio <= 25 else 1900 + anio
            from datetime import date
            hoy = date.today()
            return hoy.year - anio_completo
        except Exception:
            return None

    def _calcular_monto(self, expediente: ExpedienteSolicitud) -> float:
        if expediente.tipo_programa == TipoPrograma.ADULTOS_MAYORES:
            return MONTO_ADULTOS_MAYORES
        if expediente.tipo_programa == TipoPrograma.BECA_RITA_CETINA:
            return MONTO_BASE_RITA_CETINA + (expediente.estudiantes_adicionales * MONTO_EXTRA_ESTUDIANTE_RITA_CETINA)
        if expediente.tipo_programa == TipoPrograma.BECA_MEDIA_SUPERIOR:
            return MONTO_MEDIA_SUPERIOR
        if expediente.tipo_programa == TipoPrograma.BECA_SUPERIOR:
            return MONTO_SUPERIOR
        return 0.0

    def _ejecutar_motor_reglas(self, expediente: ExpedienteSolicitud) -> tuple[str, str, float]:
        renapo = consultar_renapo(expediente.curp)
        if renapo["baja_por_defuncion"]:
            agregar_curp_lista_negra(expediente.curp)
            return (
                EstadoExpediente.RECHAZADO_AUTOMATICO,
                "Identidad inválida: el registro de RENAPO indica baja por defunción. CURP bloqueada.",
                0.0,
            )

        sat = consultar_sat(expediente.rfc)
        if sat["estatus_fiscal"] != "Activo":
            return (
                EstadoExpediente.PENDIENTE_REVISION,
                "Situación fiscal no activa ante el SAT. Requiere revisión manual.",
                0.0,
            )

        if expediente.puntaje_biometrico < UMBRAL_BIOMETRICO_REVISION:
            return (
                EstadoExpediente.RECHAZADO_AUTOMATICO,
                f"Alerta de fraude: puntaje biométrico de {expediente.puntaje_biometrico:.1f}% es inferior al umbral mínimo del 60%.",
                0.0,
            )

        if expediente.puntaje_biometrico < UMBRAL_BIOMETRICO_APROBACION:
            return (
                EstadoExpediente.PENDIENTE_REVISION,
                f"Puntaje biométrico de {expediente.puntaje_biometrico:.1f}% requiere verificación manual (umbral: 80%).",
                0.0,
            )

        if expediente.tipo_programa == TipoPrograma.ADULTOS_MAYORES:
            edad_curp = self._calcular_edad_desde_curp(expediente.curp)
            if edad_curp is not None and edad_curp < EDAD_MINIMA_ADULTO_MAYOR:
                return (
                    EstadoExpediente.RECHAZADO_AUTOMATICO,
                    f"El solicitante no cumple la edad mínima de {EDAD_MINIMA_ADULTO_MAYOR} años (edad calculada desde CURP: {edad_curp}).",
                    0.0,
                )

        if expediente.tipo_programa == TipoPrograma.BECA_RITA_CETINA:
            if expediente.nivel_educativo not in [NivelEducativo.PRIMARIA, NivelEducativo.SECUNDARIA]:
                return (
                    EstadoExpediente.RECHAZADO_AUTOMATICO,
                    f"La Beca Rita Cetina requiere nivel educativo 'Primaria' o 'Secundaria'. Nivel registrado: '{expediente.nivel_educativo}'.",
                    0.0,
                )

        if expediente.tipo_programa == TipoPrograma.BECA_MEDIA_SUPERIOR:
            if expediente.nivel_educativo != NivelEducativo.PREPARATORIA:
                return (
                    EstadoExpediente.RECHAZADO_AUTOMATICO,
                    f"La Beca Media Superior requiere nivel 'Preparatoria/Bachillerato'. Nivel registrado: '{expediente.nivel_educativo}'.",
                    0.0,
                )

        if expediente.tipo_programa == TipoPrograma.BECA_SUPERIOR:
            if expediente.nivel_educativo != NivelEducativo.UNIVERSIDAD:
                return (
                    EstadoExpediente.RECHAZADO_AUTOMATICO,
                    f"La Beca Superior requiere nivel educativo 'Universidad'. Nivel registrado: '{expediente.nivel_educativo}'.",
                    0.0,
                )

        monto = self._calcular_monto(expediente)
        monto_fmt = f"${monto:,.0f}"

        if expediente.tipo_programa == TipoPrograma.BECA_RITA_CETINA and expediente.estudiantes_adicionales > 0:
            motivo = (
                f"Expediente aprobado automáticamente para {expediente.tipo_programa}. "
                f"Monto asignado: {monto_fmt} bimestrales "
                f"(base ${MONTO_BASE_RITA_CETINA:,.0f} + {expediente.estudiantes_adicionales} "
                f"estudiante(s) adicional(es) × ${MONTO_EXTRA_ESTUDIANTE_RITA_CETINA:,.0f})."
            )
        else:
            periodicidad = "bimestrales" if expediente.tipo_programa in [
                TipoPrograma.ADULTOS_MAYORES, TipoPrograma.BECA_RITA_CETINA
            ] else "mensuales"
            motivo = (
                f"Expediente aprobado automáticamente para {expediente.tipo_programa}. "
                f"Monto asignado: {monto_fmt} {periodicidad}."
            )

        return (EstadoExpediente.APROBADO_AUTOMATICO, motivo, monto)

    def registrar_cobro(self, folio: str):
        """Marca el periodo actual como cobrado para un expediente aprobado."""
        for i, exp in enumerate(self.expedientes):
            if exp["folio"] == folio and exp["estado"] == EstadoExpediente.APROBADO_AUTOMATICO:
                self.expedientes[i] = {**exp, "cobro_registrado": True}

    def desmarcar_cobro(self, folio: str):
        """Desmarca el cobro para reiniciar en nuevo periodo."""
        for i, exp in enumerate(self.expedientes):
            if exp["folio"] == folio:
                self.expedientes[i] = {**exp, "cobro_registrado": False}

    def aprobar_manual(self, folio: str):
        for i, exp in enumerate(self.expedientes):
            if exp["folio"] == folio and exp["estado"] == EstadoExpediente.PENDIENTE_REVISION:
                self.expedientes[i] = {
                    **exp,
                    "estado": EstadoExpediente.APROBADO_AUTOMATICO,
                    "motivo_dictamen": exp["motivo_dictamen"] + " | Aprobado manualmente por operador.",
                }

    def rechazar_manual(self, folio: str):
        for i, exp in enumerate(self.expedientes):
            if exp["folio"] == folio and exp["estado"] == EstadoExpediente.PENDIENTE_REVISION:
                self.expedientes[i] = {
                    **exp,
                    "estado": EstadoExpediente.RECHAZADO_AUTOMATICO,
                    "motivo_dictamen": exp["motivo_dictamen"] + " | Rechazado manualmente por operador.",
                }

    def procesar_expediente(self):
        self.procesando = True
        self.mensaje_resultado = ""

        error_curp = self._validar_curp(self.curp_input.upper())
        if error_curp:
            self.mensaje_resultado = error_curp
            self.tipo_mensaje = "error"
            self.procesando = False
            return

        error_rfc = self._validar_rfc(self.rfc_input.upper())
        if error_rfc:
            self.mensaje_resultado = error_rfc
            self.tipo_mensaje = "error"
            self.procesando = False
            return

        if not self.nombre_input.strip():
            self.mensaje_resultado = "El nombre completo es obligatorio."
            self.tipo_mensaje = "error"
            self.procesando = False
            return

        try:
            edad = int(self.edad_input)
            puntaje = float(self.puntaje_biometrico_input)
        except ValueError:
            self.mensaje_resultado = "Edad y puntaje biométrico deben ser valores numéricos."
            self.tipo_mensaje = "error"
            self.procesando = False
            return

        try:
            estudiantes_adicionales = int(self.estudiantes_adicionales_input or "0")
        except ValueError:
            estudiantes_adicionales = 0

        expediente = ExpedienteSolicitud(
            curp=self.curp_input.upper(),
            rfc=self.rfc_input.upper(),
            nombre=self.nombre_input.strip(),
            edad=edad,
            codigo_postal=self.cp_input.strip(),
            puntaje_biometrico=puntaje,
            tipo_programa=self.tipo_programa_input,
            nivel_educativo=self.nivel_educativo_input,
            estudiantes_adicionales=estudiantes_adicionales,
        )

        estado, motivo, monto = self._ejecutar_motor_reglas(expediente)
        expediente.estado = estado
        expediente.motivo_dictamen = motivo
        expediente.monto_asignado = monto

        if estado != EstadoExpediente.RECHAZADO_AUTOMATICO:
            CURPS_REGISTRADAS.add(expediente.curp)

        self.expedientes.append({
            "folio": expediente.folio,
            "nombre": expediente.nombre,
            "curp": expediente.curp,
            "rfc": expediente.rfc,
            "fecha_creacion": expediente.fecha_creacion,
            "estado": expediente.estado,
            "motivo_dictamen": expediente.motivo_dictamen,
            "puntaje_biometrico": expediente.puntaje_biometrico,
            "tipo_programa": expediente.tipo_programa,
            "nivel_educativo": expediente.nivel_educativo,
            "estudiantes_adicionales": expediente.estudiantes_adicionales,
            "monto_asignado": expediente.monto_asignado,
            "cobro_registrado": False,
        })

        self.mensaje_resultado = motivo
        self.tipo_mensaje = "success" if estado == EstadoExpediente.APROBADO_AUTOMATICO else (
            "warning" if estado == EstadoExpediente.PENDIENTE_REVISION else "error"
        )

        self.curp_input = ""
        self.rfc_input = ""
        self.nombre_input = ""
        self.edad_input = ""
        self.cp_input = ""
        self.puntaje_biometrico_input = ""
        self.tipo_programa_input = TipoPrograma.ADULTOS_MAYORES
        self.nivel_educativo_input = NivelEducativo.SECUNDARIA
        self.estudiantes_adicionales_input = "0"
        self.procesando = False
