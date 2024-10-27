import logging as log
from aiogram import html
from aiogram import Bot, Dispatcher, F
from aiogram.client.session import aiohttp
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from src.database_handler import database_handler
from src.constants import MOBMENTOR_BOT_TOKEN

commands_dict = {
    "/setmodule": "выбрать обучающий модуль",
    "/changetopic": "выбрать/сменить тему (в рамках модуля)",
    "/help": "подробное описание команд"
}

# TODO Заменить на постоянное хранилище
dp = Dispatcher(storage=MemoryStorage())
bot = Bot(MOBMENTOR_BOT_TOKEN)


class ModuleSelection(StatesGroup):
    waiting_module_input = State()


class TopicSelection(StatesGroup):
    waiting_topic_input = State()


# Обработка команды /start
@dp.message(CommandStart())
async def handler_start(message: Message) -> None:
    msg = (f"Привет, {html.bold(html.quote(message.from_user.first_name))}! "
           f"Я – твой персональный бот-ассистент, созданный, "
           f"чтобы помочь тебе разобраться в большом и интересном "
           f"мире программирования.\n\n"
           f"Я понимаю следующие команды:\n"
           f"{''.join([f'{cmd} – {desc},\n' for cmd, desc in commands_dict.items()])[:-2]}.")
    await message.answer(msg, parse_mode=ParseMode.HTML)

# Обработка команды /help
@dp.message(Command("help"))
async def handler_start(message: Message) -> None:
    msg = (f"Я понимаю следующие команды:\n"
           f"{''.join([f'{cmd} – {desc},\n' for cmd, desc in commands_dict.items()])[:-2]}.")
    await message.answer(msg, parse_mode=ParseMode.HTML)


# Обработка команды /setmodule
@dp.message(Command("setmodule"))
async def handler_setmodule(message: Message, state: FSMContext) -> None:
    modules = database_handler.get_modules_list()
    msg = "Введите номер модуля для погружения:\n"
    for module in modules:
        msg += f"<b>{module[0]}.</b> {module[1]}\n"
    await state.set_state(ModuleSelection.waiting_module_input)
    await message.answer(msg, parse_mode=ParseMode.HTML)

@dp.message(ModuleSelection.waiting_module_input)
async def handle_module_selection(message: Message, state: FSMContext):
    msg_text = message.text.strip()
    if not msg_text.isdigit():
        await message.answer(
            "Некорректный номер модуля. Пожалуйста, введи правильный номер.")
        return

    module_id = int(msg_text)
    module_name = database_handler.get_module_name(module_id)
    if not module_name:
        await message.answer(
            "Некорректный номер модуля. Пожалуйста, введи правильный номер.")
        return

    topics = database_handler.get_topics_list(module_id)

    if not topics:
        await message.answer(f"Темы в выбранном модуле не найдены. "
                             f"Попробуйте ввести другой номер модуля.")
        return
    # t[0] - id темы, t[1] - название темы
    topics_list = "\n".join([f"<b>{t[0]}.</b> {t[1]}" for t in topics])

    await state.set_state(TopicSelection.waiting_topic_input)
    await state.update_data(selected_module_id=module_id)
    # После выбора модуля ждём ввода темы
    await message.answer(f"Выберите тему:\n{topics_list}", parse_mode=ParseMode.HTML)


# Обработка команды /changetopic
@dp.message(Command("changetopic"))
async def handler_changetopic(message: Message) -> None:
    msg = ("Для изучения доступны следующие темы:")
    await message.answer(msg, parse_mode=ParseMode.HTML)


@dp.message(TopicSelection.waiting_topic_input)
async def handle_topic_selection(message: Message, state: FSMContext):
    msg_text = message.text.strip()
    if not msg_text.isdigit():
        await message.answer(
            "Некорректный номер темы. Пожалуйста, введи правильный номер.")
        return

    topic_id = int(msg_text)

    # Получаем сохранённый module_id из FSM
    data = await state.get_data()
    selected_module_id = data.get("selected_module_id")
    # module_name = database_handler.get_module_name(sel_module_id)

    # Проверяем наличие в базе темы с выбранным номером
    topic = database_handler.get_topic(selected_module_id, topic_id)
    if not topic:
        await message.answer(
            "Некорректный номер темы. Пожалуйста, введи правильный номер.")
        return

    # Выводим подтверждение или продолжаем выполнение логики
    await message.answer(f"<b>{topic[3]}</b>\n{topic[4]}",
                         parse_mode=ParseMode.HTML)

    # После обработки можно сбросить состояние
    await state.clear()
    await state.update_data(selected_topic_id=topic)


# Обработка произвольного сообщения от пользователя, когда группа уже выбрана
# async def handler_typing_group(message: Message, state: FSMContext) -> None:
#     await message.answer("Я не совсем понимаю, что именно нужно сделать. Пожалуйста, "
#                          "используй команды для работы со мной.")
