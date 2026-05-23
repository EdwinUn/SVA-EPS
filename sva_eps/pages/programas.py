"""Catálogo de Programas para el Bienestar."""
from __future__ import annotations

import reflex as rx

from ..components import navbar, programa_card
from ..components.theme import GUINDA, TINTA, TINTA_SUAVE
from ..models import CATALOGO


def programas_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.vstack(
                rx.text("Catálogo federal", class_name="kicker"),
                rx.heading("Programas para el Bienestar",
                           style={"font_family": "'Fraunces', serif", "font_weight": "900",
                                  "font_size": "clamp(1.8rem, 4vw, 2.6rem)", "color": TINTA}),
                rx.text("El sistema determina automáticamente para cuáles eres elegible según tu edad y perfil.",
                        style={"color": TINTA_SUAVE, "max_width": "560px"}),
                spacing="3", align="start", padding_y="2.5rem",
            ),
            rx.grid(
                *[programa_card(p, i) for i, p in enumerate(CATALOGO)],
                columns=rx.breakpoints(initial="1", sm="2", lg="3"),
                spacing="4", width="100%",
            ),
            style={"max_width": "1180px", "margin": "0 auto", "padding": "0 1.5rem 4rem"},
        ),
        width="100%", min_height="100vh",
    )
