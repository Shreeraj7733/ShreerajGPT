import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Init OpenAI (LATEST)
client = OpenAI(api_key=OPENAI_API_KEY)

# Bot + Dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Memory storage (simple)
user_memory = {}

# -----------------------------
# COMMANDS
# -----------------------------

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Hi!\nI am your AI Telegram Bot 🤖\nHow can I help you?"
    )


@dp.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer(
        "/start - Start bot\n"
        "/clear - Clear memory\n"
        "/help - Help menu"
    )


@dp.message(Command("clear"))
async def clear_handler(message: types.Message):
    user_memory[message.chat.id] = []
    await message.answer("✅ Memory cleared!")


# -----------------------------
# CHAT HANDLER
# -----------------------------

@dp.message()
async def chat_handler(message: types.Message):
    user_id = message.chat.id
    user_text = message.text

    if user_id not in user_memory:
        user_memory[user_id] = []

    # Add user message
    user_memory[user_id].append({"role": "user", "content": user_text})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",   # fast + cheap
            messages=user_memory[user_id]
        )

        bot_reply = response.choices[0].message.content

        # Save response
        user_memory[user_id].append(
            {"role": "assistant", "content": bot_reply}
        )

        await message.answer(bot_reply)

    except Exception as e:
        await message.answer(f"❌ Error: {str(e)}")


# -----------------------------
# MAIN
# -----------------------------

async def main():
    print("🚀 Bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())