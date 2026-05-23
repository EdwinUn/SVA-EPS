import reflex as rx
from ..state import AppState
from ..components import navbar, stat_card, estado_badge, COLORES
from ..models import EstadoExpediente


ICONOS_PROGRAMA = {
    "Pensión para Adultos Mayores": "👴",
    "Beca Rita Cetina (Educación Básica)": "📚",
    "Beca Media Superior (Benito Juárez)": "🎓",
    "Beca Educación Superior (Jóvenes Escribiendo el Futuro)": "🏛",
}


def chip_programa(tipo_programa: str) -> rx.Component:
    return rx.box(
        rx.text(tipo_programa, font_size="0.7rem", font_weight="600", color=COLORES["primario"]),
        background="#EBF8FF",
        padding="3px 10px",
        border_radius="20px",
        border="1px solid #BEE3F8",
    )


def monto_badge(exp: dict) -> rx.Component:
    return rx.cond(
        exp["estado"] == EstadoExpediente.APROBADO_AUTOMATICO,
        rx.box(
            rx.text(
                "$" + exp["monto_asignado"].to_string() + " MXN",
                font_size="0.7rem",
                font_weight="700",
                color="#276749",
            ),
            background="#C6F6D5",
            padding="3px 10px",
            border_radius="20px",
        ),
        rx.box(),
    )


def periodicidad_label(tipo_programa: str) -> str:
    """Retorna la etiqueta de periodicidad según el programa."""
    # Se resuelve en runtime via rx.cond en la UI
    return ""


def cobro_badge(exp: dict) -> rx.Component:
    """Muestra si el beneficiario ya cobró su periodo (bimestre o mes según programa)."""
    # Solo aplica a expedientes aprobados
    return rx.cond(
        exp["estado"] == EstadoExpediente.APROBADO_AUTOMATICO,
        rx.hstack(
            rx.cond(
                exp["cobro_registrado"],
                rx.box(
                    rx.hstack(
                        rx.text("✓", font_size="0.7rem", color="#276749", font_weight="800"),
                        rx.text(
                            rx.cond(
                                (exp["tipo_programa"] == "Beca Rita Cetina (Educación Básica)") |
                                (exp["tipo_programa"] == "Pensión para Adultos Mayores"),
                                "Bimestre cobrado",
                                "Mes cobrado",
                            ),
                            font_size="0.7rem", font_weight="700", color="#276749",
                        ),
                        gap="4px", align_items="center",
                    ),
                    background="#C6F6D5",
                    padding="3px 10px",
                    border_radius="20px",
                    border="1px solid #9AE6B4",
                ),
                rx.box(
                    rx.hstack(
                        rx.text("⏳", font_size="0.7rem"),
                        rx.text(
                            rx.cond(
                                (exp["tipo_programa"] == "Beca Rita Cetina (Educación Básica)") |
                                (exp["tipo_programa"] == "Pensión para Adultos Mayores"),
                                "Bimestre pendiente",
                                "Pago mensual pendiente",
                            ),
                            font_size="0.7rem", font_weight="700", color="#744210",
                        ),
                        gap="4px", align_items="center",
                    ),
                    background="#FEEBC8",
                    padding="3px 10px",
                    border_radius="20px",
                    border="1px solid #F6AD55",
                ),
            ),
            rx.cond(
                exp["cobro_registrado"],
                rx.button(
                    "↩ Desmarcar cobro",
                    on_click=AppState.desmarcar_cobro(exp["folio"]),
                    background="transparent",
                    color="#276749",
                    border="1px solid #9AE6B4",
                    font_size="0.72rem",
                    font_weight="600",
                    padding="4px 12px",
                    border_radius="6px",
                    cursor="pointer",
                    _hover={"background": "#F0FFF4"},
                ),
                rx.button(
                    "💳 Registrar cobro",
                    on_click=AppState.registrar_cobro(exp["folio"]),
                    background="#276749",
                    color="white",
                    font_size="0.72rem",
                    font_weight="600",
                    padding="4px 12px",
                    border_radius="6px",
                    cursor="pointer",
                    _hover={"background": "#22543d"},
                ),
            ),
            gap="8px",
            align_items="center",
            flex_wrap="wrap",
        ),
        rx.box(),
    )



