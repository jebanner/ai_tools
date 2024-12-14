#!/bin/bash

# 等待数据库准备就绪
echo "Waiting for database..."
python manage.py wait_for_db

# 执行数据库迁移
echo "Applying database migrations..."
python manage.py migrate

# 创建超级用户（如果需要）
# python manage.py createsuperuser --noinput

# 收集静态文件
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 启动应用
echo "Starting application..."
gunicorn --bind 0.0.0.0:80 --workers 4 --timeout 60 wxcloudrun.wsgi:application 