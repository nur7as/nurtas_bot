import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

# ── CONFIG ──
BOT_TOKEN  = os.getenv("BOT_TOKEN")
ADMIN_ID   = int(os.getenv("ADMIN_ID", "646654612"))
CHANNEL_ID = os.getenv("CHANNEL_ID", "-1004344613555")
KASPI_LINK = os.getenv("KASPI_LINK", "https://pay.kaspi.kz/pay/tmchkblz")
PRICE      = "7 000 ₸"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

# ── KEYBOARDS ──
def kb_pay():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=f"💳 Kaspi арқылы төлеу — {PRICE}", url=KASPI_LINK)
    ], [
        InlineKeyboardButton(text="✅ Төледім, скриншот жіберемін", callback_data="paid")
    ]])

def kb_admin(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Растау", callback_data=f"approve_{user_id}"),
        InlineKeyboardButton(text="❌ Қабылдамау", callback_data=f"reject_{user_id}")
    ]])

# ── HANDLERS ──
@dp.message(CommandStart())
async def cmd_start(msg: Message):
    text = (
        "Сәлем! 👋\n\n"
        "Бұл — <b>«Kaspi 13 000+ кейс»</b> жабық каналы.\n\n"
        "Ішінде не бар:\n"
        "— Авторлық ежедневникті нөлден қалай жасадым\n"
        "— Дизайн, типография, бірінші тираж\n"
        "— Kaspi магазин, карточка, отзывтар\n"
        "— Контент, таргет, 13 000+ сатылымға дейінгі жол\n"
        "— Нақты скриншоттар мен цифрлар\n\n"
        f"💰 Қатысу бағасы: <b>{PRICE}</b>\n\n"
        "Төлем жасап, скриншот жіберсең — каналға кіру сілтемесін аласың."
    )
    await msg.answer(text, parse_mode="HTML", reply_markup=kb_pay())

@dp.callback_query(F.data == "paid")
async def cb_paid(call: CallbackQuery):
    await call.message.answer(
        "Жақсы! 👍\n\n"
        "Енді төлем скриншотын осы жерге жібер.\n"
        "Мен тексеріп, каналға кіру сілтемесін жіберемін."
    )
    await call.answer()

@dp.message(F.photo)
async def receive_screenshot(msg: Message):
    user = msg.from_user
    name = user.full_name
    username = f"@{user.username}" if user.username else "username жоқ"

    caption = (
        f"💳 Жаңа төлем скриншоты\n\n"
        f"👤 Аты: {name}\n"
        f"📱 Username: {username}\n"
        f"🆔 ID: <code>{user.id}</code>"
    )

    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=msg.photo[-1].file_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=kb_admin(user.id)
    )

    await msg.answer(
        "Скриншот жіберілді! ✅\n\n"
        "Тексеру 5-15 минут ішінде жүреді.\n"
        "Растағаннан кейін каналға сілтемені осы жерден аласың."
    )

@dp.callback_query(F.data.startswith("approve_"))
async def approve(call: CallbackQuery):
    user_id = int(call.data.split("_")[1])

    try:
        link = await bot.create_chat_invite_link(
            chat_id=CHANNEL_ID,
            member_limit=1
        )
        await bot.send_message(
            chat_id=user_id,
            text=(
                "✅ Төлемің расталды!\n\n"
                "Каналға кіру сілтемең:\n"
                f"👇\n{link.invite_link}\n\n"
                "Сілтеме бір рет қолданылады.\n"
                "Сәттілік! 🚀"
            )
        )
        await call.message.edit_caption(
            caption=call.message.caption + "\n\n✅ РАСТАЛДЫ",
            reply_markup=None
        )
    except Exception as e:
        await call.message.answer(f"Қате: {e}")

    await call.answer("Расталды ✅")

@dp.callback_query(F.data.startswith("reject_"))
async def reject(call: CallbackQuery):
    user_id = int(call.data.split("_")[1])

    await bot.send_message(
        chat_id=user_id,
        text=(
            "❌ Төлем расталмады.\n\n"
            "Себебі: скриншот көрінбейді немесе төлем сәйкес келмеді.\n\n"
            "Қайта төлеп, анық скриншот жіберіп көр.\n"
            "Сұрақ болса — @nurtas_issabek-ке жаз."
        )
    )
    await call.message.edit_caption(
        caption=call.message.caption + "\n\n❌ ҚАБЫЛДАНБАДЫ",
        reply_markup=None
    )
    await call.answer("Қабылданбады ❌")

# ── ADMIN COMMANDS ──
@dp.message(F.text == "/start", F.from_user.id == ADMIN_ID)
async def admin_start(msg: Message):
    await msg.answer(
        "👋 Сәлем, Нуртас!\n\n"
        "Бот жұмыс істеп тұр ✅\n\n"
        "Пайдаланушы скриншот жіберсе — саған хабарлама келеді."
    )

# ── RUN ──
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
