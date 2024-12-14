# 选择构建用基础镜像
FROM alpine:3.13

# 设置时区为上海时间
RUN apk add tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo Asia/Shanghai > /etc/timezone

# 使用 HTTPS 协议访问容器云调用证书安装
RUN apk add ca-certificates

# 选用国内镜像源并安装必要的包
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tencent.com/g' /etc/apk/repositories \
    && apk add --update --no-cache \
    python3 \
    py3-pip \
    mariadb-dev \
    gcc \
    python3-dev \
    musl-dev \
    linux-headers \
    dos2unix \
    curl \
    && rm -rf /var/cache/apk/*

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=wxcloudrun.settings \
    STATIC_URL=/static/ \
    STATIC_ROOT=/app/staticfiles \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 创建必要的目录
RUN mkdir -p /app/cert /app/staticfiles \
    && chmod -R 755 /app/cert /app/staticfiles

# 配置pip使用国内源
RUN pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple \
    && pip config set global.trusted-host mirrors.cloud.tencent.com \
    && pip install --upgrade pip

# 复制requirements.txt并安装依赖
COPY requirements.txt .
RUN pip install --user -r requirements.txt \
    && pip install gunicorn==20.1.0

# 复制应用代码
COPY . .

# 修复文件编码和行尾符
RUN find . -type f -name "*.py" -exec dos2unix {} \; \
    && find . -type f -name "*.py" -exec python3 -c "import sys; content = open(sys.argv[1], 'r', encoding='utf-8-sig').read(); open(sys.argv[1], 'w', encoding='utf-8').write(content)" {} \;

# 创建应用目录结构
RUN mkdir -p wxcloudrun/apps && \
    mkdir -p wxcloudrun/apps/emotions/migrations && \
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
    mkdir -p wxcloudrun/apps/core/static

# 创建初始化文件
RUN for app in emotions collections careers users core; do \
    touch wxcloudrun/apps/$app/__init__.py; \
    touch wxcloudrun/apps/$app/migrations/__init__.py; \
    done && \
    touch wxcloudrun/apps/__init__.py

# 执行数据库迁移和收集静态文件
RUN python3 manage.py migrate --noinput && \
    python3 manage.py collectstatic --noinput --clear

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# 启动命令
ENTRYPOINT ["gunicorn"]
CMD ["--bind", "0.0.0.0:80", "--workers", "4", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "wxcloudrun.wsgi:application"]