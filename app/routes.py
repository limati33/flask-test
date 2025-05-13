from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
import sqlite3
import os
from datetime import datetime
import random
from werkzeug.utils import secure_filename
import json
from pywebpush import webpush, WebPushException

main = Blueprint('main', __name__)
DATABASE = 'instance/reviews.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@main.route('/')
def index():
    conn = get_db_connection()
    announcements = conn.execute('SELECT * FROM announcements ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('index.html', announcements=announcements)

@main.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        content = request.form['content']
        nickname = request.form['nickname'] or "Аноним"  # Если поле пустое, используем "Аноним"
        
        if content:
            unique_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1000, 9999))
            conn = get_db_connection()
            conn.execute('INSERT INTO reviews (content, unique_id, nickname) VALUES (?, ?, ?)', 
                         (content, unique_id, nickname))
            conn.commit()
            conn.close()
            return redirect(url_for('main.reviews'))
    return render_template('add.html')

@main.route('/reviews')
def reviews():
    if not session.get('admin_logged_in'):
        flash("Только администратор может просматривать отзывы.")
        return redirect(url_for('main.admin_login'))

    conn = get_db_connection()
    reviews = conn.execute('SELECT * FROM reviews ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('reviews.html', reviews=reviews)

# Пример данных для админа (можно использовать более сложную систему безопасности)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

@main.route('/admin', methods=('GET', 'POST'))
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return redirect(url_for('main.add_announcement'))
        else:
            flash("Неверный логин или пароль")
    return render_template('admin_login.html')

# Админская панель: вход
@main.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Проверяем логин и пароль
        if username == "admin" and password == "password":  # Замените на ваши данные
            session['admin_logged_in'] = True
            flash("Вы успешно вошли в админ-панель!")
            return redirect(url_for('main.index'))
        else:
            flash("Неверный логин или пароль.")
    return render_template('admin_login.html')

# Выход из системы
@main.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)  # Удаляем данные сессии
    flash("Вы вышли из админ-панели.")
    return redirect(url_for('main.admin_login'))
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Проверка разрешенных типов файлов
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Роут для добавления объявления
def send_push_notification(subscription, message):
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps(message),
            vapid_private_key=current_app.config['VAPID_PRIVATE_KEY'],
            vapid_claims=current_app.config['VAPID_CLAIMS']
        )
    except WebPushException as ex:
        print("Ошибка при отправке уведомления:", ex)

@main.route('/add_announcement', methods=['GET', 'POST'])
def add_announcement():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files.get('image')

        image_path = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            image_path = filename
            upload_folder = os.path.join(current_app.config['STATIC_FOLDER'], 'images')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file.save(os.path.join(upload_folder, filename))

        conn = get_db_connection()
        conn.execute('INSERT INTO announcements (title, content, image_path) VALUES (?, ?, ?)', (title, content, image_path))
        conn.commit()
        conn.close()

        # Читаем подписки и отправляем уведомление
        with open('subscriptions.json', 'r') as file:
            subscriptions = json.load(file)
            for subscription in subscriptions:
                send_push_notification(subscription, {
                    "title": "Новое объявление",
                    "body": f"{title}: {content[:50]}..."
                })

        flash('Объявление успешно добавлено!')
        return redirect(url_for('main.index'))

    return render_template('add_announcement.html')


@main.route('/delete_announcement/<int:announcement_id>', methods=['POST'])
def delete_announcement(announcement_id):
    if not session.get('admin_logged_in'):
        flash("Только администратор может удалить объявления.")
        return redirect(url_for('main.index'))

    conn = get_db_connection()
    # Удаляем объявление по id
    conn.execute('DELETE FROM announcements WHERE id = ?', (announcement_id,))
    conn.commit()
    conn.close()
    
    flash('Объявление успешно удалено.')
    return redirect(url_for('main.index'))

@main.route('/delete_review/<string:review_id>', methods=['POST'])
def delete_review(review_id):
    if not session.get('admin_logged_in'):
        flash("Только администратор может удалить отзывы.")
        return redirect(url_for('main.reviews'))

    conn = get_db_connection()
    # Удаляем отзыв по уникальному ID
    conn.execute('DELETE FROM reviews WHERE unique_id = ?', (review_id,))
    conn.commit()
    conn.close()
    
    flash('Отзыв успешно удален.')
    return redirect(url_for('main.reviews'))

@main.route('/subscribe', methods=['POST'])
def subscribe():
    # Получаем данные подписки от клиента
    subscription_info = request.get_json()
    with open('subscriptions.json', 'r+') as file:
        try:
            subscriptions = json.load(file)
        except json.JSONDecodeError:
            subscriptions = []
        subscriptions.append(subscription_info)
        file.seek(0)
        json.dump(subscriptions, file)

    return jsonify({'message': 'Подписка успешно добавлена'}), 201
