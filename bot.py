import asyncio
import json
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile, ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

# --- Config ---
TOKEN = "8250712732:AAGJMIuE7J8gdn6IV0MGPx1nyp1m5dPTiQA"
ADMIN_ID = 7353213881
RESUME_PATH = "resume.pdf"

# --- Fayllar ---
KINO_FILE = Path("kino.json")
PODCAST_FILE = Path("podcast.json")
BOOK_FILE = Path("books.json")

def load_data(file_path):
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

kino_data = load_data(KINO_FILE)
podcast_data = load_data(PODCAST_FILE)
book_data = load_data(BOOK_FILE)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- States ---
class FeedbackForm(StatesGroup):
    waiting_for_feedback = State()

class MovieAdder(StatesGroup):
    waiting_video = State()
    waiting_caption = State()
    waiting_name = State()
    waiting_code = State()

class PodcastAdder(StatesGroup):
    waiting_name = State()
    waiting_url = State()

class BookAdder(StatesGroup):
    waiting_name = State()

# --- Matnlar ---
ABOUT_TEXT = """
👨‍💻 *Akbarkhojayev Abbosxoja*
💼 *Backend Developer*
📧 Email: akbarkhojayev@gmail.com
"""

# --- Menu ---
def reply_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 Siz uchun"), KeyboardButton(text="👨‍💻 Admin")],
            [KeyboardButton(text="📄 Resume"), KeyboardButton(text="📬 Taklif va savollar")],
            [KeyboardButton(text="Algoritm o'rganamiz 🔜")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Tanlang..."
    )

def blog_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 Filmlar", callback_data="kino")],
        [InlineKeyboardButton(text="📚 Kitoblar", callback_data="kitob")],
        [InlineKeyboardButton(text="📢 Podcastlar", callback_data="podcast")],
    ])

def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧑🏻‍💻 Telegram", url='https://t.me/akbarkhojayev')],
        [InlineKeyboardButton(text="📸 Instagram", url='https://instagram.com/akbarkhodjayev')],
        [InlineKeyboardButton(text="📢 Telegram kanal", url='https://t.me/akbarkhodjayev')]
    ])

# --- Start ---
@dp.message(Command("start"))
async def handle_start(message: Message):
    await message.answer("👋 Mening shaxsiy botimga xush kelibsiz!", reply_markup=reply_main_menu())

# --- About ---
@dp.message(Command("about"))
async def handle_about(message: Message):
    await message.answer(ABOUT_TEXT, parse_mode="Markdown")

# --- Resume ---
@dp.message(F.text == "📄 Resume")
async def handle_resume_button(message: Message):
    try:
        file = FSInputFile(RESUME_PATH)
        await message.answer_document(file, caption="📄 Mening resume hujjatim")
    except Exception:
        await message.answer("❌ Resume fayli topilmadi.")

# --- Admin kontaktlar ---
@dp.message(F.text == "👨‍💻 Admin")
async def handle_admin(message: Message):
    await message.answer("👨‍💻 Admin kontaktlar:", reply_markup=admin_menu())

@dp.message(F.text == "Algoritm o'rganamiz 🔜")
async def algoritm(message: Message):
    await message.answer("Tez kunda !!!! \n\n"
                         "https://t.me/abzorithm")

# --- Blog menyu ---
@dp.message(F.text == "📖 Siz uchun")
async def handle_blog(message: Message):
    await message.answer("📖 Siz uchun bo‘limi:", reply_markup=blog_menu())

# --- Taklif va savollar ---
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

