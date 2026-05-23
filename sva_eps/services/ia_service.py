"""Servicio de IA con Groq.

Hace dos cosas con modelos de Groq:
1. OCR por visión: lee una imagen de INE y extrae CURP, nombre, fecha de
   nacimiento, sexo y estado usando un modelo multimodal (Llama 4 Scout).
2. Dictamen narrativo: genera una explicación en lenguaje natural del
   resultado de la validación y recomienda el apoyo federal idóneo.

Si no hay API key o la librería no está instalada, cae a un modo simulado
para que la demo del hackatón nunca se rompa. Los errores se imprimen en
consola para poder diagnosticar (clave inválida, red, etc.).
"""
from __future__ import annotations
import os

from dotenv import load_dotenv
load_dotenv(    
    dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'),
    override=True
    )
import base64
import json
import logging

logger = logging.getLogger("sva_eps.ia")

# Modelos Groq (mayo 2026). Visión: Llama 4 Scout. Texto: Llama 3.3 70B.
_MODELO_VISION = "meta-llama/llama-4-scout-17b-16e-instruct"
_MODELO_TEXTO = "llama-3.3-70b-versatile"

# Para la demo del hackatón la key va incrustada aquí.
# ⚠️ Esta key fue compartida en una captura: REVÓCALA en console.groq.com/keys
# y genera una nueva después del hackatón. Mejor aún, usa la variable de
# entorno GROQ_API_KEY (tiene prioridad sobre esta).
_API_KEY_HARDCODED = os.environ.get("GROQ_API_KEY", "")


def _get_client():
    api_key = os.environ.get("GROQ_API_KEY") or _API_KEY_HARDCODED
    print(f"[DEBUG] API KEY encontrada: {bool(api_key)} | primeros 8 chars: {api_key[:8] if api_key else 'VACIA'}")
    if not api_key:
        return None
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except ImportError:
        print("[DEBUG] groq no está instalado")
        return None


def ia_disponible() -> bool:
    return _get_client() is not None


def ocr_ine_con_ia(image_bytes: bytes, mime: str = "image/jpeg") -> dict | None:
    """Extrae datos de un INE usando el modelo de visión de Groq.

    Devuelve dict con curp/nombre/sexo/edad/estado, o None si falla
    (el caller hará fallback al OCR simulado).
    """
    client = _get_client()
    if client is None or not image_bytes:
        return None

    b64 = base64.b64encode(image_bytes).decode("utf-8")
    prompt = (
        "Eres un OCR experto en credenciales para votar del INE de México. "
        "Extrae los datos y responde SOLO con un objeto JSON válido, sin texto "
        "adicional ni markdown, con estas claves exactas: "
        "curp (string), nombre (string, nombre completo), sexo (string, 'H' o 'M'), "
        "edad (entero, calcula desde la fecha de nacimiento si está visible, si no 0), "
        "estado (string, entidad federativa). "
        "Si un dato no es legible, usa string vacío o 0."
    )
    try:
        resp = client.chat.completions.create(
            model=_MODELO_VISION,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url",
                     "image_url": {"url": f"data:{mime};base64,{b64}"}},
                ],
            }],
            temperature=0,
            max_tokens=400,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content)
        logger.info("OCR con IA exitoso para CURP %s", data.get("curp", "?"))
        return {
            "curp": str(data.get("curp", "")).upper().strip(),
            "nombre": str(data.get("nombre", "")).strip(),
            "sexo": str(data.get("sexo", "")).upper().strip()[:1] or "H",
            "edad": int(data.get("edad", 0) or 0),
            "estado": str(data.get("estado", "")).strip(),
        }
    except Exception as e:
        logger.warning("OCR con IA falló (%s): %s — usando OCR simulado",
                       type(e).__name__, str(e)[:200])
        print(f"[SVA-EPS][IA] OCR Groq falló: {type(e).__name__}: {str(e)[:200]}")
        return None


def dictamen_narrativo(expediente: dict) -> str:
    """Genera una explicación en lenguaje natural del dictamen.

    `expediente` debe traer: nombre, dictamen, motivo, score_biometrico,
    finado, programa_recomendado.
    """
    client = _get_client()
    if client is None:
        return _dictamen_fallback(expediente)

    prompt = (
        "Eres un auditor del Sistema de Validación Automatizada de Expedientes "
        "(SVA-EPS) para programas sociales en México. Con base en estos datos "
        "de validación, redacta un dictamen profesional y conciso (máximo 3 "
        "frases) que explique la decisión al revisor. Sé claro y formal.\n\n"
        f"Datos: {json.dumps(expediente, ensure_ascii=False)}"
    )
    try:
        resp = client.chat.completions.create(
            model=_MODELO_TEXTO,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.warning("Dictamen IA falló (%s): %s", type(e).__name__, str(e)[:200])
        print(f"[SVA-EPS][IA] Dictamen Groq falló: {type(e).__name__}: {str(e)[:200]}")
        return _dictamen_fallback(expediente)


def _dictamen_fallback(exp: dict) -> str:
    """Dictamen determinista cuando la IA no está disponible."""
    base = exp.get("motivo", "Validación procesada.")
    prog = exp.get("programa_recomendado", "")
    extra = f" Programa sugerido: {prog}." if prog else ""
    return f"[Dictamen automático] {base}{extra}"
