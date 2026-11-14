import telebot
import sqlite3

TOKEN = "9071175801:AAEzQFO0tJQh0xHox3-HI8Ygwq-GQskNgYo"
bot = telebot.TeleBot(TOKEN)

# Ma'lumotlar bazasini yaratish va ulanish
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Foydalanuvchilar jadvalini yaratamiz (agar mavjud bo'lmasa)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Bazaga foydalanuvchini qo'shish
def save_user(user_id, first_name):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Agar foydalanuvchi oldin bo'lmasa, qo'shamiz
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, first_name) VALUES (?, ?)
    ''', (user_id, first_name))
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Ma'lumotlarni bazaga saqlaymiz
    save_user(user_id, user_name)
    
    bot.reply_to(
        message, 
        f"Assalomu alaykum, {user_name}!\n"
        f"Sizning ma'lumotlaringiz bazaga muvaffaqiyatli saqlandi ✅\n"
        f"Sizning Telegram ID raqamingiz: {user_id}"
    )

if __name__ == '__main__':
    init_db()
    print("Bot ma'lumotlar bazasi bilan birga ishga tushdi...")
    bot.polling()