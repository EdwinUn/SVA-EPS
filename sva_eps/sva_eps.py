import reflex as rx
from .pages.ingesta import formulario_expediente
from .pages.dashboard import dashboard


app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;600&display=swap",
    ],
    style={
        "font_family": "'IBM Plex Sans', sans-serif",
        "background": "#F0F4F8",
        "margin": "0",
        "padding": "0",
    },
)

app.add_page(formulario_expediente, route="/")
app.add_page(dashboard, route="/dashboard")
