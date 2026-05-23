"""Estado del Módulo de Consulta (independiente del flujo de postulación).

Permite al ciudadano consultar el estatus (VIGENTE / INACTIVO / NO_REGISTRADO)
de un programa social específico cargando su INE y seleccionando el servicio.
No persiste nada: es solo lectura sobre la tabla Expediente.
"""
from __future__ import annotations

import asyncio
import base64
from typing import List, Tuple

import reflex as rx
from sqlmodel import select
from sqlmodel import select

from ..models import Expediente, CATALOGO
from ..services import ocr_service, ia_service


class ConsultaState(rx.State):
    # --- Archivo INE para identificación ---
    archivo_ine_consulta: str = ""
    preview_ine_consulta: str = ""
    _ine_consulta_bytes: bytes = b""

    # --- Datos extraídos del INE ---
    curp_consultada: str = ""
    nombre_consultado: str = ""
    edad_consultada: int = 0
    sexo_consultado: str = ""

    # --- Selección del programa ---
    programa_seleccionado: str = ""   # clave del programa (PAM, RITA, BJ, etc.)

    # --- Estado de la UI ---
    procesando_ocr: bool = False
    consultando: bool = False
    consulta_realizada: bool = False

    # Resultado: "VIGENTE" | "INACTIVO" | "NO_REGISTRADO" | ""
    estatus_servicio: str = ""
    mensaje_resultado: str = ""

    # Servicios cacheados de la última consulta (para mostrar todos)
    servicios_activos_consulta: list[str] = []
    servicios_inactivos_consulta: list[str] = []

    # ── vars derivados ────────────────────────────────────────────────────────

    @rx.var
    def tiene_ine(self) -> bool:
        return self.archivo_ine_consulta != ""

    @rx.var
    def datos_extraidos(self) -> bool:
        """True cuando el OCR ya produjo CURP y edad."""
        return bool(self.curp_consultada) and self.edad_consultada > 0

    @rx.var
    def puede_consultar(self) -> bool:
        return (
            self.datos_extraidos
            and self.programa_seleccionado != ""
            and not self.consultando
        )

    @rx.var
    def es_vigente(self) -> bool:
        return self.estatus_servicio == "VIGENTE"

    @rx.var
    def es_inactivo(self) -> bool:
        return self.estatus_servicio == "INACTIVO"

    @rx.var
    def es_no_registrado(self) -> bool:
        return self.estatus_servicio == "NO_REGISTRADO"

    @rx.var
    def opciones_programa(self) -> list[list[str]]:
        """[[clave, nombre], ...] para alimentar el rx.select."""
        return [[p.clave, p.nombre] for p in CATALOGO]

    @rx.var
    def nombres_programas(self) -> list[str]:
        """Solo los nombres legibles para el select."""
        return [p.nombre for p in CATALOGO]

    @rx.var
    def nombre_programa_seleccionado(self) -> str:
        if not self.programa_seleccionado:
            return ""
        p = next((x for x in CATALOGO if x.clave == self.programa_seleccionado), None)
        return p.nombre if p else ""

    # ── setters ───────────────────────────────────────────────────────────────

    def set_programa(self, nombre: str):
        """El select envía el nombre; lo mapeamos a la clave interna."""
        p = next((x for x in CATALOGO if x.nombre == nombre), None)
        self.programa_seleccionado = p.clave if p else ""
        # Si ya había una consulta hecha, la invalidamos
        self.consulta_realizada = False
        self.estatus_servicio = ""

    # ── upload INE ────────────────────────────────────────────────────────────

    async def subir_ine_consulta(self, files: list[rx.UploadFile]):
        if not files:
            yield rx.toast.error("No se recibió ningún archivo.")
            return
        try:
            file = files[0]
            data = await file.read()
            if not data:
                yield rx.toast.error("El archivo llegó vacío. Intenta de nuevo.")
                return
            self._ine_consulta_bytes = data
            self.archivo_ine_consulta = file.filename or "ine.jpg"
            mime = file.content_type or "image/jpeg"
            self.preview_ine_consulta = (
                f"data:{mime};base64,{base64.b64encode(data).decode()}"
            )
            # Reset resultados previos
            self.consulta_realizada = False
            self.estatus_servicio = ""
            yield rx.toast.info("INE cargada. Pulsa 'Identificar' para extraer datos.")
        except Exception as e:
            yield rx.toast.error(f"Error al subir la INE: {e}")

    # ── OCR (sin persistir nada) ──────────────────────────────────────────────

    async def identificar(self):
        if not self.tiene_ine:
            yield rx.toast.error("Primero sube tu INE.")
            return
        self.procesando_ocr = True
        yield
        await asyncio.sleep(0.2)

        datos = None
        if ia_service.ia_disponible():
            datos = await asyncio.to_thread(
                ia_service.ocr_ine_con_ia, self._ine_consulta_bytes
            )
        if not datos or not datos.get("curp"):
            datos = ocr_service.extraer_datos_ine(self.archivo_ine_consulta)

        self.curp_consultada = (datos.get("curp") or "").strip().upper()
        self.nombre_consultado = datos.get("nombre", "")
        self.edad_consultada = int(datos.get("edad", 0) or 0)
        self.sexo_consultado = datos.get("sexo", "H")
        self.procesando_ocr = False

        if not self.curp_consultada:
            yield rx.toast.error("No se pudo leer la CURP. Vuelve a intentar con otra foto.")
        else:
            yield rx.toast.success(f"Identificado: {self.nombre_consultado}")

    # ── Consulta de estatus ───────────────────────────────────────────────────

    async def consultar_estatus(self):
        if not self.datos_extraidos:
            yield rx.toast.error("Identifícate primero con tu INE.")
            return
        if not self.programa_seleccionado:
            yield rx.toast.error("Selecciona el programa a consultar.")
            return

        self.consultando = True
        self.consulta_realizada = False
        self.estatus_servicio = ""
        yield
        await asyncio.sleep(0.4)  # microtransición visual

        try:
            with rx.session() as session:
                expediente = session.exec(
                    select(Expediente).where(
                        Expediente.curp == self.curp_consultada
                    )
                ).first()

                if not expediente:
                    self.servicios_activos_consulta = []
                    self.servicios_inactivos_consulta = []
                    self.estatus_servicio = "NO_REGISTRADO"
                    self.mensaje_resultado = (
                        "No se encontró expediente con esta CURP. "
                        "Postúlate desde el módulo de Solicitud."
                    )
                else:
                    activos = [s for s in expediente.servicios_activos.split(",") if s]
                    inactivos = [s for s in expediente.servicios_inactivos.split(",") if s]
                    self.servicios_activos_consulta = activos
                    self.servicios_inactivos_consulta = inactivos

                    if self.programa_seleccionado in activos:
                        self.estatus_servicio = "VIGENTE"
                        self.mensaje_resultado = (
                            f"Tu apoyo «{self.nombre_programa_seleccionado}» está vigente."
                        )
                    elif self.programa_seleccionado in inactivos:
                        self.estatus_servicio = "INACTIVO"
                        self.mensaje_resultado = (
                            f"Tu apoyo «{self.nombre_programa_seleccionado}» figura como "
                            "anterior o cancelado en nuestros registros."
                        )
                    else:
                        self.estatus_servicio = "NO_REGISTRADO"
                        self.mensaje_resultado = (
                            f"No hay registro de «{self.nombre_programa_seleccionado}» "
                            "asociado a esta CURP."
                        )

            self.consulta_realizada = True
        except Exception as e:
            yield rx.toast.error(f"Error al consultar Supabase: {e}")
        finally:
            self.consultando = False

    def reiniciar_consulta(self):
        self.archivo_ine_consulta = ""
        self.preview_ine_consulta = ""
        self._ine_consulta_bytes = b""
        self.curp_consultada = ""
        self.nombre_consultado = ""
        self.edad_consultada = 0
        self.sexo_consultado = ""
        self.programa_seleccionado = ""
        self.procesando_ocr = False
        self.consultando = False
        self.consulta_realizada = False
        self.estatus_servicio = ""
        self.mensaje_resultado = ""
        self.servicios_activos_consulta = []
        self.servicios_inactivos_consulta = []
