#!/bin/bash

# 设置错误处理
set -e

# 清理__pycache__目录
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# 等待数据库准备就绪
echo "Waiting for database..."
python manage.py wait_for_db

# 执行数据库迁移
echo "Applying database migrations..."
python manage.py migrate

# 收集静态文件
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 初始化证书
if [ -f "/app/cert/initenv.sh" ]; then
    echo "Initializing certificates..."
    chmod +x /app/cert/initenv.sh
    /app/cert/initenv.sh || {
        echo "Certificate initialization failed"
        exit 1
    }
fi

# 启动应用
echo "Starting application..."
gunicorn --bind 0.0.0.0:80 --workers 4 --timeout 60 wxcloudrun.wsgi:application 