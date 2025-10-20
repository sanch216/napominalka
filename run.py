from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.client.default import DefaultBotProperties
import asyncio
import os
from aiohttp import web

# ====== Токен через Environment Variable ======
TOKEN = os.getenv("BOT_TOKEN")
#bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
scheduler = AsyncIOScheduler()

reminders = {}  # user_id -> interval (в часах)

# ====== APScheduler wrapper ======
def _schedule_send(user_id):
    asyncio.create_task(send_reminder(user_id))

# ====== Команды бота ======
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

# ====== Мини-веб-сервер для Render ======
async def handle(request):
    return web.Response(text="Bot is alive!")

app = web.Application()
app.router.add_get("/", handle)

async def run_bot_and_server():
    # Запускаем APScheduler
    scheduler.start()

    # Запускаем aiohttp сервер
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(run_bot_and_server())
