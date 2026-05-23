import reflex as rx
from ..state import AppState, PROGRAMAS_OPCIONES
from ..components import navbar, COLORES
from ..models import TipoPrograma, NivelEducativo


def campo_formulario(etiqueta: str, placeholder: str, var: rx.Var, handler, tipo: str = "text") -> rx.Component:
    return rx.vstack(
        rx.text(etiqueta, font_size="0.78rem", font_weight="600", color=COLORES["texto_suave"], letter_spacing="0.04em"),
        rx.input(
            placeholder=placeholder,
            value=var,
            on_change=handler,
            type=tipo,
            border="1.5px solid",
            border_color=COLORES["borde"],
            border_radius="8px",
            padding="10px 14px",
            font_size="0.9rem",
            color=COLORES["texto"],
            background=COLORES["superficie"],
            width="100%",
            _focus={
                "outline": "none",
                "border_color": COLORES["acento"],
                "box_shadow": f"0 0 0 3px {COLORES['acento']}22",
            },
        ),
        align_items="start",
        gap="6px",
        width="100%",
    )


def campo_select(etiqueta: str, opciones: list[str], var: rx.Var, handler) -> rx.Component:
    return rx.vstack(
        rx.text(etiqueta, font_size="0.78rem", font_weight="600", color=COLORES["texto_suave"], letter_spacing="0.04em"),
        rx.select(
            opciones,
            value=var,
            on_change=handler,
            border="1.5px solid",
            border_color=COLORES["borde"],
            border_radius="8px",
            padding="10px 14px",
            font_size="0.9rem",
            color=COLORES["texto"],
            background=COLORES["superficie"],
            width="100%",
            _focus={"outline": "none", "border_color": COLORES["acento"]},
        ),
        align_items="start",
        gap="6px",
        width="100%",
    )


def seccion_programa() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.text("PROGRAMA SOCIAL", font_size="0.7rem", font_weight="700", color=COLORES["texto_suave"], letter_spacing="0.1em"),
            margin_top="8px",
        ),
        campo_select(
            "Tipo de Programa *",
            PROGRAMAS_OPCIONES,
            AppState.tipo_programa_input,
            AppState.set_tipo_programa_input,
        ),
        rx.cond(
            AppState.es_programa_educativo,
            rx.vstack(
                campo_select(
                    "Nivel Educativo *",
                    AppState.niveles_educativos_permitidos,
                    AppState.nivel_educativo_input,
                    AppState.set_nivel_educativo_input,
                ),
                rx.cond(
                    AppState.es_rita_cetina,
                    campo_formulario(
                        "Número de estudiantes adicionales en el hogar",
                        "0 si solo hay uno (se suman $700 por cada estudiante extra)",
                        AppState.estudiantes_adicionales_input,
                        AppState.set_estudiantes_adicionales_input,
                        "number",
                    ),
                    rx.box(),
                ),
                gap="16px",
                width="100%",
            ),
            rx.box(),
        ),
        rx.box(
            rx.hstack(
                rx.text("ℹ", font_size="0.85rem", color=COLORES["acento"]),
                rx.cond(
                    AppState.tipo_programa_input == TipoPrograma.ADULTOS_MAYORES,
                    rx.text("Requiere edad ≥ 65 años derivada de la CURP · $6,000 bimestrales si se aprueba.",
                            font_size="0.75rem", color=COLORES["texto_suave"]),
                    rx.cond(
                        AppState.tipo_programa_input == TipoPrograma.BECA_RITA_CETINA,
                        rx.text("Requiere nivel Primaria o Secundaria · $1,900 base + $700 por estudiante adicional bimestrales.",
                                font_size="0.75rem", color=COLORES["texto_suave"]),
                        rx.cond(
                            AppState.tipo_programa_input == TipoPrograma.BECA_MEDIA_SUPERIOR,
                            rx.text("Requiere nivel Preparatoria/Bachillerato · $920 mensuales si se aprueba.",
                                    font_size="0.75rem", color=COLORES["texto_suave"]),
                            rx.text("Requiere nivel Universidad · $2,800 mensuales si se aprueba.",
                                    font_size="0.75rem", color=COLORES["texto_suave"]),
                        ),
                    ),
                ),
                gap="6px",
                align_items="flex-start",
            ),
            background="#EBF8FF",
            border_radius="8px",
            padding="10px 14px",
            width="100%",
        ),
        align_items="start",
        gap="16px",
        width="100%",
    )


def alerta_resultado() -> rx.Component:
    return rx.cond(
        AppState.mensaje_resultado != "",
        rx.box(
            rx.hstack(
                rx.cond(
                    AppState.tipo_mensaje == "success",
                    rx.text("✓", font_size="1.1rem", color="#276749"),
                    rx.cond(
                        AppState.tipo_mensaje == "warning",
                        rx.text("⚠", font_size="1.1rem", color="#744210"),
                        rx.text("✕", font_size="1.1rem", color="#9B2C2C"),
                    ),
                ),
                rx.text(AppState.mensaje_resultado, font_size="0.85rem", font_weight="500"),
                gap="10px",
                align_items="flex-start",
            ),
            background=rx.cond(
                AppState.tipo_mensaje == "success",
                "#C6F6D5",
                rx.cond(AppState.tipo_mensaje == "warning", "#FEEBC8", "#FED7D7"),
            ),
            border_radius="8px",
            padding="14px 16px",
            width="100%",
            margin_top="8px",
        ),
        rx.box(),
    )


