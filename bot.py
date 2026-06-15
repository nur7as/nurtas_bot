import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage
from database import Database
import asyncio

# ── CONFIG ──
BOT_TOKEN  = os.getenv("BOT_TOKEN")
ADMIN_ID   = int(os.getenv("ADMIN_ID", "646654612"))
CHANNEL_ID = os.getenv("CHANNEL_ID", "-1004344613555")
KASPI_LINK = os.getenv("KASPI_LINK", "https://pay.kaspi.kz/pay/tmchkblz")
PRICE      = "15 000 ₸"
CARD       = "5269 8800 1480 4728"
CARD_NAME  = "Нуртас И."

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())
db  = Database()

# ── KEYBOARDS ──
def kb_start():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=f"💳 Төлем жасау [{PRICE}]", callback_data="show_payment")
    ]])

def kb_payment():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔗 Kaspi Pay арқылы төлеу →", url=KASPI_LINK)
    ]])

def kb_admin(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Растау", callback_data=f"approve_{user_id}"),
        InlineKeyboardButton(text="❌ Қабылдамау", callback_data=f"reject_{user_id}")
    ]])

# ── HANDLERS ──
@dp.message(CommandStart())
async def cmd_start(msg: Message):
    user = msg.from_user

    if db.is_subscriber(user.id):
        await msg.answer(
            "Сен каналға кіруді бұрын сатып алдың! ✅\n\n"
            "Егер сілтеме жоғалып кетсе — @nurtas_issabek-ке жаз."
        )
        return

    text = (
        "Авторлық өніміңді жасап сатқың келе ме?\n"
        "Немесе өз өнімің бар, бірақ сатылмай жатыр ма?\n\n"
        "Көпшілік осылай тұрып қалады:\n"
        "— Тауар бар, карточка бар, бірақ сатылым жоқ\n"
        "— Біреулер топқа шығып кетеді, біреулер көрінбей қалады\n"
        "— Рекламаға ақша кетеді, нәтиже жоқ\n"
        "— Отзыв жинай алмайды, рейтинг көтерілмейді\n"
        "— Идея бар, бірақ қайдан бастарын білмейді\n\n"
        "Менің бастауым бірден нәтижелі болған жоқ.\n\n"
        "2 жыл бұрын алғашқы авторлық блокноттарды тәуекел етіп бірден 1 000 дана шығардым.\n"
        "Шығаруға ақшаны қарызға алдым. Каспи магазин жоқ. Тәжірибе жоқ.\n"
        "Казпочта арқылы жіберіп отырдым —\n"
        "әр клиентке өзім жауап беріп, адрестерін, номерлерін жинап,\n"
        "казпочтада 2-3 сағат кезекте тұратынмын.\n\n"
        "Алғашқы 3 айда — 40-50 дана ғана әрең сатылды.\n"
        "Анализ жасай келе өте көп қателерімді анықтадым, жаңа стратегия, воронка продаж құрып\n"
        "950 данасын келесі 2 айда сатып жіберіп, 2 есе тәуекелге бел буып\n"
        "2 000 дана блокнот тағы шығардым. 2 айда бәрін сатып тастадым.\n\n"
        "Бүгінге дейін жалпы 13 600+ сатылым. +50млн оборот. Бірнеше авторлық өнімдер.\n\n"
        "Осы жабық каналда осы жолдың бәрін ашамын:\n"
        "— Неге алғашқы 3 айда 40-50 ғана сатылды — қандай қате жасадым\n"
        "— Не өзгерттім, өнімдерім қалай тез сатыла бастады?\n"
        "— Контент, таргет — қандай видео сатты, қандай бюджет кетті\n"
        "— Типография, дизайн — ценообразование, қандай дизайн өтімді, структурасы\n"
        "— Каспи карточкасы, топқа шығу, отзыв жинау\n"
        "— ИП, Kaspi Pay, налог, доставка, упаковка\n"
        "— Тағы басқа да тәжірибелерім, қателерім және кеңестерім\n\n"
        "Бұл курс емес, бұл менің өткен нақты жолым, нақты цифрлармен, нақты скриншоттармен.\n\n"
        f"💰 Қатысу: <b>{PRICE}</b> — доступ навсегда"
    )
    await msg.answer(text, parse_mode="HTML", reply_markup=kb_start())

# ── SHOW PAYMENT ──
@dp.callback_query(F.data == "show_payment")
async def show_payment(call: CallbackQuery):
    text = (
        f"💳 Төлем жасау — <b>{PRICE}</b>\n\n"
        "1-нұсқа — Kaspi Pay:\n"
        "🔗 Төмендегі батырманы басыңыз\n\n"
        "2-нұсқа — Басқа банк арқылы:\n"
        f"<code>{CARD}</code>\n"
        f"{CARD_NAME}\n\n"
        "📸 Төлегеннен кейін скриншотты осы ботқа жіберіңіз\n\n"
        "⏱ Скриншотты жібергеннен кейін 5-15 минут ішінде каналға сілтеме келеді!"
    )
    await call.message.answer(text, parse_mode="HTML", reply_markup=kb_payment())
    await call.answer()

# ── SCREENSHOT ──
@dp.message(F.photo)
async def receive_screenshot(msg: Message):
    user = msg.from_user

    if db.is_subscriber(user.id):
        await msg.answer("Сен каналға кіруді бұрын сатып алдың! ✅")
        return

    name     = user.full_name
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

# ── APPROVE ──
@dp.callback_query(F.data.startswith("approve_"))
async def approve(call: CallbackQuery):
    user_id = int(call.data.split("_")[1])

    try:
        link = await bot.create_chat_invite_link(
            chat_id=CHANNEL_ID,
            member_limit=1
        )

        try:
            chat = await bot.get_chat(user_id)
            full_name = chat.full_name or ""
            username  = chat.username or ""
        except Exception:
            full_name = ""
            username  = ""

        db.add_subscriber(user_id, full_name, username)
        db.remove_pending(user_id)

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

# ── REJECT ──
@dp.callback_query(F.data.startswith("reject_"))
async def reject(call: CallbackQuery):
    user_id = int(call.data.split("_")[1])
    db.remove_pending(user_id)

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
@dp.message(Command("users"))
async def cmd_users(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return

    subscribers = db.get_all_subscribers()
    count = db.get_count()

    if not subscribers:
        await msg.answer("Әзірше ешкім сатып алмаған.")
        return

    text = f"👥 Жалпы сатып алушылар: <b>{count}</b>\n\n"
    for i, s in enumerate(subscribers, 1):
        username = f"@{s['username']}" if s['username'] else "—"
        text += f"{i}. {s['full_name']} | {username} | {s['added_at']}\n"

    await msg.answer(text, parse_mode="HTML")

@dp.message(Command("stats"))
async def cmd_stats(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return

    count = db.get_count()
    revenue = count * 15000
    await msg.answer(
        f"📊 Статистика\n\n"
        f"👥 Сатып алушылар: <b>{count}</b>\n"
        f"💰 Жалпы табыс: <b>{revenue:,} ₸</b>".replace(",", " "),
        parse_mode="HTML"
    )

# ── RUN ──
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
