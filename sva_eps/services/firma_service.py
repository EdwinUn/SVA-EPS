"""Simulación de firma digital / sello de inmutabilidad."""
from __future__ import annotations

import hashlib


def generar_sello(curp: str, fecha: str, estado: str) -> str:
    """Genera un sello de inmutabilidad SHA-256.

    Combina CURP + fecha exacta + estado. Cualquier alteración posterior de
    estos campos produciría un hash distinto, permitiendo trazabilidad.
    """
    payload = f"{curp.strip().upper()}|{fecha}|{estado.strip().upper()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verificar_sello(curp: str, fecha: str, estado: str, sello: str) -> bool:
    """Verifica que un expediente no haya sido alterado."""
    return generar_sello(curp, fecha, estado) == sello
