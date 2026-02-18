from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '7586435661:AAGYqwdOF8uXuGBy0yGEv4pqyJecCl2BS1k'

# ID администратора (ваш Telegram user ID). Замените 123456789 на ваш ID.
ADMIN_ID = 884422112

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Хранилище гостей в памяти
guests = []


async def send_useful_links(message: types.Message):
    """
    Отправка благодарности и скрытых ссылок на чаты.
    """
    text = (
        "Спасибо за ваш ответ💕\n"
        "Высылаем вам полезные ссылки:\n"
        "• Чат с гостями - [link](https://t.me/+h_OZrfDaf1IwNGI6) (обязательно добавиться)\n"
        "• Чат с организатором - [link](https://t.me/Juliiianaaa)"
    )
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )

# FSM для обработки ФИО и информации о паре
class RSVP(StatesGroup):
    waiting_for_fio = State()
    waiting_for_partner = State()

# Стартовое сообщение с кнопками
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("ДА"), KeyboardButton("НЕТ"))
    await message.answer(
        "Добрый день! Просим вас подтвердить присутствие на свадьбе Артема и Лидии 16 мая в Сочи 💝",
        reply_markup=keyboard
    )

# Обработка ответа "ДА"
@dp.message_handler(lambda message: message.text == "ДА")
async def yes_handler(message: types.Message):
    await message.answer(
        "Пришлите, пожалуйста, ваше ФИО полностью.",
        reply_markup=ReplyKeyboardRemove()
    )
    await RSVP.waiting_for_fio.set()

@dp.message_handler(state=RSVP.waiting_for_fio)
async def process_fio(message: types.Message, state: FSMContext):
    # Сохраняем ФИО и спрашиваем про наличие пары
    await state.update_data(fio=message.text.strip())

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("С парой"), KeyboardButton("Без пары"))

    await message.answer(
        "Подскажите, вы будете с парой?",
        reply_markup=keyboard
    )
    await RSVP.waiting_for_partner.set()

@dp.message_handler(state=RSVP.waiting_for_partner)
async def process_partner(message: types.Message, state: FSMContext):
    user_choice = message.text

    if user_choice not in ("С парой", "Без пары"):
        await message.answer("Пожалуйста, выберите один из вариантов на клавиатуре.")
        return

    data = await state.get_data()
    fio = data.get("fio", "").strip() or "Без ФИО"
    with_partner = user_choice == "С парой"

    # Сохраняем гостя в память
    guests.append(
        {
            "fio": fio,
            "with_partner": with_partner,
            "user_id": message.from_user.id,
            "username": message.from_user.username,
        }
    )

    # Дополнительно сохраняем в файл (на всякий случай)
    try:
        with open("guests.txt", "a", encoding="utf-8") as f:
            status = "с парой" if with_partner else "без пары"
            username = message.from_user.username
            username_part = f" (@{username})" if username else ""
            f.write(f"{fio}{username_part} — {status}\n")
    except Exception:
        # Не ломаем логику бота, если файл не удалось записать
        pass

    # Пытаемся отправить обновленный файл с гостями администратору
    await send_guests_file_to_admin()

    await state.finish()
    await send_useful_links(message)

async def send_guests_file_to_admin() -> bool:
    """
    Отправка файла guests.txt администратору.
    Возвращает True при успехе, False при ошибке.
    """
    if not ADMIN_ID:
        return False

    try:
        input_file = types.InputFile("guests.txt")
    except Exception:
        return False

    try:
        await bot.send_document(
            chat_id=ADMIN_ID,
            document=input_file,
            caption="Текущий список гостей",
        )
        return True
    except Exception:
        return False


# Обработка ответа "НЕТ"
@dp.message_handler(lambda message: message.text == "НЕТ")
async def no_handler(message: types.Message):
    # Только благодарность, без ссылок
    await message.answer("Спасибо за ваш ответ!", reply_markup=ReplyKeyboardRemove())

@dp.message_handler(commands=['guests'])
async def show_guests(message: types.Message):
    """
    Команда для просмотра списка гостей.
    """
    if not guests:
        await message.answer("Список гостей пока пуст.")
        return

    lines = []
    for idx, guest in enumerate(guests, start=1):
        status = "с парой" if guest.get("with_partner") else "без пары"
        fio = guest.get("fio", "Без ФИО")
        lines.append(f"{idx}. {fio} ({status})")

    text = "Список гостей:\n" + "\n".join(lines)
    await message.answer(text)


@dp.message_handler(commands=['guests_file'])
async def send_guests_file_command(message: types.Message):
    """
    Команда для администратора: выслать файл guests.txt со списком гостей.
    """
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет доступа к этому разделу.")
        return

    success = await send_guests_file_to_admin()
    if success:
        await message.answer("Файл с списком гостей отправлен.")
    else:
        await message.answer("Файл с списком гостей пока недоступен.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    