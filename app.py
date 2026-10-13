import os
from flask import Flask
from threading import Thread
import telebot
from telebot import types
import sqlite3

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_LINK", "https://t.me/schekinaelclic")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)")
    conn.commit()
    conn.close()
init_db()

@app.route('/')
def home():
    return "Bot is Running"

@bot.message_handler(commands=['start'])
def start(m):
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (m.from_user.id,))
    conn.commit()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="👉 CLIC ICI +5F", url=CHANNEL))
    markup.add(types.InlineKeyboardButton(text="✅ J'ai rejoint +5F", callback_data="claim"))
    markup.add(types.InlineKeyboardButton(text="💰 Mon Solde", callback_data="balance"))
    bot.send_message(m.chat.id, f"Salut {m.from_user.first_name}! Gagne 5F par clic", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    if call.data == "claim":
        c.execute("UPDATE users SET balance=balance+5 WHERE id=?", (call.from_user.id,))
        conn.commit()
        c.execute("SELECT balance FROM users WHERE id=?", (call.from_user.id,))
        bal = c.fetchone()[0]
        bot.answer_callback_query(call.id, f"+5F! Solde: {bal}F")
    if call.data == "balance":
        c.execute("SELECT balance FROM users WHERE id=?", (call.from_user.id,))
        bal = c.fetchone()[0]
        bot.send_message(call.message.chat.id, f"💰 Solde: {bal}F")
    conn.close()

def run_bot():
    bot.infinity_polling()
def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    Thread(target=run_bot).start()
    run_flask()
