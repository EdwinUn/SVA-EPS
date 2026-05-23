"""Motor de validación: simulación RENAPO y reglas de dictamen 90/10."""
from __future__ import annotations

import random

from ..models import Dictamen


def consultar_renapo(curp: str) -> dict:
    """Simula una consulta a RENAPO.

    Detecta estatus de defunción de forma determinista a partir de la CURP
    para que la demo sea repetible. ~5% marcados como finados.
    """
    rng = random.Random(curp)
    finado = rng.random() < 0.05
    vigente = rng.random() < 0.95
    return {"finado": finado, "vigente": vigente}


def dictaminar(curp: str, renapo: dict, bio: dict) -> tuple[str, str]:
    """Aplica la regla de eficiencia 90/10.

    `bio` es el dict de biometria_service.verificar_persona.
    Returns (dictamen, motivo).
    - Rechazo automático: finado, INE no vigente, o biometría rechazada.
    - Aprobación automática: biometría aprobada y datos vigentes.
    - Revisión manual: zona dudosa de biometría (~10%).
    """
    if renapo["finado"]:
        return Dictamen.RECHAZADO, "Estatus de defunción detectado en RENAPO."
    if not renapo["vigente"]:
        return Dictamen.RECHAZADO, "Identificación oficial no vigente."

    veredicto = bio.get("veredicto", "rechazado")
    score = bio.get("score", 0.0)
    if veredicto == "aprobado":
        return Dictamen.APROBADO, f"Cotejo biométrico exitoso (confianza {score:.0%})."
    if veredicto == "rechazado":
        return Dictamen.RECHAZADO, f"El rostro no coincide con el INE (confianza {score:.0%})."
    return (
        Dictamen.REVISION,
        f"Cotejo biométrico en zona dudosa (confianza {score:.0%}). Requiere revisión humana.",
    )
