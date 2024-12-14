FROM python:3.7.3
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 80

# 启动命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"] 