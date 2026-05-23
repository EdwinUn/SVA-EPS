"""Modelos de datos del SVA-EPS."""
from __future__ import annotations

import reflex as rx
from sqlmodel import Field


class EtapaWorkflow:
    RECIBIDO   = "Recibido"
    RENAPO     = "Validación RENAPO"
    BIOMETRICO = "Cotejo Biométrico"
    DICTAMEN   = "Dictamen"
    ORDEN = [RECIBIDO, RENAPO, BIOMETRICO, DICTAMEN]


class Dictamen:
    APROBADO  = "APROBADO"
    RECHAZADO = "RECHAZADO"
    REVISION  = "REVISIÓN MANUAL"
    PENDIENTE = "PENDIENTE"


class Expediente(rx.Model, table=True):
    """Expediente ciudadano — persiste en Supabase vía SQLModel."""

    __tablename__ = "expediente"

    id:                   int | None = Field(default=None, primary_key=True)
    folio:                str = ""
    curp:                 str = ""
    nombre:               str = ""
    rfc:                  str = ""
    estado:               str = ""
    edad:                 int = 0
    sexo:                 str = ""
    etapa:                str = EtapaWorkflow.RECIBIDO
    dictamen:             str = Dictamen.PENDIENTE
    motivo:               str = ""
    sello_hash:           str = ""
    fecha:                str = ""
    finado:               bool = False
    score_biometrico:     float = 0.0
    programa_recomendado: str = ""
    analisis_ia:          str = ""
    fecha_registro:       str = ""
    servicios_activos:    str = ""
    servicios_inactivos:  str = ""
    constancia_estudios:  str = ""
    archivo_curp:         str = ""   # NUEVO: nombre del archivo CURP físico (menores)
