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

# TODO Заменить на постоянное хранилище
dp = Dispatcher(storage=MemoryStorage())
bot = Bot("7581877647:AAEjqoONxSUx9Gg46IGU25wMqO1kCKkH_24")  # TODO Change token


# Обработка команды /start
@dp.message(CommandStart())
async def handler_start(message: Message, state: FSMContext) -> None:
    msg = (f"Привет, {html.bold(html.quote(message.from_user.first_name))}! "
           f"Я – твой персональный бот-ассистент, созданный, "
           f"чтобы помочь тебе разобраться в большом и интересном "
           f"мире программирования.")
    await message.answer(msg, parse_mode=ParseMode.HTML)


# Обработка команды /about
@dp.message(Command("about"))
async def handler_about(message: Message) -> None:
    msg = ("Я – твой персональный бот-ассистент, созданный, "
           "чтобы помочь тебе разобраться в большом и интересном "
           "мире программирования.")
    await message.answer(msg, parse_mode=ParseMode.HTML)


# Обработка произвольного сообщения от пользователя, когда группа уже выбрана
# async def handler_typing_group(message: Message, state: FSMContext) -> None:
#     await message.answer("Я не совсем понимаю, что именно нужно сделать. Пожалуйста, "
#                          "используй команды для работы со мной.")
