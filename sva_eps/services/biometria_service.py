"""Servicio de cotejo biométrico facial (INE vs selfie).

Usa DeepFace (Facenet512 + RetinaFace) si está instalado. Si no, cae a un
score simulado determinista para no romper la demo.

Umbrales sobre distancia coseno:
  <= 0.35  -> aprobado
  <= 0.50  -> revisión manual
  >  0.50  -> rechazado
"""
from __future__ import annotations

import random


def deepface_disponible() -> bool:
    try:
        import deepface  # noqa: F401
        return True
    except ImportError:
        return False


def verificar_persona(foto_ine: str, foto_selfie: str) -> dict:
    """Compara dos imágenes y devuelve el resultado biométrico.

    Returns dict: es_misma_persona, distancia, score (0-1, mayor = mejor),
    veredicto ('aprobado'|'revision_manual'|'rechazado'), modelo, simulado.
    """
    if deepface_disponible():
        return _verificar_real(foto_ine, foto_selfie)
    return _verificar_simulado(foto_ine, foto_selfie)


def _verificar_real(foto_ine: str, foto_selfie: str) -> dict:
    from deepface import DeepFace
    try:
        resultado = DeepFace.verify(
            img1_path=foto_ine,
            img2_path=foto_selfie,
            model_name="Facenet512",
            detector_backend="retinaface",
            distance_metric="cosine",
        )
        distancia = float(resultado["distance"])
        return {
            "es_misma_persona": bool(resultado["verified"]),
            "distancia": round(distancia, 4),
            "score": round(max(0.0, 1.0 - distancia), 4),
            "veredicto": _evaluar_score(distancia),
            "modelo": resultado.get("model", "Facenet512"),
            "simulado": False,
        }
    except Exception as e:
        # Sin rostro detectado u otro error -> rechazo seguro
        return {
            "es_misma_persona": False,
            "distancia": 1.0,
            "score": 0.0,
            "veredicto": "rechazado",
            "modelo": "Facenet512",
            "simulado": False,
            "error": str(e),
        }


def _verificar_simulado(foto_ine: str, foto_selfie: str) -> dict:
    """Score determinista basado en los nombres de archivo."""
    seed = f"{foto_ine}|{foto_selfie}"
    distancia = random.Random(seed).uniform(0.15, 0.65)
    return {
        "es_misma_persona": distancia <= 0.40,
        "distancia": round(distancia, 4),
        "score": round(1.0 - distancia, 4),
        "veredicto": _evaluar_score(distancia),
        "modelo": "Facenet512 (simulado)",
        "simulado": True,
    }


def _evaluar_score(distancia: float) -> str:
    if distancia <= 0.35:
        return "aprobado"
    if distancia <= 0.50:
        return "revision_manual"
    return "rechazado"