def fila_expediente(exp: dict) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.text(
                            exp["folio"],
                            font_size="0.8rem",
                            font_weight="700",
                            color=COLORES["primario"],
                            font_family="monospace",
                            background="#EBF8FF",
                            padding="3px 8px",
                            border_radius="4px",
                        ),
                        estado_badge(exp["estado"]),
                        chip_programa(exp["tipo_programa"]),
                        monto_badge(exp),
                        gap="8px",
                        align_items="center",
                        flex_wrap="wrap",
                    ),
                    cobro_badge(exp),
                    rx.text(exp["nombre"], font_size="0.95rem", font_weight="600", color=COLORES["texto"]),
                    rx.hstack(
                        rx.text(exp["curp"], font_size="0.75rem", color=COLORES["texto_suave"], font_family="monospace"),
                        rx.text("·", color=COLORES["borde"]),
                        rx.text(exp["fecha_creacion"], font_size="0.75rem", color=COLORES["texto_suave"]),
                        rx.text("·", color=COLORES["borde"]),
                        rx.text(
                            "Biometría: " + exp["puntaje_biometrico"].to_string() + "%",
                            font_size="0.75rem",
                            color=COLORES["texto_suave"],
                        ),
                        gap="6px",
                        flex_wrap="wrap",
                    ),
                    align_items="start",
                    gap="6px",
                    flex="1",
                ),
                rx.cond(
                    exp["estado"] == EstadoExpediente.PENDIENTE_REVISION,
                    rx.hstack(
                        rx.button(
                            "Aprobar",
                            on_click=AppState.aprobar_manual(exp["folio"]),
                            background="#276749",
                            color="white",
                            font_size="0.78rem",
                            font_weight="600",
                            padding="8px 16px",
                            border_radius="6px",
                            cursor="pointer",
                            _hover={"background": "#22543d"},
                        ),
                        rx.button(
                            "Rechazar",
                            on_click=AppState.rechazar_manual(exp["folio"]),
                            background="#9B2C2C",
                            color="white",
                            font_size="0.78rem",
                            font_weight="600",
                            padding="8px 16px",
                            border_radius="6px",
                            cursor="pointer",
                            _hover={"background": "#742a2a"},
                        ),
                        gap="8px",
                    ),
                    rx.box(),
                ),
                align_items="flex-start",
                width="100%",
                gap="16px",
            ),
            rx.box(
                rx.text(
                    exp["motivo_dictamen"],
                    font_size="0.78rem",
                    color=COLORES["texto_suave"],
                    font_style="italic",
                ),
                width="100%",
                padding_top="8px",
                border_top="1px solid",
                border_color=COLORES["borde"],
            ),
            align_items="start",
            gap="10px",
            width="100%",
        ),
        background=COLORES["superficie"],
        border="1px solid",
        border_color=COLORES["borde"],
        border_radius="10px",
        padding="18px 20px",
        width="100%",
        _hover={"box_shadow": "0 2px 12px rgba(0,0,0,0.07)"},
        transition="box_shadow 0.2s",
    )


def filtro_tabs() -> rx.Component:
    opciones = [
        ("Todos", "Todos"),
        (EstadoExpediente.APROBADO_AUTOMATICO, "Aprobados"),
        (EstadoExpediente.RECHAZADO_AUTOMATICO, "Rechazados"),
        (EstadoExpediente.PENDIENTE_REVISION, "Revisión Manual"),
    ]

    def tab_btn(valor, etiqueta):
        return rx.button(
            etiqueta,
            on_click=AppState.set_filtro(valor),
            background=rx.cond(AppState.filtro_estado == valor, COLORES["primario"], "transparent"),
            color=rx.cond(AppState.filtro_estado == valor, "white", COLORES["texto_suave"]),
            border="1.5px solid",
            border_color=rx.cond(AppState.filtro_estado == valor, COLORES["primario"], COLORES["borde"]),
            border_radius="6px",
            padding="7px 16px",
            font_size="0.8rem",
            font_weight="600",
            cursor="pointer",
        )

    return rx.hstack(
        *[tab_btn(v, e) for v, e in opciones],
        gap="8px",
        flex_wrap="wrap",
    )


