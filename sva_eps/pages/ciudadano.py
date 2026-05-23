"""Página principal: solicitud de apoyo del ciudadano."""
from __future__ import annotations

import reflex as rx

from ..components import (
    navbar, panel_captura, panel_datos,
    workflow_stepper, panel_resultado, sello_inmutabilidad,
)
from ..components.theme import GUINDA, DORADO, TINTA, TINTA_SUAVE


def _hero() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("Programas para el Bienestar", class_name="kicker"),
            rx.heading(
                "Solicita tu apoyo en minutos,",
                rx.text.span(" sin filas ni trámites.",
                             style={"color": GUINDA, "font_style": "italic"}),
                style={"font_family": "'Fraunces', serif", "font_weight": "900",
                       "font_size": "clamp(1.8rem, 4vw, 2.9rem)", "line_height": "1.05",
                       "color": TINTA, "max_width": "640px"},
            ),
            rx.text(
                "Sube tu INE y una selfie. Nuestra IA lee tus datos, verifica tu identidad "
                "y dictamina automáticamente el 90% de los expedientes.",
                style={"color": TINTA_SUAVE, "font_size": "1rem", "max_width": "560px",
                       "line_height": "1.6"},
            ),
            spacing="3", align="start",
        ),
        class_name="rise",
        padding_y="2.5rem",
    )


def ciudadano_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            _hero(),
            rx.grid(
                rx.vstack(panel_captura(), panel_datos(), spacing="4", width="100%"),
                rx.vstack(
                    workflow_stepper(), panel_resultado(), sello_inmutabilidad(),
                    rx.cond(
                        workflow_stepper_oculto(),
                        _placeholder(),
                    ),
                    spacing="4", width="100%",
                ),
                columns=rx.breakpoints(initial="1", md="2"),
                spacing="5", width="100%",
            ),
            style={"max_width": "1180px", "margin": "0 auto", "padding": "0 1.5rem 4rem"},
        ),
        width="100%", min_height="100vh",
    )


def workflow_stepper_oculto():
    from ..state import CiudadanoState
    return CiudadanoState.progreso_workflow < 0


def _placeholder() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.icon("file-search", size=40, color="rgba(157,36,73,0.25)"),
            rx.text("El estado de tu expediente aparecerá aquí",
                    style={"color": TINTA_SUAVE, "font_size": "0.9rem", "text_align": "center"}),
            spacing="3", align="center",
        ),
        class_name="card-paper",
        style={"padding": "3rem 1.5rem", "width": "100%",
               "display": "flex", "justify_content": "center",
               "border_style": "dashed", "background": "transparent"},
    )
