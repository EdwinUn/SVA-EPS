from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class EstadoExpediente(str, Enum):
    APROBADO_AUTOMATICO = "Aprobado Automático"
    RECHAZADO_AUTOMATICO = "Rechazado Automático"
    PENDIENTE_REVISION = "Pendiente en Revisión Manual"


class TipoDocumento(str, Enum):
    INE = "Credencial de Elector (INE)"
    COMPROBANTE_DOMICILIO = "Comprobante de Domicilio"
    CONSTANCIA_FISCAL = "Constancia de Situación Fiscal (CSF)"


class EstatusVida(str, Enum):
    ACTIVO = "Activo"
    BAJA_DEFUNCION = "Baja por Defunción"


class TipoPrograma(str, Enum):
    ADULTOS_MAYORES = "Pensión para Adultos Mayores"
    BECA_RITA_CETINA = "Beca Rita Cetina (Educación Básica)"
    BECA_MEDIA_SUPERIOR = "Beca Media Superior (Benito Juárez)"
    BECA_SUPERIOR = "Beca Educación Superior (Jóvenes Escribiendo el Futuro)"


class NivelEducativo(str, Enum):
    PRIMARIA = "Primaria"
    SECUNDARIA = "Secundaria"
    PREPARATORIA = "Preparatoria/Bachillerato"
    UNIVERSIDAD = "Universidad"


@dataclass
class Ciudadano:
    curp: str
    rfc: str
    nombre_completo: str
    estatus_vida: str = EstatusVida.ACTIVO
    firma_biometrica: str = ""


@dataclass
class DocumentoDigital:
    tipo: str
    metadata_json: dict = field(default_factory=dict)
    id_documento: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ExpedienteSolicitud:
    curp: str
    nombre: str
    rfc: str
    edad: int
    codigo_postal: str
    puntaje_biometrico: float
    tipo_programa: str = TipoPrograma.ADULTOS_MAYORES
    nivel_educativo: str = ""
    estudiantes_adicionales: int = 0
    documentos: list = field(default_factory=list)
    folio: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    fecha_creacion: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    estado: str = EstadoExpediente.PENDIENTE_REVISION
    motivo_dictamen: str = ""
    monto_asignado: float = 0.0
    cobro_registrado: bool = False