def stat_monto(total: rx.Var) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("💰", font_size="1.5rem"),
                rx.spacer(),
                rx.box(width="4px", height="40px", background=COLORES["acento"], border_radius="2px"),
            ),
            rx.text(
                "$" + total.to_string() + " MXN",
                font_size="1.5rem",
                font_weight="800",
                color=COLORES["texto"],
            ),
            rx.text("Monto Total Comprometido", font_size="0.75rem", color=COLORES["texto_suave"], font_weight="500", letter_spacing="0.05em"),
            align_items="start",
            gap="8px",
            width="100%",
        ),
        background=COLORES["superficie"],
        border="1px solid",
        border_color=COLORES["borde"],
        border_radius="12px",
        padding="20px",
        flex="1",
        box_shadow="0 1px 4px rgba(0,0,0,0.06)",
    )


def dashboard() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Panel del Operador Administrativo", font_size="1.4rem", font_weight="800", color=COLORES["texto"]),
                        rx.text(
                            "Vista tripartita de expedientes: aprobados, rechazados y en revisión manual.",
                            font_size="0.85rem",
                            color=COLORES["texto_suave"],
                        ),
                        align_items="start",
                        gap="4px",
                    ),
                    rx.spacer(),
                    rx.link(
                        rx.button(
                            "+ Nuevo Expediente",
                            background=COLORES["acento"],
                            color="white",
                            padding="10px 20px",
                            border_radius="8px",
                            font_weight="700",
                            font_size="0.85rem",
                            cursor="pointer",
                        ),
                        href="/",
                    ),
                    width="100%",
                    align_items="flex-start",
                ),
                rx.hstack(
                    stat_card("Total Expedientes", AppState.expedientes.length(), COLORES["primario"], "📁"),
                    stat_card("Aprobados", AppState.total_aprobados, COLORES["acento"], "✅"),
                    stat_card("Rechazados", AppState.total_rechazados, COLORES["peligro"], "❌"),
                    stat_card("Revisión Manual", AppState.total_revision, COLORES["alerta"], "⏳"),
                    stat_monto(AppState.monto_total_comprometido),
                    gap="16px",
                    width="100%",
                    flex_wrap="wrap",
                ),
                rx.box(
                    rx.hstack(
                        rx.text("Expedientes", font_size="1rem", font_weight="700", color=COLORES["texto"]),
                        rx.spacer(),
                        filtro_tabs(),
                        width="100%",
                        align_items="center",
                        flex_wrap="wrap",
                        gap="12px",
                    ),
                    padding_bottom="16px",
                    width="100%",
                    border_bottom="1px solid",
                    border_color=COLORES["borde"],
                ),
                rx.cond(
                    AppState.expedientes_filtrados.length() == 0,
                    rx.box(
                        rx.vstack(
                            rx.text("📭", font_size="2.5rem"),
                            rx.text("Sin expedientes en esta categoría", font_size="0.9rem", color=COLORES["texto_suave"], font_weight="500"),
                            rx.link(
                                rx.text("Registrar el primero →", color=COLORES["acento"], font_size="0.85rem", font_weight="600"),
                                href="/",
                            ),
                            align_items="center",
                            gap="8px",
                        ),
                        padding="48px",
                        width="100%",
                        text_align="center",
                    ),
                    rx.vstack(
                        rx.foreach(AppState.expedientes_filtrados, fila_expediente),
                        gap="12px",
                        width="100%",
                    ),
                ),
                align_items="start",
                gap="24px",
                width="100%",
            ),
            max_width="1100px",
            width="100%",
            padding="36px 24px",
        ),
        background=COLORES["fondo"],
        min_height="100vh",
        align_items="center",
        gap="0",
    )
