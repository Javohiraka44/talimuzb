import sqlite3
import threading
import os
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

# Botni alohida oqimda (thread) ishga tushiramiz
def run_bot():
    try:
        # Eski ochilgan ulanishlarni tozalab yuboradi
        bot.remove_webhook()
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print("Bot xatoligi:", e)

# Flask veb-server qismi
app = Flask(__name__)

@app.route('/')
def index():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT first_name FROM users ORDER BY user_id DESC LIMIT 1')
    user = cursor.fetchone()
    conn.close()
    
    user_name = user[0] if user else "Mehmon"

    html_template = """
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Zamonaviy ta'lim</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, sans-serif; }
            body { background-color: #f4f7fc; color: #333; }
            header { background-color: #3b82f6; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
            .logo-text { font-size: 22px; font-weight: bold; }
            .container { display: flex; padding: 20px; gap: 20px; }
            sidebar { width: 250px; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .main-content { flex: 1; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            footer { text-align: center; padding: 15px; background: #1e3a8a; color: white; margin-top: 20px; }
            .user-profile { display: flex; align-items: center; gap: 10px; background: rgba(255, 255, 255, 0.2); padding: 6px 12px; border-radius: 6px; }
            .user-avatar { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; }
        </style>
    </head>
    <body>
        <header>
            <div class="logo-text">Zamonaviy ta'lim</div>
            <div id="authContainer">
                <script async src="https://telegram.org/js/telegram-widget.js?22" 
                        data-telegram-login="Talimuzb_bot" 
                        data-size="medium" 
                        data-onauth="onTelegramAuth(user)" 
                        data-request-access="write">
                </script>
            </div>
        </header>

        <div class="container">
            <sidebar>
                <h3>Bo'limlar</h3>
                <ul style="list-style: none; margin-top: 10px;">
                    <li style="padding: 8px 0; border-bottom: 1px solid #eee;"><a href="#" style="color: #3b82f6; text-decoration: none;">Ta'lim va fan</a></li>
                    <li style="padding: 8px 0; border-bottom: 1px solid #eee;"><a href="#" style="color: #3b82f6; text-decoration: none;">IT-industriya</a></li>
                </ul>
            </sidebar>

            <div class="main-content">
                <h2 id="welcomeTitle">Xush kelibsiz, {{ user_name }}!</h2>
                <p id="welcomeText" style="margin-top: 10px;">Platformamiz orqali bilim olishni boshlang.</p>
            </div>
        </div>

        <footer>
            <p>© 2026 Barcha huquqlar himoyalangan</p>
        </footer>

        <script>
            function onTelegramAuth(user) {
                document.getElementById('welcomeTitle').innerText = "Assalomu alaykum, " + user.first_name + "!";
                document.getElementById('welcomeText').innerText = "Siz Telegram orqali kirdingiz. ID: " + user.id;
                
                let avatarHtml = user.photo_url ? `<img src="${user.photo_url}" class="user-avatar" alt="Rasm">` : '👤';
                document.getElementById('authContainer').innerHTML = `
                    <div class="user-profile">
                        ${avatarHtml}
                        <span style="color: white; font-weight: bold;">${user.first_name}</span>
                    </div>
                `;
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, user_name=user_name)

if __name__ == '__main__':
    init_db()
    
    # Botni ishga tushirish uchun alohida oqim
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    
    # Render talab qiladigan muhim port sozlamasi
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
