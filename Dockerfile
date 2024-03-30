# Utiliza la imagen oficial de Python como base
FROM python:3.9

# Establece el directorio de trabajo
WORKDIR /pdf-excelApp

# Copiar el proyecto
COPY . .

# Copia el archivo de requisitos a la imagen
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir --upgrade -r requirements.txt
# Comando para iniciar la aplicación
CMD ["uvicorn", "pdf-excelApp.main:app", "--host", "0.0.0.0", "--port", "7860"]