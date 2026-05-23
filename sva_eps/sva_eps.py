import reflex as rx
from .models.expediente import Expediente

from .pages.ciudadano import ciudadano_page
from .pages.admin import admin_page
from .pages.programas import programas_page
from .pages.consulta import consulta_page   # NUEVO

app = rx.App(theme=rx.theme(appearance="light"))
app.add_page(ciudadano_page, route="/",          title="SVA-EPS · Solicitud de apoyo")
app.add_page(consulta_page,  route="/consulta",  title="SVA-EPS · Consulta de estatus")
app.add_page(programas_page, route="/programas", title="SVA-EPS · Programas")
app.add_page(admin_page,     route="/admin",     title="SVA-EPS · Auditoría")