# --- Kino qo‘shish ---
@dp.message(Command("add_kino"))
async def add_kino(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Sizda ruxsat yo‘q")
        return
    await message.answer("🎬 Kinoni videosini yuboring:")
    await state.set_state(MovieAdder.waiting_video)

@dp.message(MovieAdder.waiting_video)
async def get_kino_video(message: Message, state: FSMContext):
    if not message.video:
        await message.answer("❌ Iltimos video yuboring")
        return
    await state.update_data(file_id=message.video.file_id)
    await message.answer("✍️ Videoga caption (izoh) yozing:")
    await state.set_state(MovieAdder.waiting_caption)

@dp.message(MovieAdder.waiting_caption)
async def get_kino_caption(message: Message, state: FSMContext):
    await state.update_data(caption=message.text)
    await message.answer("📌 Kino ro‘yxatida chiqadigan nomini yozing:")
    await state.set_state(MovieAdder.waiting_name)

@dp.message(MovieAdder.waiting_name)
async def get_kino_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("🔢 Kino kodi (raqam yoki matn) yuboring:")
    await state.set_state(MovieAdder.waiting_code)

@dp.message(MovieAdder.waiting_code)
async def save_kino(message: Message, state: FSMContext):
    data = await state.get_data()
    kino_data[message.text] = {
        "file_id": data["file_id"],
        "caption": data["caption"],
        "name": data["name"]
    }
    save_data(KINO_FILE, kino_data)
    await state.clear()
    await message.answer("✅ Kino muvaffaqiyatli saqlandi!")

# --- Podcast qo‘shish ---
@dp.message(Command("add_podcast"))
async def add_podcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Sizda ruxsat yo‘q")
        return
    await message.answer("🎧 Podcast nomini yozing:")
    await state.set_state(PodcastAdder.waiting_name)

@dp.message(PodcastAdder.waiting_name)
async def get_podcast_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("🔗 Podcast havolasini yuboring:")
    await state.set_state(PodcastAdder.waiting_url)

@dp.message(PodcastAdder.waiting_url)
async def save_podcast(message: Message, state: FSMContext):
    data = await state.get_data()
    podcast_data[data["name"]] = message.text
    save_data(PODCAST_FILE, podcast_data)
    await state.clear()
    await message.answer("✅ Podcast qo‘shildi!")

# --- Kitob qo‘shish ---
@dp.message(Command("add_book"))
async def add_book(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Sizda ruxsat yo‘q")
        return
    await message.answer("📚 Kitob nomini yozing:")
    await state.set_state(BookAdder.waiting_name)

@dp.message(BookAdder.waiting_name)
async def save_book(message: Message, state: FSMContext):
    idx = len(book_data) + 1
    book_data[str(idx)] = message.text
    save_data(BOOK_FILE, book_data)
    await state.clear()
    await message.answer("✅ Kitob qo‘shildi!")

# --- Callbacklar ---
@dp.callback_query()
async def handle_callbacks(callback: CallbackQuery):
    data = callback.data

    # kino ro'yxati
    if data == "kino":
        if not kino_data:
            await callback.message.edit_text("❌ Kino yo‘q", reply_markup=blog_menu())
            await callback.answer()
            return
        text = ("🎬 Filmlar ro'yxati:\n\n"
                "O'lib ketishdan oldin shu filmlarni tomasha qilib koring 🙃 "
                "Kinoni tartib raqami bu kino kodi, kodni shunchaki botga yuboring !!!\n\n")

        for code, info in kino_data.items():
            text += f"{code}. {info.get('name','(nom yo‘q)')}\n"
        await callback.message.edit_text(text, reply_markup=blog_menu())
        await callback.answer()
        return

    # podcast ro'yxati
    if data == "podcast":
        if not podcast_data:
            await callback.message.edit_text("❌ Podcast yo‘q", reply_markup=blog_menu())
            await callback.answer()
            return

        text = "🎧 Podcastlar ro'yxati:\n\n"
        buttons = []
        for idx, (name, url) in enumerate(podcast_data.items(), start=1):
            text += f"{idx}. {name}\n"
            buttons.append(InlineKeyboardButton(text=str(idx), callback_data=f"podcast_{idx}"))

        kb = InlineKeyboardMarkup(
            inline_keyboard=[buttons[i:i + 5] for i in range(0, len(buttons), 5)]
        )
        kb.inline_keyboard.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_menu")])

        await callback.message.edit_text(text, reply_markup=kb)
        await callback.answer()
        return

    # podcast tanlash
    if data.startswith("podcast_"):
        idx = int(data.split("_")[1]) - 1
        items = list(podcast_data.items())
        if 0 <= idx < len(items):
            name, url = items[idx]
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="▶️ Eshitish", url=url)],
                [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="podcast")]
            ])
            await callback.message.edit_text(f"🎧 {name}", reply_markup=kb)
        await callback.answer()
        return

    # orqaga tugmasi
    if data == "back_to_menu":
        await callback.message.edit_text("📖 Siz uchun bo‘limi:", reply_markup=blog_menu())
        await callback.answer()
        return

    # kitoblar ro'yxati
    if data == "kitob":
        if not book_data:
            await callback.message.edit_text("❌ Kitob yo‘q", reply_markup=blog_menu())
            await callback.answer()
            return
        text = "📚 Kitoblar:\n\n"
        for idx, name in book_data.items():
            text += f"{idx}. 📖 {name}\n"
        await callback.message.edit_text(text, reply_markup=blog_menu())
        await callback.answer()
        return

    await callback.answer()

# --- Kod bilan kino chiqarish ---
@dp.message(F.text & ~F.text.startswith("/"))
async def find_or_echo(message: Message):
    code = message.text.strip()
    if code in kino_data:
        data = kino_data[code]
        await message.answer_video(data["file_id"], caption=data["caption"])
    else:
        await message.answer(f"📝 Siz yubordingiz:\n`{message.text}`", parse_mode="Markdown")

# --- Main ---
async def main():
    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
