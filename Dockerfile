FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /Reminder-Bot

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y wget \
    && wget -O /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    && chmod +x /usr/local/bin/wait-for-it.sh \
    && apt-get remove -y wget \
    && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["sh", "-c", "wait-for-it.sh postgres:5432 --timeout=30 -- python -u index.py"]