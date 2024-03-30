from fastapi import FastAPI, UploadFile, File
from datetime import datetime
import pdfplumber
import re

app = FastAPI()
app.title = "Conversor de facturas PDF a tablas de GOOGLE SHEET"
   
def extract_and_clean_text(pattern, text):
    """ Extrae usando una expresión regular y limpia el texto. """
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).replace('\n', '').strip() if match else None

def prepare_response(empresa, no_factura, cufe, table_data):
    """ Prepara la respuesta a una petición. """
    prepared_data = []
    for row in table_data:
        # Asegurar que la fila tiene la cantidad correcta de elementos
        if len(row) == 13:
            # Preparar fila con los datos adicionales de la factura
            prepared_row = [empresa, no_factura, cufe] + row
            prepared_data.append(prepared_row)
    return prepared_data

def extract_references(text):
    """Busca y extrae el número de referencia de un texto dado."""
    # Primer patrón: Captura el texto entre 'Fecha Referencia' y 'Notas Finales' con un salto de línea final.
    pattern = r"Fecha Referencia\n(.+?)\nNotas Finales"
    match_section = re.search(pattern, text, re.DOTALL)
    if not match_section:
        # Segundo patrón: Captura el texto entre 'Fecha Referencia' y 'Notas Finales' sin salto de línea final.
        pattern = r"Fecha Referencia\n(.+?)Notas Finales"
        match_section = re.search(pattern, text, re.DOTALL)
    if not match_section:
        # Tercer patrón: Captura directamente el número de referencia después de 'Factura Electrónica'.
        pattern = r"Razón de Referencia\n(.+?)Notas Finales"
        match_section = re.search(pattern, text, re.DOTALL)
        """ if match_section:
            return match_section.group(1)  # Directamente retorna el número de referencia encontrado. """
    
    if not match_section:
        return "No encontrado"
    # Para los primeros dos patrones, extrae y procesa la sección encontrada.
    extracted_section = match_section.group(1)
    # Divide el texto extraído y selecciona el segundo elemento, si es aplicable.
    elements = extracted_section.split()
    if 'Electrónica' in extracted_section:
        return(elements[2])
    if len(elements) >= 2: 
        return elements[1]  # Retorna el segundo elemento, que sería el número de referencia.
    else:
        return "Formato inesperado"

def extract_reference__type_number_date(text):
    """Busca y extrae el tipo, el número y la fecha de referencia de un texto dado."""
    reference_type = ''
    reference_number = ''
    reference_date = ''
    # Primer patrón: Captura el texto entre 'Fecha Referencia' y 'Notas Finales' con un salto de línea final.
    pattern = r"Fecha Referencia\n(.+?)\nNotas Finales"
    match_section = re.search(pattern, text, re.DOTALL)
    if not match_section:
        # Segundo patrón: Captura el texto entre 'Fecha Referencia' y 'Notas Finales' sin salto de línea final.
        pattern = r"Fecha Referencia\n(.+?)Notas Finales"
        match_section = re.search(pattern, text, re.DOTALL)
    if not match_section:
        # Tercer patrón: Captura directamente el número de referencia después de 'Factura Electrónica'.
        pattern = r"Razón de Referencia\n(.+?)Notas Finales"
        match_section = re.search(pattern, text, re.DOTALL)
        """ if match_section:
            return match_section.group(1)  # Directamente retorna el número de referencia encontrado. """
    
    if not match_section:
        return reference_type, reference_number, reference_date
    # Para los primeros dos patrones, extrae y procesa la sección encontrada.
    extracted_section = match_section.group(1)
    # Divide el texto extraído y selecciona el segundo elemento, si es aplicable.
    elements = extracted_section.split()
    if 'Electrónica' in extracted_section:
        reference_type = elements[0] + ' ' + elements[1]
        reference_number = elements[2]
        reference_date = elements[3]
        return reference_type, reference_number, reference_date
    elif len(elements) == 3: 
        reference_type = elements[0]
        reference_number = elements[1]
        reference_date = elements[2]
        return reference_type, reference_number, reference_date  # Retorna el segundo elemento, que sería el número de referencia.
    elif len(elements) == 2:
        reference_type = elements[0]
        reference_number = elements[1]
        return reference_type, reference_number, reference_date
    else:
        return reference_type, reference_number, reference_date
   
@app.get("/")
def read_root():
    return {"Name" : "InvoicePdfDataExtractor_Abaco",
            "Description" : "Use InvoicePdfDataExtractor_Abaco to extract data from an Abaco invoice.",
            "Details" : {"API Framework": "FastAPI", "Programming Language" : "Python 3.8.10", "Libraries" : "pdfplumber, re"}}

