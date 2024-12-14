FROM python:3.7-slim-bullseye
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    GUNICORN_WORKERS=2 \
    GUNICORN_THREADS=4 \
    GUNICORN_TIMEOUT=60 \
    SSL_CERT_DIR=/etc/ssl/certs \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    python3-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 清理缓存文件
RUN find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true \
    && find . -type f -name "*.pyc" -delete

# 配置证书目录
RUN mkdir -p /app/cert \
    && chmod -R 755 /app/cert \
    && chown -R root:root /app/cert \
    && mkdir -p /usr/local/share/ca-certificates

# 收集静态文件
RUN python manage.py collectstatic --noinput

EXPOSE 80

# 直接使用 gunicorn 启动
CMD ["gunicorn", \
     "--bind", "0.0.0.0:80", \
     "--workers", "2", \
     "--threads", "4", \
     "--timeout", "60", \
     "--worker-class", "gthread", \
     "--worker-tmp-dir", "/dev/shm", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50", \
     "wxcloudrun.wsgi:application"] 