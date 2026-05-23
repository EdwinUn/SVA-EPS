"""Barra de navegación editorial."""
from __future__ import annotations

import reflex as rx

from .theme import GUINDA, DORADO, TINTA


def _link(texto: str, href: str) -> rx.Component:
    return rx.link(
        texto,
        href=href,
        style={
            "font_size": "0.9rem",
            "font_weight": "500",
            "color": TINTA,
            "padding": "0.4rem 0.9rem",
            "border_radius": "8px",
            "transition": "all 0.15s ease",
            "_hover": {"background": "rgba(157,36,73,0.08)", "color": GUINDA},
        },
    )


def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.box(
                    rx.icon("shield-check", size=22, color="white"),
                    style={
                        "background": f"linear-gradient(135deg, {GUINDA}, #611232)",
                        "border_radius": "11px",
                        "padding": "0.55rem",
                        "display": "flex",
                        "box_shadow": "0 8px 18px -10px rgba(157,36,73,0.8)",
                    },
                ),
                rx.vstack(
                    rx.text("SVA·EPS",
                            style={"font_family": "'Fraunces', serif",
                                   "font_weight": "900", "font_size": "1.35rem",
                                   "line_height": "1", "color": TINTA}),
                    rx.text("Validación Automatizada de Expedientes",
                            style={"font_size": "0.68rem", "color": "#6b6357",
                                   "letter_spacing": "0.04em"}),
                    spacing="0", align="start",
                ),
                spacing="3", align="center",
            ),
            rx.spacer(),
            rx.hstack(
                _link("Solicitud", "/"),
                _link("Consulta", "/consulta"),     # NUEVO
                _link("Programas", "/programas"),
                _link("Consola Admin", "/admin"),
                spacing="1",
            ),
            width="100%",
            max_width="1180px",
            margin="0 auto",
            padding="0.9rem 1.5rem",
            align="center",
        ),
        style={
            "position": "sticky", "top": "0", "z_index": "50", "width": "100%",
            "background": "rgba(247,243,236,0.82)",
            "backdrop_filter": "blur(12px)",
            "border_bottom": "1px solid rgba(28,26,23,0.08)",
        },
    )
