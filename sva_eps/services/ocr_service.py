"""Módulo de OCR real para extracción de datos del INE."""
import re
from datetime import datetime
import pytesseract
from PIL import Image

def extraer_datos_ine(ruta_archivo: str) -> dict:
    """Extrae datos reales de una imagen de INE usando Tesseract OCR."""
    
    # Diccionario base por si el OCR falla en encontrar algo
    datos = {
        "curp": "No detectada",
        "nombre": "Revisión manual requerida",
        "rfc": "No detectado",
        "estado": "Revisión manual requerida",
        "sexo": "No detectado",
        "edad": 0,
    }
    
    try:
        # 1. Abrir la imagen física y ejecutar el motor OCR en español
        img = Image.open(ruta_archivo)
        texto_extraido = pytesseract.image_to_string(img, lang='spa')
        
        # 2. Buscar la CURP (Es el ancla más fuerte en un INE)
        # Formato exacto: 4 letras, 6 números, H/M, 5 letras, 2 alfanuméricos
        curp_match = re.search(r'[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]{2}', texto_extraido)
        
        if curp_match:
            curp = curp_match.group(0)
            datos["curp"] = curp
            
            # 3. Derivar datos deterministas a partir de la estructura de la CURP
            datos["sexo"] = "Mujer" if curp[10] == 'M' else "Hombre"
            datos["rfc"] = curp[:10]  # El RFC base son los primeros 10 caracteres
            
            # Extraer año de nacimiento para calcular la edad exacta
            year_str = curp[4:6]
            año_actual = datetime.now().year
            # Lógica del siglo (asumiendo que no hay centenarios, ajusta si es necesario)
            año_nacimiento = int(year_str) + 1900 if int(year_str) > (año_actual % 100) else int(year_str) + 2000
            datos["edad"] = año_actual - año_nacimiento
            
            # Extraer Estado (posiciones 11 y 12 de la CURP)
            codigo_estado = curp[11:13]
            mapa_estados = {"YN": "Yucatán", "DF": "Ciudad de México", "JC": "Jalisco", "NL": "Nuevo León", "PL": "Puebla", "VZ": "Veracruz"}
            datos["estado"] = mapa_estados.get(codigo_estado, codigo_estado)

        # 4. Búsqueda simple de Nombre (Buscamos la palabra NOMBRE y capturamos lo siguiente)
        # Nota: En producción, podrías mejorar este Regex dependiendo del formato del INE
        nombre_match = re.search(r'NOMBRE\s*([A-Z\s]+)\n', texto_extraido)
        if nombre_match:
            # Limpiamos saltos de línea y espacios extra
            datos["nombre"] = " ".join(nombre_match.group(1).split())
            
    except Exception as e:
        print(f"Error procesando la imagen con OCR: {e}")
        
    return datos