@app.post("/extract_invoice_data")
async def extract_data_from_one_pdf(pdf_file: UploadFile = File(...)):
    try:
        reference_number = None
        # Abrir el PDF desde el archivo cargado
        with pdfplumber.open(pdf_file.file) as pdf:
            # Buscar el número de referencia en cada página hasta encontrarlo.
            all_text = ''
            for page in pdf.pages:
                text = page.extract_text()
                all_text = all_text + text
            
            reference_type, reference_number, reference_date = extract_reference__type_number_date(all_text)
            # Extraer el texto de la primera hoja del archivo pdf
            text = pdf.pages[0].extract_text()
            all_rows = []
            table_data = []
            # Extraer las tablas de cada hoja del archivo pdf
            for page in pdf.pages:
                page_tables = page.extract_tables()
                # Extrae y limpia las filas de cada tabla del archivo pdf
                for table in page_tables:
                    for row in table:
                        if len(row) == 13:
                            cleaned_row = [cell.replace('\n', ' ').replace('$ ', '').replace('$', '') if cell else cell for cell in row]
                            all_rows.append(cleaned_row)

        cufe = extract_and_clean_text(r"Código Único de Factura - CUFE :(.*?)Número de Factura", text) or "CUFE no encontrado"
        if cufe == "CUFE no encontrado":
            cufe = extract_and_clean_text(r"Código Único de documento electrónico - CUDE : (.*?)Número de Factura", text) or "CUDE no encontrado"
        if cufe == "CUDE no encontrado":
            cufe = extract_and_clean_text(r"Código Único de documento electrónico - CUDE :(.*?)Número de Factura", text) or "CUDE no encontrado"
        if cufe == "CUDE no encontrado":
            cufe = extract_and_clean_text(r"Código Único de Factura - CUDE : (.*?)Número de Factura", text) or "CUDE no encontrado"
        invoice_number = extract_and_clean_text(r"Número de Factura: (.*?)(Forma de pago)", text) or "Número de factura no encontrado"
        invoice_number = invoice_number.replace("-", "")
        social_reason = extract_and_clean_text(r"Razón Social: (.*?)(Nombre Comercial)", text) or "Razón social no encontrada"
        emision_date = extract_and_clean_text(r"Fecha de Emisión: (.*?)(Medio de Pago)", text) or "Fecha de emisión no encontrada"
        city = extract_and_clean_text(r"Municipio / Ciudad: (.*?)(Responsabilidad tributaria)", text) or "Ciudad no encontrada"
        if "Dirección" in city:
            city = extract_and_clean_text(r"Municipio / Ciudad: (.*?)(Dirección)", text) or "Ciudad no encontrada"
        emisor_nit = extract_and_clean_text(r"Nit del Emisor: (.*?)(País)", text) or "NIT Emisor no encontrado"
        operation_type = extract_and_clean_text(r"Tipo de Operación: (.*?)(Fecha de orden)", text) or "Tipo de Operación no encontrada"
        final_notes = extract_and_clean_text(r"Notas Finales(.*?)(Datos Totales)", all_text) or "Notas Finales no encontradas"
        if 'artículo 424' in final_notes or 'ARTÍCULO 424' in final_notes:
            iva_excluded = 'SI'
        else:
            iva_excluded= 'NO'
        download_date = datetime.now()
        # Verificar si los tres valores clave no fueron encontrados
        if cufe == "CUFE no encontrado" and invoice_number == "Número de factura no encontrado" and social_reason == "Razón social no encontrada" and emision_date == "Fecha de emisión no encontrada" and city == "Ciudad no encontrada":
            raise ValueError("Información (CUFE, FECHA EMISION, EMPRESA y NO. FACTURA) no encontrada en el PDF.")
        
        if all_rows:
            all_rows.pop(0)  # Eliminar encabezado de la tabla
            all_rows.pop(0)
            for row in all_rows:
                if len(row) == 13:
                    prepared_row = [emision_date, social_reason, emisor_nit, city, invoice_number, operation_type, cufe, reference_type, reference_number, reference_date, final_notes, iva_excluded, download_date] + row
                    table_data.append(prepared_row)
            return {"message": "Datos extraídos", "all_text": "all_text", "text": "text", "data": table_data}
        else:
            return {"message": "Datos NO extraídos"}
    except Exception as e:
        return {"message": f"Error al procesar el PDF: {str(e)}"}

