FROM python:3.12-slim

WORKDIR /app

COPY db/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY db/ /app/db/

CMD ["alembic", "-c", "db/alembic.ini", "upgrade", "head"]
