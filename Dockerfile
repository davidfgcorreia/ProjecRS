FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# Ensure storage directories exist
RUN mkdir -p /app/app/storage/pdfs /app/app/storage/temp /app/app/storage/results /app/app/storage/reports

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
