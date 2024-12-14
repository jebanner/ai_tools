FROM python:3.7.3
WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/cert

ENV PYTHONUNBUFFERED=1

EXPOSE 80

# 启动命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"] 