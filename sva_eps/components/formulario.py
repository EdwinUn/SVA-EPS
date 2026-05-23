"""Componentes del formulario ciudadano: upload INE + selfie + CURP + campos."""
from __future__ import annotations

import reflex as rx

from ..state import CiudadanoState
from .theme import GUINDA, DORADO, TINTA, TINTA_SUAVE

_INE_ID        = "ine_upload"
_SELFIE_ID     = "selfie_upload"
_CONSTANCIA_ID = "constancia_upload"
_CURP_ID       = "curp_upload"   # NUEVO


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


def _dropzone(label: str, sub: str, upload_id: str, handler, archivo, preview, icono: str) -> rx.Component:
    return rx.upload(
        rx.cond(
            preview != "",
            rx.vstack(
                rx.image(src=preview, width="100%", height="120px",
                         style={"object_fit": "cover", "border_radius": "10px"}),
                rx.hstack(
                    rx.icon("circle-check-big", size=15, color="#3d6b35"),
                    rx.text(archivo, style={"font_size": "0.75rem", "color": TINTA_SUAVE,
                                            "max_width": "150px", "overflow": "hidden",
                                            "text_overflow": "ellipsis", "white_space": "nowrap"}),
                    spacing="2", align="center",
                ),
                spacing="2", align="center", width="100%",
            ),
            rx.vstack(
                rx.icon(icono, size=30, color=GUINDA),
                rx.text(label, style={"font_weight": "500", "color": TINTA, "font_size": "0.92rem"}),
                rx.text(sub, style={"font_size": "0.74rem", "color": TINTA_SUAVE}),
                align="center", spacing="2",
            ),
        ),
        id=upload_id,
        accept={"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"]},
        max_files=1,
        multiple=False,
        on_drop=handler(rx.upload_files(upload_id=upload_id)),
        class_name="dropzone",
        padding="1.2rem 1rem",
        width="100%",
        style={"cursor": "pointer", "min_height": "150px",
               "display": "flex", "align_items": "center", "justify_content": "center"},
    )


def _dropzone_doc(label: str, sub: str, upload_id: str, handler, archivo: str, icono: str) -> rx.Component:
    """Dropzone para documentos (PDF/imagen) sin preview de imagen."""
    return rx.upload(
        rx.cond(
            archivo != "",
            rx.vstack(
                rx.icon("file-check", size=30, color="#3d6b35"),
                rx.text(archivo, style={"font_size": "0.78rem", "color": TINTA_SUAVE,
                                        "max_width": "170px", "overflow": "hidden",
                                        "text_overflow": "ellipsis", "white_space": "nowrap"}),
                rx.text("Archivo cargado ✓", style={"font_size": "0.72rem", "color": "#3d6b35",
                                                    "font_weight": "600"}),
                spacing="2", align="center", width="100%",
            ),
            rx.vstack(
                rx.icon(icono, size=30, color=GUINDA),
                rx.text(label, style={"font_weight": "500", "color": TINTA, "font_size": "0.92rem"}),
                rx.text(sub, style={"font_size": "0.74rem", "color": TINTA_SUAVE}),
                align="center", spacing="2",
            ),
        ),
        id=upload_id,
        accept={
            "image/png": [".png"],
            "image/jpeg": [".jpg", ".jpeg"],
            "application/pdf": [".pdf"],
        },
        max_files=1,
        multiple=False,
        on_drop=handler(rx.upload_files(upload_id=upload_id)),
        class_name="dropzone",
        padding="1.2rem 1rem",
        width="100%",
        style={"cursor": "pointer", "min_height": "150px",
               "display": "flex", "align_items": "center", "justify_content": "center"},
    )


def _bloque_curp_menor() -> rx.Component:
    """NUEVO: Dropzone obligatorio para CURP cuando el postulante es menor."""
    return rx.cond(
        CiudadanoState.requiere_curp_doc,
        rx.vstack(
            rx.hstack(
                rx.icon("baby", size=16, color=GUINDA),
                rx.text(
                    "Documento CURP obligatorio (menor de edad)",
                    style={"font_size": "0.82rem", "font_weight": "600", "color": GUINDA},
                ),
                spacing="2", align="center",
            ),
            rx.text(
                "Detectamos que el postulante es menor de 18 años. "
                "Sube la CURP oficial del Registro Nacional de Población.",
                style={"font_size": "0.76rem", "color": TINTA_SUAVE},
            ),
            _dropzone_doc(
                "Documento CURP",
                "Clic o arrastra · PDF/PNG/JPG · Máx 5 MB",
                _CURP_ID,
                CiudadanoState.subir_curp,
                CiudadanoState.archivo_curp,
                "file-badge",
            ),
            spacing="2", width="100%",
            style={"background": "rgba(165,127,44,0.06)", "border_radius": "12px",
                   "padding": "1rem", "border": "1px solid rgba(165,127,44,0.20)"},
        ),
    )


