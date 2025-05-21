FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY cli.py .
COPY converter/ ./converter/

RUN chmod +x cli.py

ENTRYPOINT ["python", "cli.py"]