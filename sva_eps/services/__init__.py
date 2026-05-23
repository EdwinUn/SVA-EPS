CURPS_FALLECIDOS = {"GOML800101HDFNZR09", "PERA750212MDFLRS04"}

LISTA_NEGRA_CURPS = set()

RFCS_SUSPENDIDOS = {"XAXX010101000", "GOML800101ABC"}


def consultar_renapo(curp: str) -> dict:
    if curp in CURPS_FALLECIDOS or curp in LISTA_NEGRA_CURPS:
        return {"baja_por_defuncion": True, "estatus": "Baja por Defunción"}
    return {"baja_por_defuncion": False, "estatus": "Activo"}


def consultar_sat(rfc: str) -> dict:
    if rfc in RFCS_SUSPENDIDOS:
        return {"estatus_fiscal": "Suspendido"}
    return {"estatus_fiscal": "Activo"}


def agregar_curp_lista_negra(curp: str):
    LISTA_NEGRA_CURPS.add(curp)