def _bloque_constancia_becas() -> rx.Component:
    """Dropzone para constancia de estudios (Rita Cetina / Benito Juárez)."""
    return rx.cond(
        CiudadanoState.requiere_constancia,
        rx.vstack(
            rx.hstack(
                rx.icon("graduation-cap", size=16, color=GUINDA),
                rx.text(
                    "Constancia de estudios requerida",
                    style={"font_size": "0.82rem", "font_weight": "600", "color": GUINDA},
                ),
                spacing="2", align="center",
            ),
            rx.text(
                "La beca solicitada requiere constancia oficial de inscripción "
                "emitida por la escuela.",
                style={"font_size": "0.76rem", "color": TINTA_SUAVE},
            ),
            _dropzone_doc(
                "Constancia de estudios",
                "Clic o arrastra · PDF/PNG/JPG",
                _CONSTANCIA_ID,
                CiudadanoState.subir_constancia,
                CiudadanoState.archivo_constancia,
                "file-text",
            ),
            spacing="2", width="100%",
            style={"background": "rgba(122,0,25,0.04)", "border_radius": "12px",
                   "padding": "1rem", "border": "1px solid rgba(122,0,25,0.15)"},
        ),
    )


def panel_captura() -> rx.Component:
    return rx.box(
        rx.vstack(
            _kicker("1", "Captura biométrica"),
            rx.text(
                "Sube tu identificación oficial y una selfie. La IA leerá tus datos "
                "y verificará tu rostro.",
                style={"color": TINTA_SUAVE, "font_size": "0.86rem"},
            ),
            rx.badge(
                rx.hstack(
                    rx.icon(rx.cond(CiudadanoState.ia_activa, "sparkles", "cpu"), size=13),
                    rx.text(CiudadanoState.badge_ia, style={"font_size": "0.7rem"}),
                    spacing="1", align="center",
                ),
                style={"background": "rgba(165,127,44,0.15)", "color": DORADO,
                       "border": "1px solid rgba(165,127,44,0.3)"},
            ),
            rx.grid(
                _dropzone("Identificación (INE)", "Clic o arrastra · PNG/JPG", _INE_ID,
                          CiudadanoState.subir_ine, CiudadanoState.archivo_ine,
                          CiudadanoState.preview_ine, "scan-line"),
                _dropzone("Selfie del solicitante", "Clic o arrastra · PNG/JPG", _SELFIE_ID,
                          CiudadanoState.subir_selfie, CiudadanoState.archivo_selfie,
                          CiudadanoState.preview_selfie, "camera"),
                columns="2", spacing="3", width="100%",
            ),
            # NUEVO: bloque CURP condicional (menores)
            _bloque_curp_menor(),
            # Existente: constancia de estudios para becas menores
            _bloque_constancia_becas(),
            rx.button(
                rx.cond(CiudadanoState.procesando_ocr,
                        rx.hstack(rx.spinner(size="2"), rx.text("Leyendo INE con IA..."), spacing="2"),
                        rx.hstack(rx.icon("wand-sparkles", size=17), rx.text("Extraer datos"), spacing="2")),
                on_click=CiudadanoState.extraer_datos,
                disabled=CiudadanoState.procesando_ocr | ~CiudadanoState.tiene_ine,
                class_name="btn-guinda",
                width="100%", size="3", margin_top="0.4rem",
            ),
            spacing="4", align="start", width="100%",
        ),
        class_name="card-paper rise rise-1",
        padding="1.7rem",
        width="100%",
    )


def _campo(label: str, value, on_change=None, disabled: bool = False) -> rx.Component:
    input_props = dict(
        value=value, disabled=disabled, placeholder="—",
        style={
            "width": "100%",
            "background": "white" if not disabled else "rgba(28,26,23,0.03)",
            "border": "1px solid rgba(28,26,23,0.15)",
            "border_radius": "10px", "padding": "0.6rem 0.8rem",
            "font_family": "'Geist', monospace" if label == "CURP" else "'Geist', sans-serif",
        },
    )
    if on_change is not None:
        input_props["on_change"] = on_change
    return rx.vstack(
        rx.text(label, style={"font_size": "0.72rem", "font_weight": "600",
                              "letter_spacing": "0.08em", "text_transform": "uppercase",
                              "color": TINTA_SUAVE}),
        rx.input(**input_props),
        spacing="1", width="100%", align="start",
    )


def _chip_servicio(nombre: str, activo: bool) -> rx.Component:
    color  = "#3d6b35" if activo else "#888"
    bg     = "rgba(61,107,53,0.10)" if activo else "rgba(28,26,23,0.06)"
    icono  = "circle-check-big" if activo else "circle-x"
    return rx.badge(
        rx.hstack(
            rx.icon(icono, size=12, color=color),
            rx.text(nombre, style={"font_size": "0.72rem", "color": color}),
            spacing="1", align="center",
        ),
        style={"background": bg, "border": f"1px solid {color}33",
               "border_radius": "20px", "padding": "0.25rem 0.6rem"},
    )


