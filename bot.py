import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile, ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

TOKEN = "7624889825:AAEotYU-RvgiVkyH-I3GSwY8vzLwelAw1_Y"
ADMIN_ID = 7353213881
RESUME_PATH = "resume.pdf"


class FeedbackForm(StatesGroup):
    waiting_for_feedback = State()

ABOUT_TEXT = """
👨‍💻 *Akbarkhojayev Abbosxoja*
💼 *Backend Developer*
📧 Email: akbarkhojayev@gmail.com

"""

import json
from pathlib import Path

USERS_FILE = Path("users.json")

def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def add_user(user):
    users = load_users()
    user_data = {
        "id": user.id,
        "full_name": user.full_name,
        "username": user.username
    }
    if not any(u["id"] == user.id for u in users):
        users.append(user_data)
        save_users(users)


KINO_TEXT = """🎬 *Kinolarim reytingi (shaxsiy fikr)*

1. Munaboi 1  
2. Muhabbat masofasi  
3. Interstellar  
4. Yulduzlar aybdor  
5. Joker  
6. Sevgi va mahluq  
7. Vijdon amri  
8. Uch savdoyi  
9. Shonshenkdan Qochib  
10. O'lik shoirlar jamiyati  
11. Tanishing Jou Black  
12. Zakovatli Uil  
13. Trueman Show  
14. Chol va nabira  
15. Forrest Gump  
16. Yo‘l-yo‘l pijamali bolakay  
17. Mo‘jiza (2017)

🛑 *Izoh:* Turk kinolarini yoqtirmayman!
"""

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


def reply_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 Bloglar"), KeyboardButton(text="👨‍💻 Admin")],
            [KeyboardButton(text="📄 Resume"), KeyboardButton(text="📬 Taklif va savollar")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Tanlang..."
    )

def blog_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Telegram", callback_data="telegram"),
            InlineKeyboardButton(text="🎬 Kinolar", callback_data="kino")
        ],
        [InlineKeyboardButton(text="📚 Kitoblar", callback_data="kitob")]
    ])

def bot_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Anonim bot", callback_data="anonim")]
    ])

def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Telegram", callback_data="admin_telegram")],
        [InlineKeyboardButton(text="📸 Instagram", callback_data="admin_instagram")]
    ])


@dp.message(Command("start"))
async def handle_start(message: Message):
    add_user(message.from_user)
    await message.answer("👋 Mening shaxsiy botimga xush kelibsiz!", reply_markup=reply_main_menu())

@dp.message(Command("about"))
async def handle_about(message: Message):
    await message.answer(ABOUT_TEXT)

@dp.message(F.photo)
async def get_photo_id(message: Message):
    file_id = message.photo[-1].file_id
    await message.answer(f"📎 Rasmning file_id:\n\n{file_id}")

@dp.message(Command("website"))
async def handle_website(message: Message):
    file_id = "AgACAgIAAxkBAAIDcmh1NEK1_OXKwjKqh0qNnP28DKUwAAJx-DEb3DyxS_3VMHAUD45bAQADAgADeQADNgQ"
    btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Tashrif buyurish", url="https://abbosceek.pythonanywhere.com/")]
    ])
    await message.answer_photo(photo=file_id, caption="🌐 Shaxsiy portfolio sayt", reply_markup=btn)

@dp.message(Command("users"))
async def list_users(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Bu buyruq mavjud emas")
        return

    users = load_users()
    if not users:
        await message.answer("👥 Hali foydalanuvchi yo‘q.")
        return

    text = "📋 Bot foydalanuvchilari:\n\n"
    for u in users:
        uname = f"@{u['username']}" if u['username'] else "—"
        text += f"👤 {u['full_name']} | {uname} | ID: `{u['id']}`\n"

    await message.answer(text, parse_mode="Markdown")


# @dp.message(Command("website"))
# async def handle_website(message: Message):
#     try:
#         photo = FSInputFile("website.png")
#         btn = InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text="🔗 Tashrif buyurish", url="https://abbosceek.pythonanywhere.com/")]
#         ])
#         await message.answer_photo(photo=photo, caption="🌐 Shaxsiy portfolio sayt", reply_markup=btn)
#     except Exception as e:
#         await message.answer("❌ Sayt rasmi topilmadi.")


@dp.message(F.text == "👨‍💻 Admin")
async def handle_admin(message: Message):
    await message.answer("👨‍💻 Admin kontaktlar:", reply_markup=admin_menu())

@dp.message(F.text == "📖 Bloglar")
async def handle_blog(message: Message):
    await message.answer("📖 Bloglar bo‘limi:", reply_markup=blog_menu())

@dp.message(F.text == "📄 Resume")
async def handle_resume_button(message: Message):
    try:
        file = FSInputFile(RESUME_PATH)
        await message.answer_document(file, caption="📄 Mening resume hujjatim")
    except Exception:
        await message.answer("❌ Resume fayli topilmadi.")

@dp.message(F.text == "📬 Taklif va savollar")
async def handle_feedback_start(message: Message, state: FSMContext):
    await message.answer("✍️ Iltimos, taklif yoki savolingizni yozing:")
    await state.set_state(FeedbackForm.waiting_for_feedback)

@dp.message(FeedbackForm.waiting_for_feedback)
async def handle_feedback_message(message: Message, state: FSMContext):
    user = message.from_user
    text = f"📩 Yangi xabar!\n\n👤 <b>{user.full_name}</b> (@{user.username})\n🆔 ID: <code>{user.id}</code>\n\n💬 {message.text}"
    await bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="HTML")

    await message.answer("✅ Xabaringiz yuborildi. Rahmat!", reply_markup=reply_main_menu())
    await state.clear()

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_echo(message: Message):
    await message.answer(f"📝 Siz yubordingiz:\n`{message.text}`")

@dp.callback_query()
async def handle_callbacks(callback: CallbackQuery):
    data = callback.data

    if data == "telegram":
        await callback.message.answer("📢 Telegram blog: https://t.me/akbarkhodjayev")

    elif data == "kitob":
        await callback.message.answer("📚 Kitoblarim: (hozircha bo‘sh)")

    elif data == "kino":
        await callback.message.answer(KINO_TEXT)

    elif data == "anonim":
        await callback.message.answer("🤖 Anonim bot: https://t.me/anonim_abzbot")

    elif data == "admin_telegram":
        await callback.message.answer("👨‍💻 Telegram: https://t.me/akbarkhojayev")

    elif data == "admin_instagram":
        await callback.message.answer("📸 Instagram: https://instagram.com/akbarkhodjayev")

    await callback.answer()

async def main():
    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
