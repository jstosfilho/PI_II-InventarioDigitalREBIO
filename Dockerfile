FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY inventario ./inventario
COPY serve.py .
RUN useradd --create-home app && mkdir -p /data /app/instance && chown -R app:app /data /app/instance
USER app
ENV REBIO_DATABASE=/data/inventario.sqlite3 PORT=8080
EXPOSE 8080
CMD ["python", "serve.py"]
