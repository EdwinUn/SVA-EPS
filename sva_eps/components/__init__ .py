from . import theme
from .navbar import navbar
from .workflow import workflow_stepper
from .sello import sello_inmutabilidad, panel_resultado
from .formulario import panel_captura, panel_datos
from .programa_card import programa_card
from .consulta import panel_consulta, panel_resultado_consulta   # NUEVO

__all__ = [
    "theme",
    "navbar",
    "workflow_stepper",
    "sello_inmutabilidad",
    "panel_resultado",
    "panel_captura",
    "panel_datos",
    "programa_card",
    "panel_consulta",
    "panel_resultado_consulta",
]
