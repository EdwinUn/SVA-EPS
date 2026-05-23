"""Módulo de Consulta: panel para verificar estatus de un apoyo."""
from __future__ import annotations

import reflex as rx

from ..state.consulta_state import ConsultaState
from .theme import GUINDA, DORADO, TINTA, TINTA_SUAVE, VERDE, ROJO, AMBAR

_INE_CONSULTA_ID = "ine_consulta_upload"


def _kicker(num: str, texto: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            num,
            style={
                "font_family": "'Fraunces', serif", "font_weight": "900",
                "font_size": "0.9rem", "color": "white",
                "background": GUINDA, "border_radius": "50%",
                "width": "26px", "height": "26px", "display": "flex",
                "align_items": "center", "justify_content": "center",
            },
        ),
        rx.text(texto, style={"font_family": "'Fraunces', serif",
                              "font_weight": "600", "font_size": "1.15rem",
                              "color": TINTA}),
        spacing="3", align="center",
    )


def _dropzone_ine_consulta() -> rx.Component:
    return rx.upload(
        rx.cond(
            ConsultaState.preview_ine_consulta != "",
            rx.vstack(
                rx.image(
                    src=ConsultaState.preview_ine_consulta,
                    width="100%", height="140px",
                    style={"object_fit": "cover", "border_radius": "10px"},
                ),
                rx.hstack(
                    rx.icon("circle-check-big", size=15, color=VERDE),
                    rx.text(
                        ConsultaState.archivo_ine_consulta,
                        style={"font_size": "0.75rem", "color": TINTA_SUAVE,
                               "max_width": "240px", "overflow": "hidden",
                               "text_overflow": "ellipsis", "white_space": "nowrap"},
                    ),
                    spacing="2", align="center",
                ),
                spacing="2", align="center", width="100%",
            ),
            rx.vstack(
                rx.icon("scan-line", size=32, color=GUINDA),
                rx.text("Sube tu INE",
                        style={"font_weight": "500", "color": TINTA, "font_size": "0.95rem"}),
                rx.text("Clic o arrastra · PNG/JPG",
                        style={"font_size": "0.74rem", "color": TINTA_SUAVE}),
                align="center", spacing="2",
            ),
        ),
        id=_INE_CONSULTA_ID,
        accept={"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"]},
        max_files=1,
        multiple=False,
        on_drop=ConsultaState.subir_ine_consulta(
            rx.upload_files(upload_id=_INE_CONSULTA_ID)
        ),
        class_name="dropzone",
        padding="1.4rem 1rem",
        width="100%",
        style={"cursor": "pointer", "min_height": "170px",
               "display": "flex", "align_items": "center", "justify_content": "center"},
    )


def _datos_identificados() -> rx.Component:
    """Muestra los datos extraídos del INE (read-only)."""
    return rx.cond(
        ConsultaState.datos_extraidos,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("badge-check", size=16, color=VERDE),
                    rx.text("Identidad verificada",
                            style={"font_size": "0.78rem", "font_weight": "700",
                                   "letter_spacing": "0.06em", "text_transform": "uppercase",
                                   "color": VERDE}),
                    spacing="2", align="center",
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Nombre", style={"font_size": "0.68rem",
                                                 "letter_spacing": "0.08em",
                                                 "text_transform": "uppercase",
                                                 "color": TINTA_SUAVE}),
                        rx.text(ConsultaState.nombre_consultado,
                                style={"font_weight": "600", "color": TINTA}),
                        spacing="0", align="start",
                    ),
                    rx.vstack(
                        rx.text("CURP", style={"font_size": "0.68rem",
                                               "letter_spacing": "0.08em",
                                               "text_transform": "uppercase",
                                               "color": TINTA_SUAVE}),
                        rx.text(ConsultaState.curp_consultada,
                                style={"font_family": "'Geist', monospace",
                                       "font_weight": "600", "color": TINTA,
                                       "font_size": "0.85rem"}),
                        spacing="0", align="start",
                    ),
                    columns="2", spacing="3", width="100%",
                ),
                spacing="3", align="start", width="100%",
            ),
            style={
                "background": "rgba(61,107,53,0.06)",
                "border": f"1px solid {VERDE}33",
                "border_radius": "12px",
                "padding": "0.9rem 1.1rem",
                "width": "100%",
            },
        ),
    )


