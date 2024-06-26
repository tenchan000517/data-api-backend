FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP=wsgi.py
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app", "--log-level=debug"]
