FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "until python -c 'import socket; s=socket.socket(); s.connect((\"auth-db\", 5432))' 2>/dev/null; do echo 'Esperando auth-db...'; sleep 2; done; uvicorn main:app --host 0.0.0.0 --port 8001"]