def formulario_expediente() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.box(
            rx.vstack(
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.text("01", color=COLORES["acento"], font_size="0.7rem", font_weight="700"),
                            background=COLORES["primario"],
                            padding="6px 10px",
                            border_radius="6px",
                        ),
                        rx.vstack(
                            rx.text("Registro de Nuevo Expediente", font_size="1.4rem", font_weight="800", color=COLORES["texto"]),
                            rx.text(
                                "Complete los datos del solicitante y seleccione el programa social. El motor de reglas procesará la solicitud automáticamente.",
                                font_size="0.85rem",
                                color=COLORES["texto_suave"],
                            ),
                            align_items="start",
                            gap="2px",
                        ),
                        align_items="center",
                        gap="14px",
                    ),
                    width="100%",
                    padding_bottom="20px",
                    border_bottom="1px solid",
                    border_color=COLORES["borde"],
                ),
                seccion_programa(),
                rx.box(
                    rx.text("DATOS DE IDENTIDAD", font_size="0.7rem", font_weight="700", color=COLORES["texto_suave"], letter_spacing="0.1em"),
                    margin_top="8px",
                    border_top="1px solid",
                    border_color=COLORES["borde"],
                    padding_top="20px",
                    width="100%",
                ),
                rx.hstack(
                    campo_formulario("CURP *", "18 caracteres (ej. GOML800101HDFNZR09)", AppState.curp_input, AppState.set_curp_input),
                    campo_formulario("RFC *", "13 caracteres", AppState.rfc_input, AppState.set_rfc_input),
                    gap="20px",
                    width="100%",
                ),
                campo_formulario("Nombre Completo *", "Apellido Paterno Apellido Materno Nombre(s)", AppState.nombre_input, AppState.set_nombre_input),
                rx.hstack(
                    campo_formulario("Edad declarada", "En años", AppState.edad_input, AppState.set_edad_input, "number"),
                    campo_formulario("Código Postal", "5 dígitos", AppState.cp_input, AppState.set_cp_input),
                    gap="20px",
                    width="100%",
                ),
                rx.box(
                    rx.text("VALIDACIÓN BIOMÉTRICA", font_size="0.7rem", font_weight="700", color=COLORES["texto_suave"], letter_spacing="0.1em"),
                    margin_top="12px",
                ),
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("📷", font_size="1.5rem"),
                            rx.vstack(
                                rx.text("Puntaje de Coincidencia Facial", font_size="0.85rem", font_weight="600", color=COLORES["texto"]),
                                rx.text("Valor 0–100 generado por el módulo de face matching (simulado en MVP)", font_size="0.75rem", color=COLORES["texto_suave"]),
                                align_items="start",
                                gap="2px",
                            ),
                            align_items="center",
                            gap="12px",
                        ),
                        rx.input(
                            placeholder="Ej. 85.5  (≥80 aprueba | 60–79.9 revisión manual | <60 fraude)",
                            value=AppState.puntaje_biometrico_input,
                            on_change=AppState.set_puntaje_biometrico_input,
                            type="number",
                            border="1.5px solid",
                            border_color=COLORES["borde"],
                            border_radius="8px",
                            padding="10px 14px",
                            font_size="0.9rem",
                            width="100%",
                            _focus={"outline": "none", "border_color": COLORES["acento"]},
                        ),
                        align_items="start",
                        gap="12px",
                    ),
                    background="#F7FAFC",
                    border="1.5px dashed",
                    border_color=COLORES["borde"],
                    border_radius="10px",
                    padding="18px",
                    width="100%",
                ),
                alerta_resultado(),
                rx.hstack(
                    rx.button(
                        rx.cond(AppState.procesando, "Procesando...", "Enviar al Motor de Reglas →"),
                        on_click=AppState.procesar_expediente,
                        background=COLORES["primario"],
                        color="white",
                        padding="12px 28px",
                        border_radius="8px",
                        font_weight="700",
                        font_size="0.9rem",
                        cursor="pointer",
                        _hover={"background": "#1a3a5c"},
                        disabled=AppState.procesando,
                    ),
                    rx.link(
                        rx.button(
                            "Ver Panel →",
                            background="transparent",
                            color=COLORES["acento"],
                            border="2px solid",
                            border_color=COLORES["acento"],
                            padding="12px 24px",
                            border_radius="8px",
                            font_weight="700",
                            font_size="0.9rem",
                            cursor="pointer",
                        ),
                        href="/dashboard",
                    ),
                    gap="12px",
                    margin_top="8px",
                ),
                align_items="start",
                gap="16px",
                width="100%",
            ),
            background=COLORES["superficie"],
            border_radius="16px",
            padding="36px",
            max_width="780px",
            width="100%",
            box_shadow="0 4px 20px rgba(0,0,0,0.08)",
            border="1px solid",
            border_color=COLORES["borde"],
        ),
        background=COLORES["fondo"],
        min_height="100vh",
        align_items="center",
        gap="0",
        padding_bottom="48px",
    )
