FROM python:3.8-slim-buster

COPY . /app

WORKDIR /app

RUN pip install --upgrade --no-cache-dir -r requirements.txt

CMD ["python3", "./main.py"]