def _selector_programa() -> rx.Component:
    return rx.vstack(
        rx.text("Programa a consultar",
                style={"font_size": "0.72rem", "font_weight": "600",
                       "letter_spacing": "0.08em", "text_transform": "uppercase",
                       "color": TINTA_SUAVE}),
        rx.select(
            ConsultaState.nombres_programas,
            placeholder="Selecciona un apoyo...",
            value=ConsultaState.nombre_programa_seleccionado,
            on_change=ConsultaState.set_programa,
            disabled=~ConsultaState.datos_extraidos,
            width="100%",
            size="3",
        ),
        rx.cond(
            ~ConsultaState.datos_extraidos,
            rx.text("Primero identifícate cargando tu INE.",
                    style={"font_size": "0.74rem", "color": TINTA_SUAVE,
                           "font_style": "italic"}),
        ),
        spacing="2", width="100%", align="start",
    )


def _resultado_consulta() -> rx.Component:
    """Tarjeta con el dictamen visual del estatus."""
    return rx.cond(
        ConsultaState.consulta_realizada,
        rx.box(
            # VIGENTE — verde
            rx.cond(
                ConsultaState.es_vigente,
                rx.vstack(
                    rx.hstack(
                        rx.icon("shield-check", size=28, color=VERDE),
                        rx.vstack(
                            rx.text("VIGENTE", style={"font_family": "'Fraunces', serif",
                                                      "font_weight": "900",
                                                      "font_size": "1.8rem",
                                                      "color": VERDE,
                                                      "letter_spacing": "0.04em"}),
                            rx.text("Apoyo activo confirmado",
                                    style={"font_size": "0.78rem", "color": TINTA_SUAVE}),
                            spacing="0", align="start",
                        ),
                        spacing="3", align="center",
                    ),
                    rx.text(ConsultaState.mensaje_resultado,
                            style={"color": TINTA, "font_size": "0.92rem",
                                   "line_height": "1.5"}),
                    spacing="3", align="start", width="100%",
                ),
            ),
            # INACTIVO — ámbar
            rx.cond(
                ConsultaState.es_inactivo,
                rx.vstack(
                    rx.hstack(
                        rx.icon("circle-pause", size=28, color=AMBAR),
                        rx.vstack(
                            rx.text("INACTIVO", style={"font_family": "'Fraunces', serif",
                                                       "font_weight": "900",
                                                       "font_size": "1.8rem",
                                                       "color": AMBAR,
                                                       "letter_spacing": "0.04em"}),
                            rx.text("Apoyo cancelado o anterior",
                                    style={"font_size": "0.78rem", "color": TINTA_SUAVE}),
                            spacing="0", align="start",
                        ),
                        spacing="3", align="center",
                    ),
                    rx.text(ConsultaState.mensaje_resultado,
                            style={"color": TINTA, "font_size": "0.92rem",
                                   "line_height": "1.5"}),
                    spacing="3", align="start", width="100%",
                ),
            ),
            # NO_REGISTRADO — guinda suave
            rx.cond(
                ConsultaState.es_no_registrado,
                rx.vstack(
                    rx.hstack(
                        rx.icon("circle-help", size=28, color=GUINDA),
                        rx.vstack(
                            rx.text("NO REGISTRADO",
                                    style={"font_family": "'Fraunces', serif",
                                           "font_weight": "900", "font_size": "1.5rem",
                                           "color": GUINDA, "letter_spacing": "0.04em"}),
                            rx.text("Sin expediente para este apoyo",
                                    style={"font_size": "0.78rem", "color": TINTA_SUAVE}),
                            spacing="0", align="start",
                        ),
                        spacing="3", align="center",
                    ),
                    rx.text(ConsultaState.mensaje_resultado,
                            style={"color": TINTA, "font_size": "0.92rem",
                                   "line_height": "1.5"}),
                    rx.link(
                        rx.button(
                            rx.hstack(
                                rx.icon("file-plus", size=15),
                                rx.text("Iniciar postulación"),
                                spacing="2",
                            ),
                            class_name="btn-guinda", size="2",
                        ),
                        href="/",
                        style={"text_decoration": "none"},
                    ),
                    spacing="3", align="start", width="100%",
                ),
            ),
            class_name="card-paper rise rise-2",
            padding="1.5rem 1.7rem",
            width="100%",
        ),
    )