def panel_servicios() -> rx.Component:
    return rx.cond(
        (CiudadanoState.servicios_activos.length() > 0) | (CiudadanoState.servicios_inactivos.length() > 0),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("shield-check", size=18, color=GUINDA),
                    rx.text("Apoyos registrados", style={"font_family": "'Fraunces', serif",
                                                         "font_weight": "600", "font_size": "1rem",
                                                         "color": TINTA}),
                    spacing="2", align="center",
                ),
                rx.cond(
                    CiudadanoState.servicios_activos.length() > 0,
                    rx.vstack(
                        rx.text("Vigentes", style={"font_size": "0.72rem", "font_weight": "700",
                                                   "letter_spacing": "0.08em", "text_transform": "uppercase",
                                                   "color": "#3d6b35"}),
                        rx.flex(
                            rx.foreach(
                                CiudadanoState.servicios_activos_nombres,
                                lambda n: _chip_servicio(n, True),
                            ),
                            wrap="wrap", gap="0.4rem",
                        ),
                        spacing="2", align="start", width="100%",
                    ),
                ),
                rx.cond(
                    CiudadanoState.servicios_inactivos.length() > 0,
                    rx.vstack(
                        rx.text("Anteriores / cancelados",
                                style={"font_size": "0.72rem", "font_weight": "700",
                                       "letter_spacing": "0.08em", "text_transform": "uppercase",
                                       "color": "#888"}),
                        rx.flex(
                            rx.foreach(
                                CiudadanoState.servicios_inactivos_nombres,
                                lambda n: _chip_servicio(n, False),
                            ),
                            wrap="wrap", gap="0.4rem",
                        ),
                        spacing="2", align="start", width="100%",
                    ),
                ),
                spacing="3", align="start", width="100%",
            ),
            class_name="card-paper",
            padding="1.2rem 1.7rem",
            width="100%",
            style={"border_left": f"4px solid {GUINDA}"},
        ),
    )


def panel_datos() -> rx.Component:
    return rx.box(
        rx.vstack(
            _kicker("2", "Verificación de datos"),
            _campo("CURP", CiudadanoState.curp, CiudadanoState.set_curp),
            rx.cond(
                CiudadanoState.curp_duplicada,
                rx.box(
                    rx.hstack(
                        rx.icon("triangle-alert", size=15, color="#b3261e"),
                        rx.text("Esta CURP ya tiene un expediente. Envío bloqueado.",
                                style={"font_size": "0.78rem", "color": "#b3261e"}),
                        spacing="2", align="center",
                    ),
                    style={"background": "rgba(179,38,30,0.08)", "border_radius": "9px",
                           "padding": "0.5rem 0.7rem", "width": "100%"},
                ),
            ),
            panel_servicios(),
            _campo("Nombre completo", CiudadanoState.nombre, CiudadanoState.set_nombre),
            rx.grid(
                _campo("Edad", CiudadanoState.edad.to_string(), disabled=True),
                _campo("Sexo", CiudadanoState.sexo, disabled=True),
                columns="2", spacing="3", width="100%",
            ),
            rx.cond(
                CiudadanoState.requiere_rfc,
                rx.grid(
                    _campo("RFC", CiudadanoState.rfc, disabled=True),
                    _campo("Estado", CiudadanoState.estado_entidad, disabled=True),
                    columns="2", spacing="3", width="100%",
                ),
                rx.vstack(
                    _campo("Estado", CiudadanoState.estado_entidad, disabled=True),
                    rx.cond(
                        CiudadanoState.requiere_constancia,
                        rx.text(
                            "ℹ️ Beca estudiantil: no se solicita RFC. "
                            "La constancia de estudios se carga en el paso anterior.",
                            style={"font_size": "0.74rem", "color": TINTA_SUAVE,
                                   "font_style": "italic"},
                        ),
                        rx.text(
                            "ℹ️ Menor de edad: no se solicita RFC, pero sí el documento CURP.",
                            style={"font_size": "0.74rem", "color": TINTA_SUAVE,
                                   "font_style": "italic"},
                        ),
                    ),
                    spacing="2", width="100%",
                ),
            ),
            rx.hstack(
                rx.button(
                    rx.hstack(rx.icon("send", size=16), rx.text("Enviar expediente"), spacing="2"),
                    on_click=CiudadanoState.enviar_expediente,
                    disabled=~CiudadanoState.puede_enviar,
                    class_name="btn-guinda", size="3", width="100%",
                ),
                rx.button(
                    rx.icon("rotate-ccw", size=16),
                    on_click=CiudadanoState.reiniciar,
                    variant="outline", size="3",
                    style={"border_color": "rgba(28,26,23,0.2)", "color": TINTA},
                ),
                spacing="3", width="100%",
            ),
            spacing="3", align="start", width="100%",
        ),
        class_name="card-paper rise rise-2",
        padding="1.7rem",
        width="100%",
    )
