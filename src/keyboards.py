from aiogram.utils.keyboard import ReplyKeyboardBuilder


def gen_topic_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Повторить теорию")
    builder.button(text="У меня вопрос!")
    builder.adjust(1)
    return builder.as_markup()