def panel_consulta() -> rx.Component:
    """Panel principal del módulo de consulta."""
    return rx.box(
        rx.vstack(
            # Paso 1: Subir INE
            _kicker("1", "Identifícate"),
            rx.text(
                "Sube tu identificación oficial para verificar tu identidad.",
                style={"color": TINTA_SUAVE, "font_size": "0.86rem"},
            ),
            _dropzone_ine_consulta(),
            rx.button(
                rx.cond(
                    ConsultaState.procesando_ocr,
                    rx.hstack(rx.spinner(size="2"), rx.text("Leyendo INE..."), spacing="2"),
                    rx.hstack(rx.icon("scan-search", size=17), rx.text("Identificar"), spacing="2"),
                ),
                on_click=ConsultaState.identificar,
                disabled=ConsultaState.procesando_ocr | ~ConsultaState.tiene_ine,
                class_name="btn-guinda",
                width="100%", size="3",
            ),
            _datos_identificados(),

            # Paso 2: Seleccionar programa
            rx.divider(margin_y="0.5rem"),
            _kicker("2", "Selecciona el apoyo"),
            _selector_programa(),

            # Paso 3: Consultar
            rx.button(
                rx.cond(
                    ConsultaState.consultando,
                    rx.hstack(rx.spinner(size="2"),
                              rx.text("Consultando expediente..."), spacing="2"),
                    rx.hstack(rx.icon("search", size=17),
                              rx.text("Consultar estatus"), spacing="2"),
                ),
                on_click=ConsultaState.consultar_estatus,
                disabled=~ConsultaState.puede_consultar,
                class_name="btn-guinda",
                width="100%", size="3", margin_top="0.4rem",
            ),
            rx.button(
                rx.hstack(rx.icon("rotate-ccw", size=15),
                          rx.text("Nueva consulta"), spacing="2"),
                on_click=ConsultaState.reiniciar_consulta,
                variant="outline", size="2",
                style={"border_color": "rgba(28,26,23,0.2)", "color": TINTA_SUAVE,
                       "margin_top": "0.2rem"},
            ),
            spacing="4", align="start", width="100%",
        ),
        class_name="card-paper rise rise-1",
        padding="1.7rem",
        width="100%",
    )


def panel_resultado_consulta() -> rx.Component:
    """Panel lateral con el resultado del dictamen."""
    return rx.vstack(
        _resultado_consulta(),
        rx.cond(
            ~ConsultaState.consulta_realizada,
            rx.box(
                rx.vstack(
                    rx.icon("file-search", size=40, color="rgba(157,36,73,0.25)"),
                    rx.text("El estatus de tu apoyo aparecerá aquí",
                            style={"color": TINTA_SUAVE, "font_size": "0.9rem",
                                   "text_align": "center"}),
                    spacing="3", align="center",
                ),
                class_name="card-paper",
                style={"padding": "3rem 1.5rem", "width": "100%",
                       "display": "flex", "justify_content": "center",
                       "border_style": "dashed", "background": "transparent"},
            ),
        ),
        spacing="4", width="100%",
    )
