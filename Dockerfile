FROM python:3.11-slim

WORKDIR /app

COPY ./PROJECT/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./PROJECT/ .

EXPOSE 8080

CMD ["python", "main.py"]