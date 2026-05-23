"""Workflow stepper editorial del flujo de aprobación."""
from __future__ import annotations

import reflex as rx

from ..models import EtapaWorkflow
from ..state import CiudadanoState
from .theme import GUINDA, DORADO, VERDE, TINTA, TINTA_SUAVE

_ICONOS = ["inbox", "database", "scan-face", "gavel"]


def _step(nombre: str, indice: int) -> rx.Component:
    activa = CiudadanoState.progreso_workflow == indice
    completada = CiudadanoState.progreso_workflow > indice
    return rx.vstack(
        rx.box(
            rx.cond(
                completada,
                rx.icon("check", size=18, color="white"),
                rx.icon(_ICONOS[indice], size=18,
                        color=rx.cond(activa, "white", TINTA_SUAVE)),
            ),
            class_name=rx.cond(activa, "pulse", ""),
            style={
                "width": "46px", "height": "46px", "border_radius": "13px",
                "display": "flex", "align_items": "center", "justify_content": "center",
                "background": rx.cond(completada, VERDE,
                                      rx.cond(activa, GUINDA, "rgba(28,26,23,0.06)")),
                "transition": "all 0.35s cubic-bezier(0.22,1,0.36,1)",
                "transform": rx.cond(activa, "scale(1.08)", "scale(1)"),
            },
        ),
        rx.text(nombre, style={
            "font_size": "0.72rem", "text_align": "center", "max_width": "84px",
            "font_weight": rx.cond(activa, "600", "400"),
            "color": rx.cond(activa, GUINDA, TINTA_SUAVE),
        }),
        align="center", spacing="2",
    )


def _conector(indice: int) -> rx.Component:
    lleno = CiudadanoState.progreso_workflow > indice
    return rx.box(
        rx.box(style={
            "height": "100%",
            "width": rx.cond(lleno, "100%", "0%"),
            "background": VERDE, "transition": "width 0.5s ease 0.2s",
        }),
        style={"flex": "1", "height": "3px", "background": "rgba(28,26,23,0.1)",
               "border_radius": "2px", "margin_top": "21px", "max_width": "60px"},
    )


def workflow_stepper() -> rx.Component:
    return rx.cond(
        CiudadanoState.progreso_workflow >= 0,
        rx.box(
            rx.vstack(
                rx.text("Trazabilidad del expediente",
                        style={"font_family": "'Fraunces', serif", "font_weight": "600",
                               "font_size": "1.1rem", "color": TINTA}),
                rx.hstack(
                    _step(EtapaWorkflow.RECIBIDO, 0), _conector(0),
                    _step(EtapaWorkflow.RENAPO, 1), _conector(1),
                    _step(EtapaWorkflow.BIOMETRICO, 2), _conector(2),
                    _step(EtapaWorkflow.DICTAMEN, 3),
                    align="start", justify="center", width="100%",
                ),
                spacing="4", width="100%",
            ),
            class_name="card-paper rise",
            padding="1.6rem", width="100%",
        ),
    )
