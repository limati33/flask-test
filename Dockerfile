# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Указываем порт
EXPOSE 10000

# Запуск Flask (или Gunicorn — по желанию)
CMD ["python", "app.py"]