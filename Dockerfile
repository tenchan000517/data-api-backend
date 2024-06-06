# Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP=run.py
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
