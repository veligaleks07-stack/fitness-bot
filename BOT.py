import os
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect("db.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, points INTEGER)")
conn.commit()

def add_points(user_id, value):
    cur.execute("INSERT OR IGNORE INTO users VALUES (?, 0)", (user_id,))
    cur.execute("UPDATE users SET points = points + ? WHERE id=?", (value, user_id))
    conn.commit()

def get_points(user_id):
    cur.execute("SELECT points FROM users WHERE id=?", (user_id,))
    res = cur.fetchone()
    return res[0] if res else 0

@dp.message_handler(commands=['plus'])
async def plus(message: types.Message):
    add_points(message.from_user.id, 1)
    await message.reply("➕ +1 тебе!")

@dp.message_handler(commands=['points'])
async def points(message: types.Message):
    await message.reply(f"⭐ У тебя {get_points(message.from_user.id)} очков")

@dp.message_handler(commands=['top'])
async def top(message: types.Message):
    cur.execute("SELECT id, points FROM users ORDER BY points DESC LIMIT 10")
    rows = cur.fetchall()

    text = "🏆 ТОП:\n\n"
    for i, (uid, pts) in enumerate(rows, 1):
        text += f"{i}. {uid} — {pts}\n"

    await message.reply(text)

async def is_admin(message):
    m = await bot.get_chat_member(message.chat.id, message.from_user.id)
    return m.is_chat_admin()

@dp.message_handler(commands=['add'])
async def add(message: types.Message):
    if not await is_admin(message):
        return await message.reply("❌ Только админы")

    args = message.get_args().split()
    if len(args) < 2:
        return await message.reply("/add user_id 5")

    add_points(int(args[0]), int(args[1]))
    await message.reply("➕ Добавлено")

@dp.message_handler(commands=['remove'])
async def remove(message: types.Message):
    if not await is_admin(message):
        return await message.reply("❌ Только админы")

    args = message.get_args().split()
    if len(args) < 2:
        return await message.reply("/remove user_id 5")

    add_points(int(args[0]), -int(args[1]))
    await message.reply("➖ Убрано")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)