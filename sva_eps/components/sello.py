"""Panel de resultados: dictamen, análisis IA, biometría, programa y sello."""
from __future__ import annotations

import reflex as rx

from ..models import Dictamen
from ..state import CiudadanoState
from .theme import GUINDA, DORADO, VERDE, ROJO, AMBAR, TINTA, TINTA_SUAVE


def panel_resultado() -> rx.Component:
    color = rx.match(
        CiudadanoState.dictamen,
        (Dictamen.APROBADO, VERDE),
        (Dictamen.RECHAZADO, ROJO),
        (Dictamen.REVISION, AMBAR),
        TINTA_SUAVE,
    )
    icono = rx.match(
        CiudadanoState.dictamen,
        (Dictamen.APROBADO, "circle-check-big"),
        (Dictamen.RECHAZADO, "circle-x"),
        (Dictamen.REVISION, "circle-alert"),
        "circle",
    )
    return rx.cond(
        CiudadanoState.dictamen != Dictamen.PENDIENTE,
        rx.box(
            rx.vstack(
                # Encabezado de dictamen
                rx.hstack(
                    rx.icon(icono, size=30, color=color),
                    rx.vstack(
                        rx.text("Dictamen automático",
                                style={"font_size": "0.7rem", "letter_spacing": "0.1em",
                                       "text_transform": "uppercase", "color": TINTA_SUAVE}),
                        rx.text(CiudadanoState.dictamen,
                                style={"font_family": "'Fraunces', serif", "font_weight": "900",
                                       "font_size": "1.4rem", "color": color, "line_height": "1"}),
                        spacing="1", align="start",
                    ),
                    spacing="3", align="center", width="100%",
                ),
                rx.text(CiudadanoState.motivo,
                        style={"font_size": "0.86rem", "color": TINTA}),

                # Score biométrico
                rx.box(
                    rx.hstack(
                        rx.icon("scan-face", size=16, color=GUINDA),
                        rx.text("Confianza biométrica",
                                style={"font_size": "0.78rem", "color": TINTA_SUAVE, "flex": "1"}),
                        rx.text(CiudadanoState.score_biometrico.to_string() + "%",
                                style={"font_family": "'Fraunces', serif", "font_weight": "600",
                                       "color": GUINDA}),
                        spacing="2", align="center", width="100%",
                    ),
                    rx.box(
                        rx.box(style={
                            "height": "100%",
                            "width": CiudadanoState.score_biometrico.to_string() + "%",
                            "background": f"linear-gradient(90deg, {DORADO}, {GUINDA})",
                            "border_radius": "4px", "transition": "width 0.6s ease",
                        }),
                        style={"height": "7px", "background": "rgba(28,26,23,0.08)",
                               "border_radius": "4px", "margin_top": "0.4rem", "width": "100%"},
                    ),
                    width="100%",
                ),

                # Análisis IA
                rx.cond(
                    CiudadanoState.analisis_ia != "",
                    rx.box(
                        rx.hstack(
                            rx.icon("sparkles", size=15, color=DORADO),
                            rx.text("Análisis de IA",
                                    style={"font_size": "0.72rem", "font_weight": "600",
                                           "letter_spacing": "0.08em", "text_transform": "uppercase",
                                           "color": DORADO}),
                            spacing="2", align="center",
                        ),
                        rx.text(CiudadanoState.analisis_ia,
                                style={"font_size": "0.84rem", "color": TINTA,
                                       "font_style": "italic", "margin_top": "0.3rem"}),
                        style={"background": "rgba(165,127,44,0.07)", "border_left": f"3px solid {DORADO}",
                               "border_radius": "0 10px 10px 0", "padding": "0.7rem 0.9rem", "width": "100%"},
                    ),
                ),

                # Programa recomendado
                rx.box(
                    rx.hstack(
                        rx.icon("heart-handshake", size=18, color=GUINDA),
                        rx.vstack(
                            rx.text("Apoyo federal recomendado",
                                    style={"font_size": "0.7rem", "color": TINTA_SUAVE,
                                           "text_transform": "uppercase", "letter_spacing": "0.08em"}),
                            rx.text(CiudadanoState.programa_recomendado,
                                    style={"font_weight": "600", "color": GUINDA, "font_size": "0.9rem"}),
                            spacing="0", align="start",
                        ),
                        spacing="3", align="center",
                    ),
                    style={"background": "rgba(157,36,73,0.06)", "border_radius": "12px",
                           "padding": "0.8rem 1rem", "width": "100%"},
                ),

                spacing="4", align="start", width="100%",
            ),
            class_name="card-paper rise rise-1",
            padding="1.7rem", width="100%",
            style={"border_top": f"4px solid {color}"},
        ),
    )


def sello_inmutabilidad() -> rx.Component:
    return rx.cond(
        CiudadanoState.sello_hash != "",
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("shield-check", size=20, color=VERDE),
                    rx.text("Sello de Inmutabilidad",
                            style={"font_family": "'Fraunces', serif", "font_weight": "600",
                                   "font_size": "1.1rem", "color": TINTA}),
                    rx.spacer(),
                    rx.badge("SHA-256", style={"background": "rgba(61,107,53,0.12)", "color": VERDE}),
                    width="100%", align="center",
                ),
                rx.text("CURP + fecha exacta + estado",
                        style={"font_size": "0.72rem", "color": TINTA_SUAVE}),
                rx.box(
                    rx.text(CiudadanoState.sello_hash,
                            style={"font_family": "monospace", "font_size": "0.72rem",
                                   "color": VERDE, "word_break": "break-all", "line_height": "1.5"}),
                    style={"background": "rgba(61,107,53,0.06)", "border": "1px dashed rgba(61,107,53,0.3)",
                           "border_radius": "10px", "padding": "0.7rem", "width": "100%"},
                ),
                rx.hstack(
                    rx.icon("clock", size=13, color=TINTA_SUAVE),
                    rx.text(CiudadanoState.fecha_registro,
                            style={"font_size": "0.74rem", "color": TINTA_SUAVE}),
                    spacing="2", align="center",
                ),
                spacing="2", align="start", width="100%",
            ),
            class_name="card-paper rise rise-2",
            padding="1.5rem", width="100%",
        ),
    )
