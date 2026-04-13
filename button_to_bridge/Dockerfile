FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data
RUN python init_db.py

EXPOSE 5011

CMD ["sh", "-c", "python init_db.py && gunicorn --bind 0.0.0.0:5011 app:app"]
