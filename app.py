import sqlite3
import threading
import telebot
from flask import Flask, render_template_string

TOKEN = "9071175801:AAEzQFO0tJQh0xHox3-HI8Ygwq-GQskNgYo"
bot = telebot.TeleBot(TOKEN)

# Ma'lumotlar bazasini sozlash
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_user(user_id, first_name):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, first_name) VALUES (?, ?)
    ''', (user_id, first_name))
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    save_user(user_id, user_name)
    bot.reply_to(
        message, 
        f"Assalomu alaykum, {user_name}!\nSizning ma'lumotlaringiz bazaga muvaffaqiyatli saqlandi ✅"
    )

# Botni alohida oqimda (thread) ishga tushiramiz, toki u veb-saytga xalaqit bermasin
def run_bot():
    bot.polling(none_stop=True)

# Flask veb-server qismi
app = Flask(__name__)

@app.route('/')
def index():
    # Bazadan oxirgi ro'yxatdan o'tgan foydalanuvchini o'qib olamiz
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT first_name FROM users ORDER BY user_id DESC LIMIT 1')
    user = cursor.fetchone()
    conn.close()
    
    user_name = user[0] if user else "Mehmon"

    # HTML sahifa
    html_template = """
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <title>Zamonaviy ta'lim</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f7fc; text-align: center; padding-top: 50px; }
            .card { background: white; max-width: 400px; margin: 0 auto; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            h1 { color: #3b82f6; }
            p { color: #555; margin-top: 15px; }
            .btn { display: inline-block; background: #0088cc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 20px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Xush kelibsiz, {{ user_name }}!</h1>
            <p>Siz Telegram botimiz orqali muvaffaqiyatli ro'yxatdan o'tdingiz va bu ma'lumot avtomatik ravishda veb-saytga chiqdi.</p>
            <a href="https://t.me/SizningBotingiz_bot" target="_blank" class="btn">Telegram botga o'tish</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, user_name=user_name)

if __name__ == '__main__':
    init_db()
    # Botni ishga tushirish
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    
    print("Veb-server va Telegram bot ishga tushdi: http://127.0.0.1:5000")
    # Flask serverini yoqamiz
    app.run(debug=False, port=5000)