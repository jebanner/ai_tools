FROM python:3.7-slim-bullseye
WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/cert
RUN chmod +x migrate.sh

ENV PYTHONUNBUFFERED=1

EXPOSE 80

# 使用迁移脚本启动
CMD ["./migrate.sh"] 