FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/
COPY ./PROJECT/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --only main

COPY ./PROJECT/ .

EXPOSE 8080

CMD ["python", "main.py", "--port", "80"]
