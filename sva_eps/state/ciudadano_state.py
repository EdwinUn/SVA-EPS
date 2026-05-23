"""Estado reactivo del flujo de registro del ciudadano.

Cambios v2:
- Nuevo campo `archivo_curp` (documento CURP físico) requerido para menores.
- `@rx.var requiere_curp_doc` dispara la visibilidad del dropzone.
- `puede_enviar` ahora exige la CURP cuando edad < 18.
"""
from __future__ import annotations

import asyncio
import base64
import os
import tempfile
import uuid
from datetime import datetime

import reflex as rx
from sqlmodel import select

from ..models import Expediente, EtapaWorkflow, Dictamen, recomendar_programas, CATALOGO
from ..services import (
    ocr_service,
    validacion_service,
    firma_service,
    ia_service,
    biometria_service,
)

# Becas que requieren constancia de estudios
_BECAS_MENORES = {"RITA", "BJ"}


class CiudadanoState(rx.State):
    # --- Campos del formulario (autocompletables por OCR/IA) ---
    curp: str = ""
    nombre: str = ""
    rfc: str = ""
    estado_entidad: str = ""
    edad: int = 0
    sexo: str = ""

    # --- Archivos ---
    archivo_ine: str = ""
    archivo_selfie: str = ""
    archivo_constancia: str = ""     # Constancia de estudios (becas menores)
    archivo_curp: str = ""           # NUEVO: documento CURP físico (menores)
    preview_ine: str = ""
    preview_selfie: str = ""
    preview_curp: str = ""           # NUEVO
    _ine_bytes: bytes = b""
    _curp_bytes: bytes = b""         # NUEVO
    _ine_path: str = ""
    _selfie_path: str = ""

    # --- Estado de la UI ---
    procesando_ocr: bool = False
    usando_ia: bool = False
    etapa_actual: str = ""
    dictamen: str = Dictamen.PENDIENTE
    motivo: str = ""
    analisis_ia: str = ""
    sello_hash: str = ""
    fecha_registro: str = ""
    finalizado: bool = False
    programa_recomendado: str = ""
    score_biometrico: int = 0

    # --- Servicios/apoyos del ciudadano ---
    servicios_activos: list[str] = []
    servicios_inactivos: list[str] = []

    # ── vars derivados ────────────────────────────────────────────────────────

    @rx.var
    def curp_duplicada(self) -> bool:
        if not self.curp:
            return False
        return self.curp.strip().upper() in BancoExpedientes.curps_registradas

    @rx.var
    def tiene_ine(self) -> bool:
        return self.archivo_ine != ""

    @rx.var
    def tiene_selfie(self) -> bool:
        return self.archivo_selfie != ""

    @rx.var
    def tiene_constancia(self) -> bool:
        return self.archivo_constancia != ""

    @rx.var
    def tiene_curp_doc(self) -> bool:
        """NUEVO: True si el documento físico CURP ya fue cargado."""
        return self.archivo_curp != ""

    @rx.var
    def es_menor(self) -> bool:
        """NUEVO: True una vez extraída la edad y siendo menor de 18."""
        return 0 < self.edad < 18

    @rx.var
    def requiere_curp_doc(self) -> bool:
        """NUEVO: visibilidad condicional del dropzone CURP.

        Se exige el documento CURP físico cuando el sistema detecta minor edad
        en el OCR (edad > 0 garantiza que ya hubo extracción).
        """
        return self.es_menor

    @rx.var
    def requiere_constancia(self) -> bool:
        """True cuando hay programas Rita Cetina / Benito Juárez elegibles."""
        elegibles = recomendar_programas(self.edad, self.sexo)
        claves = {p.clave for p in elegibles}
        return bool(claves & _BECAS_MENORES)

    @rx.var
    def requiere_rfc(self) -> bool:
        return self.edad >= 18

    @rx.var
    def puede_enviar(self) -> bool:
        base = bool(
            self.curp
            and self.nombre
            and self.tiene_selfie
            and not self.curp_duplicada
            and not self.finalizado
        )
        # Encadenamos requisitos condicionales sin permitir bypass:
        if self.requiere_constancia and not self.tiene_constancia:
            return False
        if self.requiere_curp_doc and not self.tiene_curp_doc:
            return False
        return base

    @rx.var
    def progreso_workflow(self) -> int:
        if self.etapa_actual in EtapaWorkflow.ORDEN:
            return EtapaWorkflow.ORDEN.index(self.etapa_actual)
        return -1

    @rx.var
    def badge_ia(self) -> str:
        return "IA Groq activa" if ia_service.ia_disponible() else "Modo simulado"

    @rx.var
    def ia_activa(self) -> bool:
        return ia_service.ia_disponible()

    @rx.var
    def nombre_programa_recomendado(self) -> str:
        elegibles = recomendar_programas(self.edad, self.sexo)
        return elegibles[0].nombre if elegibles else "Ninguno aplica por edad/perfil"

    @rx.var
    def servicios_activos_nombres(self) -> list[str]:
        nombres = []
        for clave in self.servicios_activos:
            p = next((x for x in CATALOGO if x.clave == clave), None)
            if p:
                nombres.append(p.nombre)
        return nombres

    @rx.var
    def servicios_inactivos_nombres(self) -> list[str]:
        nombres = []
        for clave in self.servicios_inactivos:
            p = next((x for x in CATALOGO if x.clave == clave), None)
            if p:
                nombres.append(p.nombre)
        return nombres

    # ── setters ───────────────────────────────────────────────────────────────

    def set_curp(self, value: str):
        self.curp = value.upper()

    def set_nombre(self, value: str):
        self.nombre = value

    # ── uploads ───────────────────────────────────────────────────────────────

    async def subir_ine(self, files: list[rx.UploadFile]):
        if not files:
            yield rx.toast.error("No se recibió ningún archivo.")
            return
        try:
            file = files[0]
            data = await file.read()
            if not data:
                yield rx.toast.error("El archivo llegó vacío. Intenta de nuevo.")
                return
            self._ine_bytes = data
            self.archivo_ine = file.filename or "ine.jpg"
            mime = file.content_type or "image/jpeg"
            self.preview_ine = f"data:{mime};base64,{base64.b64encode(data).decode()}"
            ext = ".png" if "png" in mime else ".jpg"
            path = os.path.join(tempfile.gettempdir(), f"ine_{uuid.uuid4().hex}{ext}")
            with open(path, "wb") as f:
                f.write(data)
            self._ine_path = path
            yield rx.toast.info("INE cargada. Pulsa 'Extraer datos'.")
        except Exception as e:
            yield rx.toast.error(f"Error al subir la INE: {e}")

    async def subir_selfie(self, files: list[rx.UploadFile]):
        if not files:
            yield rx.toast.error("No se recibió ningún archivo.")
            return
        try:
            file = files[0]
            data = await file.read()
            if not data:
                yield rx.toast.error("El archivo llegó vacío. Intenta de nuevo.")
                return
            self.archivo_selfie = file.filename or "selfie.jpg"
            mime = file.content_type or "image/jpeg"
            self.preview_selfie = f"data:{mime};base64,{base64.b64encode(data).decode()}"
            ext = ".png" if "png" in mime else ".jpg"
            path = os.path.join(tempfile.gettempdir(), f"selfie_{uuid.uuid4().hex}{ext}")
            with open(path, "wb") as f:
                f.write(data)
            self._selfie_path = path
            yield rx.toast.success("Selfie cargada correctamente.")
        except Exception as e:
            yield rx.toast.error(f"Error al subir la selfie: {e}")

    async def subir_constancia(self, files: list[rx.UploadFile]):
        """Sube constancia de estudios (solo para becas Rita Cetina / Benito Juárez)."""
        if not files:
            yield rx.toast.error("No se recibió ningún archivo.")
            return
        try:
            file = files[0]
            data = await file.read()
            if not data:
                yield rx.toast.error("El archivo llegó vacío. Intenta de nuevo.")
                return
            self.archivo_constancia = file.filename or "constancia.pdf"
            yield rx.toast.success("Constancia de estudios cargada.")
        except Exception as e:
            yield rx.toast.error(f"Error al subir la constancia: {e}")

    async def subir_curp(self, files: list[rx.UploadFile]):
        """NUEVO: Sube el documento CURP físico (obligatorio para menores).

        Validación de archivo:
        - Acepta PDF / PNG / JPG
        - Rechaza archivos > 5 MB
        - Rechaza archivos vacíos
        """
        if not files:
            yield rx.toast.error("No se recibió ningún archivo.")
            return
        try:
            file = files[0]
            data = await file.read()
            if not data:
                yield rx.toast.error("El archivo CURP llegó vacío.")
                return
            if len(data) > 5 * 1024 * 1024:
                yield rx.toast.error("El archivo CURP excede 5 MB.")
                return
            self._curp_bytes = data
            self.archivo_curp = file.filename or "curp.pdf"
            mime = file.content_type or "application/pdf"
            # Preview solo si es imagen; PDF solo muestra el nombre
            if mime.startswith("image/"):
                self.preview_curp = (
                    f"data:{mime};base64,{base64.b64encode(data).decode()}"
                )
            else:
                self.preview_curp = ""
            yield rx.toast.success("Documento CURP cargado.")
        except Exception as e:
            yield rx.toast.error(f"Error al subir el CURP: {e}")

    # ── OCR ───────────────────────────────────────────────────────────────────

    async def extraer_datos(self):
        if not self.tiene_ine:
            yield rx.toast.error("Primero sube la imagen del INE.")
            return
        self.procesando_ocr = True
        yield
        await asyncio.sleep(0.2)

        datos = None
        if ia_service.ia_disponible():
            datos = await asyncio.to_thread(ia_service.ocr_ine_con_ia, self._ine_bytes)
        if datos and datos.get("curp"):
            self.usando_ia = True
        else:
            datos = ocr_service.extraer_datos_ine(self.archivo_ine)
            self.usando_ia = False

        self.curp = datos.get("curp", "")
        self.nombre = datos.get("nombre", "")
        self.estado_entidad = datos.get("estado", "")
        self.sexo = datos.get("sexo", "H")
        self.edad = int(datos.get("edad", 0) or 0)

        if self.edad >= 18:
            self.rfc = datos.get("rfc", self.curp[:10] if self.curp else "")
        else:
            self.rfc = ""

        await self._cargar_servicios()
        self.procesando_ocr = False

        if self.curp_duplicada:
            yield rx.toast.error(f"La CURP {self.curp} ya está registrada.")
        elif self.es_menor:
            yield rx.toast.warning(
                "Detectamos que eres menor de edad. Sube tu documento CURP."
            )
        elif self.usando_ia:
            yield rx.toast.success("Datos extraídos con IA (Groq).")
        else:
            yield rx.toast.success("Datos extraídos (modo simulado).")

    async def _cargar_servicios(self):
        if not self.curp:
            return
        try:
            with rx.session() as session:
                expediente = session.exec(
                    select(Expediente).where(
                        Expediente.curp == self.curp.strip().upper()
                    )
                ).first()
                if expediente:
                    self.servicios_activos = [
                        s for s in expediente.servicios_activos.split(",") if s
                    ]
                    self.servicios_inactivos = [
                        s for s in expediente.servicios_inactivos.split(",") if s
                    ]
                else:
                    self.servicios_activos = []
                    self.servicios_inactivos = []
        except Exception:
            self.servicios_activos = []
            self.servicios_inactivos = []

    # ── Workflow principal ────────────────────────────────────────────────────

    async def enviar_expediente(self):
        if self.curp_duplicada:
            yield rx.toast.error("Expediente duplicado. Envío bloqueado.")
            return
        if not self.puede_enviar:
            # Diagnóstico granular antes de salir
            if self.requiere_curp_doc and not self.tiene_curp_doc:
                yield rx.toast.error("Menor de edad: falta documento CURP.")
            elif self.requiere_constancia and not self.tiene_constancia:
                yield rx.toast.error("Beca seleccionada: falta constancia de estudios.")
            else:
                yield rx.toast.error("Faltan datos o archivos requeridos.")
            return

        self.fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.etapa_actual = EtapaWorkflow.RECIBIDO
        self.dictamen = Dictamen.PENDIENTE
        self.motivo = ""
        self.analisis_ia = ""
        self.sello_hash = ""
        yield
        await asyncio.sleep(0.7)

        self.etapa_actual = EtapaWorkflow.RENAPO
        yield
        await asyncio.sleep(0.8)
        renapo = validacion_service.consultar_renapo(self.curp)

        self.etapa_actual = EtapaWorkflow.BIOMETRICO
        yield
        bio = await asyncio.to_thread(
            biometria_service.verificar_persona,
            self._ine_path or self.archivo_ine,
            self._selfie_path or self.archivo_selfie,
        )
        self.score_biometrico = int(bio.get("score", 0) * 100)
        await asyncio.sleep(0.4)

        self.etapa_actual = EtapaWorkflow.DICTAMEN
        dictamen, motivo = validacion_service.dictaminar(self.curp, renapo, bio)
        self.dictamen = dictamen
        self.motivo = motivo

        elegibles = recomendar_programas(self.edad, self.sexo)
        prog = elegibles[0] if elegibles else None
        self.programa_recomendado = prog.nombre if prog else "Ninguno aplica por edad/perfil"

        if dictamen == Dictamen.APROBADO and prog:
            if prog.clave not in self.servicios_activos:
                self.servicios_activos = self.servicios_activos + [prog.clave]

        yield
        await asyncio.sleep(0.3)

        self.analisis_ia = await asyncio.to_thread(
            ia_service.dictamen_narrativo,
            {
                "nombre": self.nombre,
                "dictamen": dictamen,
                "motivo": motivo,
                "score_biometrico": self.score_biometrico,
                "finado": renapo["finado"],
                "programa_recomendado": self.programa_recomendado,
            },
        )

        self.sello_hash = firma_service.generar_sello(
            self.curp, self.fecha_registro, self.estado_entidad
        )

        try:
            with rx.session() as session:
                nuevo = Expediente(
                    nombre=self.nombre,
                    curp=self.curp,
                    rfc=self.rfc,
                    estado=self.estado_entidad,
                    sexo=self.sexo,
                    edad=self.edad,
                    dictamen=dictamen,
                    motivo=motivo,
                    programa_recomendado=self.programa_recomendado,
                    score_biometrico=float(self.score_biometrico),
                    finado=bool(renapo["finado"]),
                    servicios_activos=",".join(self.servicios_activos),
                    servicios_inactivos=",".join(self.servicios_inactivos),
                    constancia_estudios=self.archivo_constancia,
                    archivo_curp=self.archivo_curp,   # NUEVO
                )
                session.add(nuevo)
                session.commit()

            BancoExpedientes.registrar_curp_local(self.curp)

        except Exception as e:
            print(f"[SVA-EPS][ERROR SUPABASE] {e}")
            yield rx.toast.error("Fallo de conexión con Supabase.")
            return

        self.finalizado = True

        if dictamen == Dictamen.APROBADO:
            yield rx.toast.success("Expediente APROBADO y guardado en Supabase.")
        elif dictamen == Dictamen.RECHAZADO:
            yield rx.toast.error(f"Expediente RECHAZADO: {motivo}")
        else:
            yield rx.toast.warning("Derivado a revisión manual (10%).")

    def reiniciar(self):
        self.curp = ""
        self.nombre = ""
        self.rfc = ""
        self.estado_entidad = ""
        self.edad = 0
        self.sexo = ""
        self.archivo_ine = ""
        self.archivo_selfie = ""
        self.archivo_constancia = ""
        self.archivo_curp = ""        # NUEVO
        self.preview_ine = ""
        self.preview_selfie = ""
        self.preview_curp = ""        # NUEVO
        self._ine_bytes = b""
        self._curp_bytes = b""        # NUEVO
        self._ine_path = ""
        self._selfie_path = ""
        self.usando_ia = False
        self.etapa_actual = ""
        self.dictamen = Dictamen.PENDIENTE
        self.motivo = ""
        self.analisis_ia = ""
        self.sello_hash = ""
        self.fecha_registro = ""
        self.finalizado = False
        self.programa_recomendado = ""
        self.score_biometrico = 0
        self.servicios_activos = []
        self.servicios_inactivos = []


class BancoExpedientes:
    curps_registradas: set[str] = set()

    @classmethod
    def registrar_curp_local(cls, curp: str):
        cls.curps_registradas.add(curp.strip().upper())
