FROM python:3.7-slim-bullseye
WORKDIR /app

# 禁用Python字节码生成
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    python3-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

# 清理所有__pycache__目录
RUN find . -type d -name "__pycache__" -exec rm -r {} +

COPY . .

# 再次清理所有__pycache__目录
RUN find . -type d -name "__pycache__" -exec rm -r {} +
RUN find . -type d -name "*.pyc" -delete

# 创建证书目录并设置权限
RUN mkdir -p /app/cert && \
    chmod -R 755 /app/cert && \
    chown -R root:root /app/cert

RUN chmod +x migrate.sh

EXPOSE 80

# 使用迁移脚本启动
CMD ["./migrate.sh"] 