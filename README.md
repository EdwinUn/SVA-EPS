# SVA-EPS — Sistema de Validación Automatizada de Expedientes y Programas Sociales

> Plataforma web que automatiza la recepción, auditoría y dictamen de expedientes ciudadanos para la asignación de apoyos federales (Programas para el Bienestar). Desarrollada para el hackathon **Hackatec 2025**.

---

## Tabla de Contenidos

1. [¿Qué hace esta aplicación?](#qué-hace-esta-aplicación)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Uso de la Aplicación](#uso-de-la-aplicación)
6. [Base de Datos](#base-de-datos)
7. [Servicios Clave](#servicios-clave)
8. [Programas Sociales Cubiertos](#programas-sociales-cubiertos)
9. [Variables de Entorno](#variables-de-entorno)

---

## ¿Qué hace esta aplicación?

SVA-EPS automatiza el proceso de validación de expedientes para programas sociales federales bajo una **regla de eficiencia 90/10**:

- **90 %** de los expedientes se aprueban o rechazan automáticamente mediante:
  - OCR del INE (real con Tesseract, o con visión IA vía Groq)
  - Consulta simulada a RENAPO (detección de estatus de defunción)
  - Cotejo biométrico facial INE vs. selfie (DeepFace o simulado)
  - Motor de reglas de elegibilidad por programa

- **10 %** dudoso pasa a una consola de revisión manual para el operador.

Adicionalmente genera un **Sello de Inmutabilidad SHA-256** por expediente, garantizando trazabilidad y auditoría.

---

## Stack Tecnológico

| Categoría | Tecnología | Versión / Detalle |
|---|---|---|
| **Framework Web** | [Reflex](https://reflex.dev) | 0.8.26 — Full-stack Python, UI reactiva con WebSockets |
| **Lenguaje** | Python | 3.12 / 3.13 |
| **Base de Datos** | PostgreSQL (Supabase) | Hosted en AWS us-west-2 |
| **ORM / Modelos** | SQLModel + SQLAlchemy | Integrado en Reflex vía `rx.Model` |
| **IA — OCR y Dictamen** | [Groq API](https://console.groq.com) | Llama 4 Scout (visión) + Llama 3.3 70B (texto) |
| **OCR de respaldo** | Tesseract OCR + pytesseract | Motor local en español (`spa`) |
| **Procesamiento de imágenes** | Pillow (PIL) | Preprocesamiento de INE antes del OCR |
| **Biometría Facial** | DeepFace (opcional) | Facenet512 + RetinaFace (cosine distance) |
| **Criptografía / Firma** | hashlib (stdlib) | SHA-256 — Sello de Inmutabilidad del expediente |
| **Tipografía** | Google Fonts | Fraunces (display editorial) + Geist Sans (UI) |
| **Paleta Institucional** | CSS Variables | Guinda `#9d2449`, Dorado `#a57f2c`, Papel `#f7f3ec` |
| **Migraciones DB** | Alembic | Gestionado por Reflex automáticamente |
| **Gestión de entorno** | Python venv | `.venv` local por máquina |

### Dependencias Python principales

```
reflex==0.8.26
pytesseract
Pillow
groq
sqlmodel
psycopg2-binary
deepface          # opcional — si no está, cae a modo simulado
```

---

## Arquitectura del Proyecto

```
SVA-EPS/
├── rxconfig.py                  # Configuración Reflex + URL de Supabase
├── requirements.txt
├── alembic/                     # Migraciones de base de datos
│   └── versions/
│
└── sva_eps/
    ├── __init__.py              # Registro de páginas y app Reflex
    ├── sva_eps.py               # Punto de entrada principal
    │
    ├── components/              # Componentes de UI reutilizables
    │   ├── theme.py             # Paleta, tipografía y CSS global
    │   ├── navbar.py            # Barra de navegación institucional
    │   ├── formulario.py        # Paneles de captura y datos del ciudadano
    │   ├── workflow.py          # Stepper visual de etapas (Recibido → Dictamen)
    │   ├── sello.py             # Componente Sello de Inmutabilidad SHA-256
    │   ├── programa_card.py     # Tarjeta de programa social elegible
    │   └── consulta.py          # Componente de consulta de expediente
    │
    ├── models/                  # Modelos de datos (SQLModel)
    │   ├── expediente.py        # Tabla `expediente` + Enums Dictamen/Etapa
    │   └── programas.py         # Catálogo de programas sociales federales
    │
    ├── pages/                   # Páginas de la aplicación
    │   ├── ciudadano.py         # /  → Formulario de solicitud ciudadana
    │   ├── admin.py             # /admin → Panel operador / revisión manual
    │   ├── programas.py         # /programas → Catálogo de apoyos
    │   └── consulta.py          # /consulta → Consulta de expediente por CURP
    │
    ├── state/                   # Gestión de estado reactivo (rx.State)
    │   ├── ciudadano_state.py   # Estado del flujo de registro ciudadano
    │   ├── admin_state.py       # Estado del panel de administrador
    │   └── consulta_state.py    # Estado de la consulta pública
    │
    └── services/                # Capa de servicios (lógica de negocio)
        ├── ocr_service.py       # OCR real con Tesseract (fallback)
        ├── ia_service.py        # OCR + dictamen con Groq (primario)
        ├── biometria_service.py # Cotejo facial DeepFace / simulado
        ├── validacion_service.py# Motor RENAPO + reglas 90/10
        └── firma_service.py     # Generación y verificación SHA-256
```

---

## Instalación y Configuración

### Prerrequisitos

- Python 3.12 o 3.13
- `tesseract-ocr` instalado en el sistema
- Node.js 18+ (Reflex lo necesita para el frontend)

### 1. Clonar e instalar dependencias

```bash
git clone <url-del-repo>
cd SVA-EPS

# Crear entorno virtual LOCAL (obligatorio en cada máquina)
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# Instalar dependencias
pip install reflex pytesseract Pillow groq psycopg2-binary sqlmodel
```

### 2. Instalar Tesseract en el sistema

```bash
# Arch / Manjaro
sudo pacman -S tesseract tesseract-data-spa

# Ubuntu / Debian
sudo apt install tesseract-ocr tesseract-ocr-spa

# macOS
brew install tesseract tesseract-lang
```

### 3. Configurar variables de entorno (opcional)

```bash
# API Key de Groq para IA (si no se configura, usa modo simulado)
export GROQ_API_KEY="tu_clave_aqui"
```

### 4. Inicializar y correr

```bash
reflex init    # Solo la primera vez
reflex run     # Levanta frontend (localhost:3000) + backend (localhost:8000)
```

---

## Uso de la Aplicación

### Flujo Ciudadano (`/`)

1. **Subir INE** — Se extrae CURP, nombre, edad, sexo y entidad automáticamente.
2. **Subir Selfie** — El sistema realiza cotejo biométrico facial contra el INE.
3. **Documentos adicionales según perfil:**
   - **Menor de edad:** Se solicita documento CURP físico (PDF/imagen).
   - **Becas Rita Cetina o Benito Juárez:** Se solicita constancia de estudios o kardex (PDF).
   - **Mayores de 18 años:** Se muestra campo RFC (derivado del OCR).
4. **Enviar expediente** — El workflow animado muestra las 4 etapas en tiempo real.
5. **Resultado** — Dictamen automático + programa social recomendado + Sello SHA-256.

### Flujo Administrador (`/admin`)

- Vista de todos los expedientes registrados en Supabase.
- Búsqueda reactiva por CURP, nombre o dictamen.
- Herramienta de revisión para el 10% de casos derivados a revisión manual.

### Consulta Pública (`/consulta`)

- Cualquier ciudadano puede consultar el estado de su expediente ingresando su CURP.

---

## Base de Datos

La aplicación usa **PostgreSQL en Supabase**. La tabla principal se crea con el siguiente SQL:

```sql
CREATE TABLE IF NOT EXISTS expediente (
    id                   SERIAL PRIMARY KEY,
    folio                TEXT NOT NULL DEFAULT '',
    curp                 TEXT NOT NULL DEFAULT '',
    nombre               TEXT NOT NULL DEFAULT '',
    rfc                  TEXT NOT NULL DEFAULT '',
    estado               TEXT NOT NULL DEFAULT '',
    edad                 INTEGER NOT NULL DEFAULT 0,
    sexo                 TEXT NOT NULL DEFAULT '',
    etapa                TEXT NOT NULL DEFAULT 'Recibido',
    dictamen             TEXT NOT NULL DEFAULT 'PENDIENTE',
    motivo               TEXT NOT NULL DEFAULT '',
    sello_hash           TEXT NOT NULL DEFAULT '',
    fecha                TEXT NOT NULL DEFAULT '',
    finado               BOOLEAN NOT NULL DEFAULT FALSE,
    score_biometrico     REAL NOT NULL DEFAULT 0.0,
    programa_recomendado TEXT NOT NULL DEFAULT '',
    analisis_ia          TEXT NOT NULL DEFAULT '',
    fecha_registro       TEXT NOT NULL DEFAULT '',
    servicios_activos    TEXT NOT NULL DEFAULT '',
    servicios_inactivos  TEXT NOT NULL DEFAULT '',
    constancia_estudios  TEXT NOT NULL DEFAULT '',
    archivo_curp         TEXT NOT NULL DEFAULT ''
);
```

La URL de conexión se configura en `rxconfig.py`:

```python
db_url="postgresql://usuario:contraseña@host:5432/postgres"
```

---

## Servicios Clave

### `ia_service.py` — Motor IA (Groq)
- **OCR con visión:** Usa `meta-llama/llama-4-scout-17b-16e-instruct` para extraer datos del INE como imagen.
- **Dictamen narrativo:** Usa `llama-3.3-70b-versatile` para redactar la explicación del dictamen en lenguaje natural.
- **Fallback automático:** Si Groq no está disponible, cae silenciosamente al OCR con Tesseract.

### `biometria_service.py` — Cotejo Facial
- **Modo real:** DeepFace con modelo Facenet512 + detector RetinaFace (distancia coseno).
- **Modo simulado:** Score determinista basado en nombres de archivo (para demo sin GPU).
- **Umbrales:** ≤ 0.35 aprobado | ≤ 0.50 revisión manual | > 0.50 rechazado.

### `validacion_service.py` — Motor de Reglas 90/10
- Simula consulta RENAPO con ~5% de detección de finados (determinista por CURP).
- Aplica la regla de eficiencia: rechazo automático por finado, INE no vigente o biometría fallida.

### `firma_service.py` — Sello de Inmutabilidad
- Genera `SHA-256(CURP | timestamp_ISO | estado_dictamen)`.
- Cualquier alteración posterior del expediente produce un hash distinto, garantizando trazabilidad.

---

## Programas Sociales Cubiertos

| Clave | Programa | Edad | Perfil |
|---|---|---|---|
| PAM | Pensión Bienestar Adultos Mayores | 65+ | Todos |
| PMB | Pensión Mujeres Bienestar | 60–64 | Solo mujeres |
| SCC | Salud Casa por Casa | 60+ | Todos |
| RITA | Beca Rita Cetina (Sec. Pública) | 12–17 | Todos (requiere constancia) |
| BJ | Beca Benito Juárez (Bachillerato) | 15–17 | Todos (requiere constancia) |
| JEF | Jóvenes Escribiendo el Futuro | 18–29 | Todos |

---

## Variables de Entorno

| Variable | Descripción | Requerida |
|---|---|---|
| `GROQ_API_KEY` | API Key de Groq para IA (OCR + dictamen) | No — usa modo simulado si está ausente |

La URL de Supabase se configura directamente en `rxconfig.py` para la demo del hackathon.

---

## Equipo

Desarrollado por el equipo SVA-EPS para **Hackatec 2025** — Yucatán, México.
