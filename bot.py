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

# ── FILE IDs (после первого запуска заполнятся автоматически) ──
PHOTO_IDS = {}

async def preload_photos():
    """Фотоларды дискіден жүктейді"""
    photos = {
        "photo1": "photo1.png",
        "photo2": "photo2.png",
    }
    for key, filename in photos.items():
        try:
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    msg = await bot.send_photo(
                        chat_id=ADMIN_ID,
                        photo=f,
                        caption=f"✅ {key} жүктелді"
                    )
                    PHOTO_IDS[key] = msg.photo[-1].file_id
                    logging.info(f"{key} file_id сақталды")
            else:
                logging.warning(f"{filename} табылмады")
        except Exception as e:
            logging.error(f"{key} қатесі: {e}")

# ── KEYBOARDS ──
def kb_start():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="💳 Төлем жасау — 15 000 ₸", callback_data="show_payment")
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

    # Бірінші хабар — боль
    msg1 = (
        "Авторлық өніміңді жасап сатқың келе ме?\n"
        "Немесе өз өнімің бар, бірақ сатылмай жатыр ма?\n\n"
        "Көпшілік осылай тұрып қалады:\n\n"
        "❓ Тауар бар, карточка бар — сатылым жоқ\n"
        "❓ Біреулер топқа шығады, біреулер көрінбей қалады\n"
        "❓ Рекламаға ақша кетеді — нәтиже жоқ\n"
        "❓ Отзыв жинай алмайды, рейтинг көтерілмейді\n"
        "❓ Идея бар — бірақ қайдан бастарын білмейді"
    )
    await msg.answer(msg1)
    await asyncio.sleep(2)

    # Екінші хабар — история
    msg2 = (
        "Менің бастауым да бірден нәтижелі болған жоқ.\n\n"
        "2 жыл бұрын тәуекел етіп бастадым, себебі:\n\n"
        "❌ Ақша жоқ (қарызға алдым)\n"
        "❌ Каспи магазин жоқ, ИП жоқ\n"
        "❌ Тәжірибе жоқ, тауар сатып көрмегенмін\n\n"
        "Алғашқы 3 ай дұрыс сауда болмады 😅\n\n"
        "Бірақ әрдайым анализ жасап, қателерімді іздеп,\n"
        "жаңа стратегия, воронкаларды тест жасап, нәтижесінде бүгінге дейін:\n\n"
        "✅ 13 700+ сатылым\n"
        "✅ 50млн+ оборот\n"
        "✅ 4 жеке оқушы (менторлықтан өткен)\n"
        "✅ 5 авторлық блокнот/трекер"
    )
    await msg.answer(msg2)
    await asyncio.sleep(2)

    # Үшінші хабар — оффер + кнопка
    msg3 = (
        "Осы жабық каналда осы жолдың бәрін ашамын:\n\n"
        "📌 Идея қалай келді, қалай жүзеге асты, дизайн, типография, бюджет\n"
        "📌 Неге бастапқыда сатылым болмады, қандай қателер жасадым?\n"
        "📌 Не өзгерттім, өнімдерім қалай сатыла бастады? Қандай воронка продаж құрдым?\n"
        "📌 Каспи карточкасы, топқа шығу, отзыв жинау\n"
        "📌 ИП, Kaspi Pay, салық, жеткізу, упаковка жасау т.б.\n"
        "📌 Қателерім, тәжірибелерім, кеңестерім\n\n"
        "Бұл курс емес.\n"
        "Бұл — менің нақты өткен жолым, нақты цифрлармен, нақты скриншоттармен.\n\n"
        f"💰 Presale баға: <b>{PRICE}</b> — шексіз доступ\n"
        "⏳ Келесі аптада 22.06.2026, баға 25 000 ₸ болады."
    )
    await msg.answer(msg3, parse_mode="HTML")
    await asyncio.sleep(1)

    # Төртінші хабар — фотодоказательства
    if PHOTO_IDS.get("photo1"):
        await bot.send_photo(
            chat_id=msg.chat.id,
            photo=PHOTO_IDS["photo1"],
            caption="📦 Нақты жұмыс — заказдар, накладной, Kaspi обороты"
        )
        await asyncio.sleep(1)

    if PHOTO_IDS.get("photo2"):
        await bot.send_photo(
            chat_id=msg.chat.id,
            photo=PHOTO_IDS["photo2"],
            caption="⭐️ Оқушыларымның нәтижелері мен пікірлері"
        )
        await asyncio.sleep(1)

    # Кнопка
    await msg.answer(
        "👇 Каналға қосылу үшін төлем жасаңыз:",
        reply_markup=kb_start()
    )

# ── SHOW PAYMENT ──
@dp.callback_query(F.data == "show_payment")
async def show_payment(call: CallbackQuery):
    text = (
        f"💳 <b>{PRICE} — шексіз доступ</b>\n\n"
        f"1-нұсқа — Kaspi Pay:\n"
        f'🔗 <a href="{KASPI_LINK}">Kaspi Pay арқылы төлеу →</a>\n\n'
        f"2-нұсқа — Басқа банк арқылы:\n"
        f"<code>{CARD}</code>\n"
        f"{CARD_NAME}\n\n"
        f"📸 Төлегеннен кейін скриншотты осы ботқа жіберіңіз\n\n"
        f"⏱ Скриншотты жібергеннен кейін 5-15 минут ішінде каналға сілтеме келеді!"
    )
    await call.message.answer(text, parse_mode="HTML")
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

@dp.message(Command("reload_photos"))
async def cmd_reload(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer("Фотолар қайта жүктелуде...")
    await preload_photos()
    await msg.answer(f"✅ Дайын. Жүктелген фотолар: {list(PHOTO_IDS.keys())}")

# ── RUN ──
async def main():
    await preload_photos()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
