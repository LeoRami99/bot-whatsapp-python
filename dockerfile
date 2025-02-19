### Dockerfile (Configuración para Docker)
FROM python:3.9

# Configuración del entorno de trabajo
WORKDIR /app

# Copiar y instalar dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente al contenedor
COPY . .

# Exponer el puerto 8000
EXPOSE 1000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1000"]
