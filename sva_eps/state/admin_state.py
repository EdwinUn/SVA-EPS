from __future__ import annotations
import reflex as rx
from sqlmodel import select
from ..models.expediente import Expediente

class AdminState(rx.State):
    busqueda: str = ""
    expedientes: list[Expediente] = []

    def cargar_expedientes(self):
        with rx.session() as session:
            # Esta consulta es la más compatible con SQLModel en Reflex
            self.expedientes = session.exec(select(Expediente)).all()

    # ... resto de tus métodos ...

    # ... el resto de tus métodos ...
    @rx.var
    def expedientes_filtrados(self) -> list[Expediente]:
        q = (self.busqueda or "").strip().lower()
        if not q:
            return self.expedientes
        return [
            e for e in self.expedientes
            if (e.curp and q in e.curp.lower()) or (e.nombre and q in e.nombre.lower())
        ]

    @rx.var
    def total(self) -> int:
        return len(self.expedientes)

    @rx.var
    def total_aprobados(self) -> int:
        return sum(1 for e in self.expedientes if e.dictamen == "APROBADO")

    @rx.var
    def total_rechazados(self) -> int:
        return sum(1 for e in self.expedientes if e.dictamen == "RECHAZADO")

    @rx.var
    def total_revision(self) -> int:
        return sum(1 for e in self.expedientes if e.dictamen == "REVISIÓN MANUAL")

    def set_busqueda(self, value: str):
        self.busqueda = value