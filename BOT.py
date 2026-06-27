from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# база очков
points = {}

# проверка админа
async def is_admin(message: types.Message):
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    return chat_member.is_chat_admin()


# =========================
# +1 себе (все могут)
# =========================
@dp.message_handler(commands=['plus'])
async def plus_one(message: types.Message):
    user_id = message.from_user.id
    points[user_id] = points.get(user_id, 0) + 1
    await message.reply("➕ +1 очко тебе!")


# =========================
# добавить очки (только админы)
# =========================
@dp.message_handler(commands=['add'])
async def add_points(message: types.Message):
    if not await is_admin(message):
        await message.reply("❌ Только админы могут добавлять очки")
        return

    args = message.get_args().split()

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        value = int(args[0]) if args else 1
    else:
        if len(args) < 2:
            await message.reply("Используй: /add @user 5 (или ответом)")
            return
        value = int(args[1])
        user_id = message.reply_to_message.from_user.id if message.reply_to_message else args[0]

    points[user_id] = points.get(user_id, 0) + value
    await message.reply(f"➕ Добавлено {value} очков")


# =========================
# убрать очки (только админы)
# =========================
@dp.message_handler(commands=['remove'])
async def remove_points(message: types.Message):
    if not await is_admin(message):
        await message.reply("❌ Только админы могут отнимать очки")
        return

    args = message.get_args().split()

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        value = int(args[0]) if args else 1
    else:
        if len(args) < 2:
            await message.reply("Используй: /remove @user 5")
            return
        value = int(args[1])
        user_id = args[0]

    points[user_id] = max(0, points.get(user_id, 0) - value)
    await message.reply(f"➖ Убрано {value} очков")


# =========================
# посмотреть свои очки
# =========================
@dp.message_handler(commands=['points'])
async def my_points(message: types.Message):
    user_id = message.from_user.id
    score = points.get(user_id, 0)
    await message.reply(f"⭐ У тебя {score} очков")


# =========================
# топ
# =========================
@dp.message_handler(commands=['top'])
async def top(message: types.Message):
    if not points:
        await message.reply("Пока нет очков")
        return

    sorted_points = sorted(points.items(), key=lambda x: x[1], reverse=True)

    text = "🏆 Таблица лидеров:\n\n"
    for i, (user_id, score) in enumerate(sorted_points, 1):
        text += f"{i}. {user_id} — {score}\n"

    await message.reply(text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)