"""Tarjeta de programa social para el catálogo."""
from __future__ import annotations

import reflex as rx

from ..models import ProgramaSocial
from .theme import GUINDA, DORADO, TINTA, TINTA_SUAVE


def programa_card(p: ProgramaSocial, idx: int) -> rx.Component:
    rango = (
        f"{p.edad_min}+ años" if p.edad_max >= 200
        else f"{p.edad_min}–{p.edad_max} años"
    )
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(p.icono, size=22, color="white"),
                    style={"background": f"linear-gradient(135deg, {GUINDA}, #611232)",
                           "border_radius": "12px", "padding": "0.6rem", "display": "flex"},
                ),
                rx.spacer(),
                rx.badge(rango, style={"background": "rgba(165,127,44,0.14)", "color": DORADO}),
                width="100%", align="center",
            ),
            rx.text(p.nombre,
                    style={"font_family": "'Fraunces', serif", "font_weight": "600",
                           "font_size": "1.05rem", "color": TINTA, "line_height": "1.25"}),
            rx.text(p.descripcion,
                    style={"font_size": "0.83rem", "color": TINTA_SUAVE, "line_height": "1.5"}),
            rx.cond(
                p.solo_mujeres,
                rx.badge("Exclusivo mujeres",
                         style={"background": "rgba(157,36,73,0.1)", "color": GUINDA}),
            ),
            spacing="3", align="start", width="100%", height="100%",
        ),
        class_name="card-paper",
        style={"padding": "1.4rem", "height": "100%",
               "transition": "transform 0.2s ease", "_hover": {"transform": "translateY(-4px)"}},
    )
