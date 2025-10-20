from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

import os
TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
scheduler = AsyncIOScheduler()

reminders = {}  # user_id -> interval (в часах)

def _schedule_send(user_id):
    # wrapper called by APScheduler; it schedules the coroutine on the asyncio loop
    asyncio.create_task(send_reminder(user_id))

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! Я бот-напоминалка 💬\n\n"
        "Напиши команду:\n"
        "<b>/settime 2</b> — чтобы я напоминал каждые 2 часа\n"
        "<b>/stop</b> — чтобы остановить напоминания"
    )

@dp.message(Command("settime"))
async def set_time(message: types.Message):
    try:
        interval = int(message.text.split()[1])
        user_id = message.from_user.id
        reminders[user_id] = interval

        # schedule the synchronous wrapper which will create the async task
        scheduler.add_job(_schedule_send, "interval", hours=interval, args=[user_id], id=str(user_id), replace_existing=True)
        await message.answer(f"✅ Буду напоминать каждые {interval} ч.")
    except:
        await message.answer("⚠️ Укажи число после команды. Пример: /settime 2")

@dp.message(Command("stop"))
async def stop(message: types.Message):
    user_id = str(message.from_user.id)
    if scheduler.get_job(user_id):
        scheduler.remove_job(user_id)
        await message.answer("🛑 Напоминания остановлены.")
    else:
        await message.answer("Ты и так ничего не получаешь 😄")

async def send_reminder(user_id):
    await bot.send_message(user_id, "⏰ Пора кодить, дружище!")

async def main():
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
