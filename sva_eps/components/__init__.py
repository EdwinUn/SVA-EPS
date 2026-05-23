import reflex as rx
from ..models import EstadoExpediente


COLORES = {
    "primario": "#0A2540",
    "acento": "#00C896",
    "alerta": "#F5A623",
    "peligro": "#E53E3E",
    "fondo": "#F0F4F8",
    "superficie": "#FFFFFF",
    "texto": "#1A202C",
    "texto_suave": "#718096",
    "borde": "#E2E8F0",
}


def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.box(
                    rx.text("SVA", color=COLORES["acento"], font_weight="800", font_size="1.1rem"),
                    rx.text("EPS", color="white", font_weight="800", font_size="1.1rem"),
                    display="flex",
                    gap="2px",
                ),
                rx.vstack(
                    rx.text(
                        "Sistema de Validación Automatizada",
                        color="white",
                        font_size="0.65rem",
                        font_weight="500",
                        letter_spacing="0.08em",
                        line_height="1",
                    ),
                    rx.text(
                        "Expedientes y Programas Sociales",
                        color=COLORES["acento"],
                        font_size="0.6rem",
                        font_weight="400",
                        letter_spacing="0.06em",
                        line_height="1",
                    ),
                    gap="2px",
                    align_items="start",
                ),
                align_items="center",
                gap="12px",
            ),
            rx.spacer(),
            rx.hstack(
                rx.link("Nuevo Expediente", href="/", color="white", font_size="0.85rem", opacity="0.8"),
                rx.link("Panel Operador", href="/dashboard", color="white", font_size="0.85rem", opacity="0.8"),
                gap="24px",
            ),
            align_items="center",
            width="100%",
        ),
        background=COLORES["primario"],
        padding="16px 32px",
        width="100%",
        box_shadow="0 2px 8px rgba(0,0,0,0.15)",
    )


def stat_card(titulo: str, valor: rx.Var, color_acento: str, icono: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(icono, font_size="1.5rem"),
                rx.spacer(),
                rx.box(width="4px", height="40px", background=color_acento, border_radius="2px"),
            ),
            rx.text(valor, font_size="2rem", font_weight="800", color=COLORES["texto"]),
            rx.text(titulo, font_size="0.75rem", color=COLORES["texto_suave"], font_weight="500", letter_spacing="0.05em"),
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


def estado_badge(estado: str) -> rx.Component:
    return rx.cond(
        estado == EstadoExpediente.APROBADO_AUTOMATICO,
        rx.box(
            rx.text("✓ " + EstadoExpediente.APROBADO_AUTOMATICO, font_size="0.7rem", font_weight="600", color="#276749"),
            background="#C6F6D5",
            padding="4px 10px",
            border_radius="20px",
        ),
        rx.cond(
            estado == EstadoExpediente.RECHAZADO_AUTOMATICO,
            rx.box(
                rx.text("✕ " + EstadoExpediente.RECHAZADO_AUTOMATICO, font_size="0.7rem", font_weight="600", color="#9B2C2C"),
                background="#FED7D7",
                padding="4px 10px",
                border_radius="20px",
            ),
            rx.box(
                rx.text("⏳ " + EstadoExpediente.PENDIENTE_REVISION, font_size="0.7rem", font_weight="600", color="#744210"),
                background="#FEEBC8",
                padding="4px 10px",
                border_radius="20px",
            ),
        ),
    )
