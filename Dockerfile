FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# Ensure storage directories exist
RUN mkdir -p /app/app/storage/pdfs /app/app/storage/temp /app/app/storage/results /app/app/storage/reports

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
