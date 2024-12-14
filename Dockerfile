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
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    STATIC_URL=/static/ \
    STATIC_ROOT=/app/staticfiles \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONPATH=/app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    python3-dev \
    ca-certificates \
    dos2unix \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 创建必要的目录
RUN mkdir -p /app/cert /app/staticfiles /usr/local/share/ca-certificates \
    && chmod -R 755 /app/cert /app/staticfiles \
    && chown -R root:root /app/cert /app/staticfiles

# 复制 requirements.txt
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建应用目录结��
RUN mkdir -p wxcloudrun/apps/emotions/migrations && \
    mkdir -p wxcloudrun/apps/emotions/templates && \
    mkdir -p wxcloudrun/apps/emotions/static && \
    mkdir -p wxcloudrun/apps/collections/migrations && \
    mkdir -p wxcloudrun/apps/collections/templates && \
    mkdir -p wxcloudrun/apps/collections/static && \
    mkdir -p wxcloudrun/apps/careers/migrations && \
    mkdir -p wxcloudrun/apps/careers/templates && \
    mkdir -p wxcloudrun/apps/careers/static && \
    mkdir -p wxcloudrun/apps/users/migrations && \
    mkdir -p wxcloudrun/apps/users/templates && \
    mkdir -p wxcloudrun/apps/users/static && \
    mkdir -p wxcloudrun/apps/core/migrations && \
    mkdir -p wxcloudrun/apps/core/templates && \
    mkdir -p wxcloudrun/apps/core/static && \
    touch wxcloudrun/apps/emotions/migrations/__init__.py && \
    touch wxcloudrun/apps/collections/migrations/__init__.py && \
    touch wxcloudrun/apps/careers/migrations/__init__.py && \
    touch wxcloudrun/apps/users/migrations/__init__.py && \
    touch wxcloudrun/apps/core/migrations/__init__.py && \
    touch wxcloudrun/apps/emotions/__init__.py && \
    touch wxcloudrun/apps/collections/__init__.py && \
    touch wxcloudrun/apps/careers/__init__.py && \
    touch wxcloudrun/apps/users/__init__.py && \
    touch wxcloudrun/apps/core/__init__.py && \
    touch wxcloudrun/apps/__init__.py

# 转换文件格式并清理缓存文件
RUN find . -type f -name "*.py" -exec dos2unix {} \; && \
    find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true && \
    find . -type f -name "*.pyc" -delete

# 检查环境编码设置
RUN python -c "import sys; print('Default encoding:', sys.getdefaultencoding())" && \
    python -c "import locale; print('Locale:', locale.getpreferredencoding())"

# 检查并修复 Python 文件编码
RUN for f in $(find . -type f -name "*.py"); do \
        if ! python -c "open('$f', 'rb').read().decode('utf-8')"; then \
            echo "Converting $f to UTF-8" && \
            iconv -f ISO-8859-1 -t UTF-8 "$f" > "$f.tmp" && \
            mv "$f.tmp" "$f"; \
        fi \
    done

# 检查 Django 应用配置
RUN python -c "from django.apps import apps; from django.conf import settings; \
    settings.configure(); \
    print('Django settings configured successfully')"

# 收集静态文件
RUN DJANGO_SETTINGS_MODULE=wxcloudrun.settings python manage.py collectstatic --noinput --clear

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