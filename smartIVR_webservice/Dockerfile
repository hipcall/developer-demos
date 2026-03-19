FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure data directory exists
RUN mkdir -p data

# Initialize database
RUN python init_db.py

EXPOSE 5008

CMD ["gunicorn", "--bind", "0.0.0.0:5008", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
