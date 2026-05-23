from __future__ import annotations

import reflex as rx

from ..components import navbar
from ..components.theme import GUINDA, DORADO, VERDE, ROJO, AMBAR, TINTA, TINTA_SUAVE
from ..models import Expediente, Dictamen
# En pages/admin.py
from ..state.admin_state import AdminState 

# No importes el archivo padre o el init que pueda causar bucles

def _metrica(label: str, valor, color: str, icono: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(rx.icon(icono, size=20, color=color),
                   style={"background": f"{color}1a", "border_radius": "11px",
                          "padding": "0.6rem", "display": "flex"}),
            rx.vstack(
                rx.text(valor.to_string(),
                        style={"font_family": "'Fraunces', serif", "font_weight": "900",
                               "font_size": "1.7rem", "color": TINTA, "line_height": "1"}),
                rx.text(label, style={"font_size": "0.74rem", "color": TINTA_SUAVE}),
                spacing="1", align="start",
            ),
            spacing="3", align="center",
        ),
        class_name="card-paper", style={"padding": "1.1rem 1.3rem"},
    )

def _badge(dictamen: str) -> rx.Component:
    color = rx.match(dictamen,
                     (Dictamen.APROBADO, VERDE), (Dictamen.RECHAZADO, ROJO),
                     (Dictamen.REVISION, AMBAR), TINTA_SUAVE)
    return rx.badge(dictamen, style={"background": rx.color_mode_cond("white", "white"),
                                     "color": color, "border": f"1px solid {color}",
                                     "font_weight": "600"})

def _fila(exp: Expediente) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(exp.folio, style={"font_weight": "600", "color": GUINDA})),
        rx.table.cell(rx.text(exp.curp, style={"font_family": "monospace", "font_size": "0.8rem"})),
        rx.table.cell(exp.nombre),
        rx.table.cell(exp.estado),
        rx.table.cell(rx.text(exp.score_biometrico.to_string() + "%")),
        rx.table.cell(_badge(exp.dictamen)),
        rx.table.cell(rx.text(exp.programa_recomendado, style={"font_size": "0.78rem", "max_width": "180px"})),
        rx.table.cell(
            rx.tooltip(
                rx.text(exp.sello_hash[:10] + "…", style={"font_family": "monospace", "font_size": "0.75rem", "color": VERDE}),
                content=exp.sello_hash,
            ),
        ),
        style={"_hover": {"background": "rgba(157,36,73,0.03)"}},
    )

@rx.page(route="/admin", on_load=AdminState.cargar_expedientes)
def admin_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.vstack(
                rx.text("Panel de control", class_name="kicker"),
                rx.heading("Consola de auditoría",
                           style={"font_family": "'Fraunces', serif", "font_weight": "900",
                                  "font_size": "clamp(1.7rem, 4vw, 2.4rem)", "color": TINTA}),
                spacing="2", align="start", padding_y="2rem",
            ),
            rx.grid(
                _metrica("Total expedientes", AdminState.total, GUINDA, "files"),
                _metrica("Aprobados", AdminState.total_aprobados, VERDE, "circle-check-big"),
                _metrica("Rechazados", AdminState.total_rechazados, ROJO, "circle-x"),
                _metrica("Revisión (10%)", AdminState.total_revision, AMBAR, "circle-alert"),
                columns=rx.breakpoints(initial="2", md="4"),
                spacing="3", width="100%",
            ),
            rx.box(
                rx.input(
                    rx.input.slot(rx.icon("search", size=16)),
                    placeholder="Buscar por CURP o nombre…",
                    value=AdminState.busqueda,
                    on_change=AdminState.set_busqueda,
                    size="3",
                    style={"background": "white", "border_radius": "12px", "width": "100%"},
                ),
                margin="1.5rem 0",
            ),
            rx.box(
                rx.cond(
                    AdminState.expedientes_filtrados.length() > 0,
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Folio"),
                                rx.table.column_header_cell("CURP"),
                                rx.table.column_header_cell("Nombre"),
                                rx.table.column_header_cell("Estado"),
                                rx.table.column_header_cell("Biometría"),
                                rx.table.column_header_cell("Dictamen"),
                                rx.table.column_header_cell("Programa"),
                                rx.table.column_header_cell("Sello"),
                            ),
                        ),
                        rx.table.body(rx.foreach(AdminState.expedientes_filtrados, _fila)),
                        width="100%",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.icon("inbox", size=36, color="rgba(157,36,73,0.25)"),
                            rx.text("Aún no hay expedientes que coincidan.",
                                    style={"color": TINTA_SUAVE}),
                            spacing="3", align="center",
                        ),
                        style={"padding": "3rem", "display": "flex", "justify_content": "center"},
                    ),
                ),
                class_name="card-paper",
                style={"padding": "0.5rem", "width": "100%", "overflow_x": "auto"},
            ),
            style={"max_width": "1180px", "margin": "0 auto", "padding": "0 1.5rem 4rem"},
        ),
        width="100%", min_height="100vh",
    )
