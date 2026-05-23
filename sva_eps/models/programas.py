"""Catálogo de Programas para el Bienestar (apoyos federales reales).

Datos basados en los programas sociales federales vigentes. Incluye reglas
de elegibilidad simplificadas para que el motor recomiende automáticamente.
"""
from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class ProgramaSocial:
    clave: str
    nombre: str
    descripcion: str
    edad_min: int = 0
    edad_max: int = 200
    solo_mujeres: bool = False
    color: str = "ruby"          # color de acento para la UI
    icono: str = "heart-handshake"


CATALOGO: list[ProgramaSocial] = [
    ProgramaSocial(
        clave="PAM",
        nombre="Pensión para el Bienestar de las Personas Adultas Mayores",
        descripcion="Apoyo económico bimestral para personas de 65 años o más.",
        edad_min=65,
        color="ruby",
        icono="heart-handshake",
    ),
    ProgramaSocial(
        clave="PMB",
        nombre="Pensión Mujeres Bienestar",
        descripcion="Apoyo para mujeres de 60 a 64 años.",
        edad_min=60,
        edad_max=64,
        solo_mujeres=True,
        color="purple",
        icono="venus",
    ),
    ProgramaSocial(
        clave="SCC",
        nombre="Salud Casa por Casa",
        descripcion="Atención médica domiciliaria para adultos mayores y personas con discapacidad.",
        edad_min=60,
        color="crimson",
        icono="house-plus",
    ),
    ProgramaSocial(
        clave="RITA",
        nombre="Beca Universal Rita Cetina (Educación Básica)",
        descripcion="Beca para estudiantes de secundaria pública (menores de edad).",
        edad_min=12,
        edad_max=17,
        color="pink",
        icono="graduation-cap",
    ),
    ProgramaSocial(
        clave="BJ",
        nombre="Beca Benito Juárez (Media Superior)",
        descripcion="Beca universal para estudiantes de bachillerato (menores de edad).",
        edad_min=15,
        edad_max=17,
        color="ruby",
        icono="book-open",
    ),
    ProgramaSocial(
        clave="JEF",
        nombre="Beca Educación Superior Jóvenes Escribiendo el Futuro",
        descripcion="Apoyo para estudiantes de licenciatura en situación vulnerable.",
        edad_min=18,
        edad_max=29,
        color="amber",
        icono="award",
    ),
]


def recomendar_programas(edad: int, sexo: str) -> list[ProgramaSocial]:
    """Devuelve los programas para los que el ciudadano es elegible."""
    es_mujer = sexo.upper().startswith("M")
    elegibles = []
    for p in CATALOGO:
        if not (p.edad_min <= edad <= p.edad_max):
            continue
        if p.solo_mujeres and not es_mujer:
            continue
        elegibles.append(p)
    return elegibles


def por_clave(clave: str) -> ProgramaSocial | None:
    return next((p for p in CATALOGO if p.clave == clave), None)
