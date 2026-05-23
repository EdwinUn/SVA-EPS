"""Página /consulta — Módulo de Consulta de Estatus."""
from __future__ import annotations

import reflex as rx

from ..components import navbar
from ..components.consulta import panel_consulta, panel_resultado_consulta
from ..components.theme import GUINDA, TINTA, TINTA_SUAVE


def _hero() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("Consulta ciudadana", class_name="kicker"),
            rx.heading(
                "¿Tu apoyo está",
                rx.text.span(" vigente?",
                             style={"color": GUINDA, "font_style": "italic"}),
                style={"font_family": "'Fraunces', serif", "font_weight": "900",
                       "font_size": "clamp(1.8rem, 4vw, 2.9rem)", "line_height": "1.05",
                       "color": TINTA, "max_width": "640px"},
            ),
            rx.text(
                "Sube tu INE, selecciona el programa y consulta tu estatus en segundos. "
                "Sin filas, sin trámites presenciales.",
                style={"color": TINTA_SUAVE, "font_size": "1rem", "max_width": "560px",
                       "line_height": "1.6"},
            ),
            spacing="3", align="start",
        ),
        class_name="rise",
        padding_y="2.5rem",
    )


def consulta_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            _hero(),
            rx.grid(
                panel_consulta(),
                panel_resultado_consulta(),
                columns=rx.breakpoints(initial="1", md="2"),
                spacing="5", width="100%",
            ),
            style={"max_width": "1180px", "margin": "0 auto",
                   "padding": "0 1.5rem 4rem"},
        ),
        width="100%", min_height="100vh",
    )
