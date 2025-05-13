import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'instance', 'reviews.db')

class Config:
    SECRET_KEY = 'your-secret-key'
    DATABASE = DATABASE
    STATIC_FOLDER = os.path.join(os.getcwd(), 'app', 'static')  # Путь к папке static
