import logging as log

from aiogram import html
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault, Message
from src.database_handler import database_handler
from src.constants import MOBMENTOR_BOT_TOKEN, DEFAULT_PSSWD_FOR_TEACHER_LOGIN
import src.constants
from typing import List

default_commands =  [BotCommand(command="login",          description="зайти в свой профиль"),
                     BotCommand(command="help",           description="подробное описание команд")]

pupils_commands  =  [BotCommand(command="setmodule",      description="выбрать обучающий модуль"), 
                     BotCommand(command="changetopic",    description="выбрать/сменить тему (в рамках модуля)"),
                     BotCommand(command="repeat",         description="повторить теорию"),
                     BotCommand(command="question",       description="задать вопрос"),
                     BotCommand(command="deletequestion", description="удалить вопрос"),
                     BotCommand(command="myquestions",    description="список моих вопросов"),
                     BotCommand(command="help",           description="подробное описание команд")]

teachers_commands = [BotCommand(command="getquestions",   description="список всех вопросов"),
                     BotCommand(command="answerquestion", description="ответить на вопрос"),
                     BotCommand(command="addnewteacher",  description="добавить профиль для учителя"),
                     BotCommand(command="changepassword", description="сменить свой пароль"),

                     BotCommand(command="allmodules",     description="просмотреть все модули"),
                     BotCommand(command="alltopics",      description="просмотреть все темы в одном модуле"),
                     BotCommand(command="module",         description="просмотреть содержимое модуля"),
                     BotCommand(command="topic",          description="просмотреть содержимое темы"),

                     BotCommand(command="addnewmodule",   description="добавить новый модуль"),
                     BotCommand(command="addnewtopic",    description="добавить новую тему"),
                     BotCommand(command="changemodule",   description="изменить модуль"),
                     BotCommand(command="changetopic",    description="изменить тему"),
                     BotCommand(command="deletemodule",   description="удалить модуль"),
                     BotCommand(command="deletetopic",    description="удалить тему"),

                     BotCommand(command="help",           description="подробное описание команд")]


# TODO Заменить на постоянное хранилище
dp  = Dispatcher(storage=MemoryStorage())
bot = Bot(MOBMENTOR_BOT_TOKEN)

class Login(StatesGroup):
    waiting_answer_for_login = State()
    waiting_password_input   = State()

class TopicSelection(StatesGroup):
    waiting_module_input = State()
    waiting_topic_input  = State()

class PupilQuestionSelection(StatesGroup):
    waiting_module_input          = State()
    waiting_topic_input           = State()
    waiting_question_input        = State()

class DeleteQuestion(StatesGroup):
    waiting_question_number_input = State()

class TeacherQuestionSelection(StatesGroup):
    waiting_question_number_input = State()
    waiting_answer_input          = State()

class AddNewTeacher(StatesGroup):
    waiting_name_input  = State()
    waiting_psswd_input = State()

class ChangePassword(StatesGroup):
    waiting_psswd_input = State()

class Module(StatesGroup):
    waiting_module_input = State()

class Topic(StatesGroup):
    waiting_module_input = State()
    waiting_topic_input = State()

class NewModuleCreation(StatesGroup):
    waiting_name_input        = State()
    waiting_description_input = State()

class NewTopicCreation(StatesGroup):
    waiting_module_input = State()
    waiting_name_input   = State()
    waiting_text_input   = State()

class ChangeModuleText(StatesGroup):
    waiting_module_input      = State()
    waiting_name_input        = State()
    waiting_description_input = State()

class ChangeTopicText(StatesGroup):
    waiting_module_input = State()
    waiting_topic_input  = State()
    waiting_name_input   = State()
    waiting_text_input   = State()

class DeleteModule(StatesGroup):
    waiting_module_input = State()

class DeleteTopic(StatesGroup):
    waiting_module_input = State()
    waiting_topic_input  = State()

class EmptyContext(StatesGroup):
    teacher_empty_context = State()
    pupil_empty_context   = State()
    empty_context         = State()

async def set_menu(cmds: List[BotCommand]):
    await bot.set_my_commands(commands=cmds)

# -------- Команды незалогиненного пользователя --------
# Обработка команды /start
@dp.message(CommandStart())
async def handler_start(message: Message) -> None:
    await set_menu(default_commands)
    curr_bot_cmds = default_commands
    msg = (f"Привет, {html.bold(html.quote(message.from_user.first_name))}! "
           f"Я – твой персональный бот-ассистент, созданный, "
           f"чтобы помочь тебе разобраться в большом и интересном "
           f"мире программирования.\n\n"
           f"Я понимаю следующие команды:\n"
           f"{''.join([f'/{cmd.command} – {cmd.description},\n' for cmd in curr_bot_cmds])[:-2]}.")
    await message.answer(msg, parse_mode=ParseMode.HTML)


# Обработка команды /login
@dp.message(Command("login"))
async def handler_login(message: Message, state: FSMContext) -> None:
    await state.set_state(Login.waiting_answer_for_login)
    await message.answer("Ты учитель? Да/Нет")


# Обработка команды /help
@dp.message(Command("help"))
async def handler_start(message: Message, state: FSMContext) -> None:
    curr_bot_cmds = await bot.get_my_commands()
    msg = (f"Я понимаю следующие команды:\n"
           f"{''.join([f'/{cmd.command} – {cmd.description},\n' for cmd in curr_bot_cmds])[:-2]}.")
    await message.answer(msg)


# -------- Команды ученика --------
# Обработка команды /setmodule
@dp.message(Command("setmodule"), EmptyContext.pupil_empty_context)
async def handler_set_module(message: Message, state: FSMContext) -> None:
    modules = database_handler.get_modules_list()
    msg = "Введи номер модуля для погружения:\n"
    for module in modules:
                    #module_id       module_name
        msg += f"<b>{module[0]}.</b> {module[1]}\n"
    await state.set_state(TopicSelection.waiting_module_input)
    await message.answer(msg, parse_mode=ParseMode.HTML)


# Обработка команды /changetopic
@dp.message(Command("changetopic"), EmptyContext.pupil_empty_context)
async def handler_change_topic(message: Message, state: FSMContext) -> None:
    # Получаем сохранённый module_id из FSM контекста
    data = await state.get_data()
    selected_module_id = data.get("selected_module_id")
    if not selected_module_id:
        handler_set_module(message, state)
        return
    topics = database_handler.get_topics_list(selected_module_id)
                                    #topic_id    topic_name
    topics_list = "\n".join([f"<b>{t[0]}.</b> {t[1]}" for t in topics])
    await state.set_state(TopicSelection.waiting_topic_input)
    await message.answer(f"Выбери тему:\n{topics_list}", parse_mode=ParseMode.HTML)


# Обработка команды /repeat
@dp.message(Command("repeat"), EmptyContext.pupil_empty_context)
async def handler_repeat_topic(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    selected_module_id = data.get("selected_module_id")
    selected_topic_id = data.get("selected_topic_id")

    if not selected_module_id or not selected_topic_id:
        await handler_set_module(message, state)
        return

    topic = database_handler.get_topic(selected_module_id, selected_topic_id)

    await message.answer(
        f"Конечно, давай повторим.\n"
                                   #topic_name            module_name
        f"Сейчас ты изучаешь тему «{topic[3]}»\nиз модуля «{topic[1]}».\n\n"
        f"{topic[4]}\n" #topic_text
        f"Ты всегда можешь задать вопрос, если что-то непонятно.",
        parse_mode=ParseMode.HTML)


# Обработка команды /question
@dp.message(Command("question"), EmptyContext.pupil_empty_context)
async def handler_ask_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    selected_module_id = data.get("selected_module_id")
    selected_topic_id = data.get("selected_topic_id")

    if not selected_module_id:
        await message.answer("Прости, дорогой друг!\n"
                             "Я не могу ответить на твой вопрос,\nпока ты не выберешь обучающий модуль :(")
        msg = "Список всех модулей:\n"
        modules_list = database_handler.get_modules_list()
        if len(modules_list) > 0:
            for module_id, module_name in modules_list:
                msg += f"{module_id}. {module_name}\n"
            await message.answer(msg, parse_mode=ParseMode.HTML)
            await message.answer("Введите номер модуля")
            await state.set_state(PupilQuestionSelection.waiting_module_input)
        else:
            await message.answer("Модулей пока нет.")
            await state.set_state(EmptyContext.pupil_empty_context)
        return

    if not selected_topic_id:
        await message.answer("Прости, дорогой друг!\n"
                             "Я не могу ответить на твой вопрос,\nпока ты не выберешь тему :(")

        topics_list = database_handler.get_topics_list(selected_module_id)
        if len(topics_list) > 0:
            msg += "Введите номер темы:\n"
            for topic_id, topic_name in topics_list:
                msg += f"{topic_id}. {topic_name}\n"
            await message.answer(msg, parse_mode=ParseMode.HTML)
            await state.set_state(PupilQuestionSelection.waiting_topic_input)
        else:
            await message.answer("В выбранном ранее модуле пока нет тем.")
            await message.answer("Введите номер другого модуля")
            await state.set_state(PupilQuestionSelection.waiting_module_input)

        return

    topic = database_handler.get_topic(selected_module_id, selected_topic_id)
    questions = database_handler.get_questions_by_topic(selected_module_id, selected_topic_id)

    if len(questions) > 0:
        await message.answer(
            f"Популярные вопросы по теме:\n"
                          #question_text
            f"{''.join([f'{n+1}. {question[1]}\n' for n, question in enumerate(questions)])}\n"
            f"Введи номер вопроса, на который хочешь узнать ответ.\n"
            f"Если здесь нет твоего вопроса, введи свой вопрос.\n"
            f"Я отправлю его преподавателю и вернусь к тебе с ответом!",
            parse_mode=ParseMode.HTML)
    else:
        await message.answer(
            f"Введи свой вопрос по теме «{topic[3]}».\n" #topic_name
            f"Я отправлю его преподавателю и вернусь к тебе с ответом!")

    await state.set_state(PupilQuestionSelection.waiting_question_input)


# Обработка команды /deletequestion
@dp.message(Command("deletequestion"), EmptyContext.pupil_empty_context)
async def handler_delete_question(message: Message, state: FSMContext) -> None:
    user_name = message.from_user.username
    questions = database_handler.get_questions_by_user(user_name)
    if len(questions) > 0:
        question_num = 0
        msg = f"Ты задал следующие вопросы:\n"
        for _,_, _, _, question_text, question_answer_text in questions:
            msg += f"{question_num + 1}. {question_text}"
            if question_answer_text == "" or question_answer_text == None:
                msg += "\n"
            else:
                msg += f" -- Ответ: {question_answer_text}\n"
            question_num += 1
        await message.answer(msg, parse_mode=ParseMode.HTML)

        await state.set_state(DeleteQuestion.waiting_question_number_input)
        await message.answer("Какой вопрос ты хочешь удалить?")
    else:
        await message.answer("Ты пока не задал ни одного вопроса.")
        await state.set_state(EmptyContext.pupil_empty_context)


# Обработка команды /myquestions
@dp.message(Command("myquestions"), EmptyContext.pupil_empty_context)
async def handler_my_questions(message: Message, state: FSMContext) -> None:
    user_name = message.from_user.username
    questions = database_handler.get_questions_by_user(user_name)
    if len(questions) > 0:
        msg = f"Ты задал следующие вопросы:\n"
        for _, module_id, topic_id, _, question_text, question_answer_text in questions:
            msg += f"{module_id}.{topic_id} {question_text}"
            if question_answer_text == "" or question_answer_text == None:
                msg += "\n"
            else:
                msg += f" -- Ответ: {question_answer_text}\n"
        await message.answer(msg, parse_mode=ParseMode.HTML)
    else:
        await message.answer("Ты пока не задал ни одного вопроса.", parse_mode=ParseMode.HTML)
    await state.set_state(EmptyContext.pupil_empty_context)


# --------- Команды учителя ---------
# Обработка команды /getquestions
@dp.message(Command("getquestions"), EmptyContext.teacher_empty_context)
async def handler_get_questions(message: Message, state: FSMContext) -> None:
    questions = database_handler.get_questions_without_answer()
    if len(questions) > 0:
        msg = (f"Вопросы без ответов:\n"
            f"{''.join([f'#{question_id} Тема: {module_id}.{topic_id} {question_text}\n'
                                                for question_id, module_id,
                                                    topic_id, question_text
                                                in questions])[:-2]}.")
        await message.answer(msg, parse_mode=ParseMode.HTML)
    else:
        await message.answer("Новых вопросов пока нет.", parse_mode=ParseMode.HTML)
    await state.set_state(EmptyContext.teacher_empty_context)


# Обработка команды /answerquestion
@dp.message(Command("answerquestion"), EmptyContext.teacher_empty_context)
async def handler_answer_question(message: Message, state: FSMContext) -> None:
    questions = database_handler.get_questions_without_answer()
    if len(questions) > 0:
        msg = (f"Вопросы без ответов:\n"
            f"{''.join([f'#{question_id} Тема: {module_id}.{topic_id} {question_text}\n'
                                                for question_id, module_id,
                                                    topic_id, question_text
                                                in questions])[:-2]}.")
        await message.answer(msg, parse_mode=ParseMode.HTML)
        await state.set_state(TeacherQuestionSelection.waiting_question_number_input)
        await message.answer("Введите номер вопроса для ответа\n")
    else:
        await message.answer("Новых вопросов пока нет.", parse_mode=ParseMode.HTML) 
        await state.set_state(EmptyContext.teacher_empty_context)


# Обработка команды /addnewteacher
@dp.message(Command("addnewteacher"), EmptyContext.teacher_empty_context)
async def handler_add_new_teacher(message: Message, state: FSMContext) -> None:
    msg = ("Введите имя нового учителя в TG (без символа @).\n"
           "Eго можно найти в профиле пользователя, это строка, начинающаяся с символа @.\n")
    await state.set_state(AddNewTeacher.waiting_name_input)
    await message.answer(msg)


# Обработка команды /changepassword
@dp.message(Command("changepassword"), EmptyContext.teacher_empty_context)
async def handler_change_password(message: Message, state: FSMContext) -> None:
    await state.set_state(ChangePassword.waiting_psswd_input)
    await message.answer("Введите новый пароль")


# Обработка команды /allmodules
@dp.message(Command("allmodules"), EmptyContext.teacher_empty_context)
async def handler_all_modules(message: Message, state: FSMContext) -> None:
    modules = database_handler.get_modules_list()
    if len(modules) > 0:
        msg = "Модули:\n"
        for module in modules:
                        #module_id       module_name
            msg += f"<b>{module[0]}.</b> {module[1]}\n"
        await message.answer(msg, parse_mode=ParseMode.HTML)
    else:
        await message.answer("Модулей пока нет.")
    await state.set_state(EmptyContext.teacher_empty_context)


# Обработка команды /alltopics
@dp.message(Command("alltopics"), EmptyContext.teacher_empty_context)
async def handler_all_topics(message: Message, state: FSMContext) -> None:
    msg = "Список всех тем по модулям:\n"
    modules_list = database_handler.get_modules_list()
    if len(modules_list) > 0:
        for module_id, module_name in modules_list:
            msg += f"{module_id}. {module_name}\n"
            topics_list = database_handler.get_topics_list(module_id)
            if len(topics_list) == 0:
                msg += "   В этом модуле пока нет тем.\n"
            for topic_id, topic_name in topics_list:
                msg += f"   {topic_id}. {topic_name}\n"
        await message.answer(msg)
    else:
        await message.answer("Модулей пока нет.")
    await state.set_state(EmptyContext.teacher_empty_context)


# Обработка команды /module
@dp.message(Command("module"), EmptyContext.teacher_empty_context)
async def handler_module(message: Message, state: FSMContext) -> None:
    modules = database_handler.get_modules_list()
    if len(modules) > 0:
        msg = "Модули:\n"
        for module in modules:
                        #module_id       module_name
            msg += f"<b>{module[0]}.</b> {module[1]}\n"
        await message.answer(msg, parse_mode=ParseMode.HTML)
        await state.set_state(Module.waiting_module_input)
    else:
        await message.answer("Модулей пока нет.")
        await state.set_state(EmptyContext.teacher_empty_context)


# Обработка команды /topic
@dp.message(Command("topic"), EmptyContext.teacher_empty_context)
async def handler_module(message: Message, state: FSMContext) -> None:
    modules = database_handler.get_modules_list()
    if len(modules) > 0:
        msg = "Модули:\n"
        for module in modules:
                        #module_id       module_name
            msg += f"<b>{module[0]}.</b> {module[1]}\n"
        await message.answer(msg, parse_mode=ParseMode.HTML)
        await state.set_state(Topic.waiting_module_input)
    else:
        await message.answer("Модулей пока нет.")
        await state.set_state(EmptyContext.teacher_empty_context)


# Обработка команды /addnewmodule
@dp.message(Command("addnewmodule"), EmptyContext.teacher_empty_context)
async def handler_add_new_module(message: Message, state: FSMContext) -> None:
    await state.set_state(NewModuleCreation.waiting_name_input)
    await message.answer("Введите название нового модуля")


# Обработка команды /addnewtopic
@dp.message(Command("addnewtopic"), EmptyContext.teacher_empty_context)
async def handler_add_new_topic(message: Message, state: FSMContext) -> None:
    msg = "Список всех модулей:\n"
    modules_list = database_handler.get_modules_list()
    if len(modules_list) > 0:
        for module_id, module_name in modules_list:
            msg += f"{module_id}. {module_name}\n"
        await message.answer(msg)
        await state.set_state(NewTopicCreation.waiting_module_input)
        await message.answer("Введите номер модуля для добавления новой темы", parse_mode=ParseMode.HTML)
    else:
        await message.answer("Модулей пока нет.")
        await state.set_state(EmptyContext.teacher_empty_context)


# Обработка команды /changemodule
@dp.message(Command("changemodule"), EmptyContext.teacher_empty_context)
async def handler_change_module(message: Message, state: FSMContext) -> None:
    msg = "Список всех модулей:\n"
    modules_list = database_handler.get_modules_list()
    if len(modules_list) > 0:
        for module_id, module_name in modules_list:
            msg += f"{module_id}. {module_name}\n"
        await message.answer(msg)
        await state.set_state(ChangeModuleText.waiting_module_input)
        await message.answer("Введите номер модуля для изменения")
    else:
        await message.answer("Модулей пока нет.")
        await state.set_state(EmptyContext.teacher_empty_context)


# Обработка команды /changetopic
@dp.message(Command("changetopic"), EmptyContext.teacher_empty_context)
async def handler_change_topic(message: Message, state: FSMContext) -> None:
    msg = "Список всех тем по модулям:\n"
    modules_list = database_handler.get_modules_list()
    if len(modules_list) > 0:
        for module_id, module_name in modules_list:
            msg += f"{module_id}. {module_name}\n"
            topics_list = database_handler.get_topics_list(module_id)
            if len(topics_list) == 0:
                msg += "   В этом модуле пока нет тем.\n"
            for topic_id, topic_name in topics_list:
                msg += f"   {topic_id}. {topic_name}\n"
        await message.answer(msg)
        await state.set_state(ChangeTopicText.waiting_module_input)
        await message.answer("Введите номер модуля для изменения")
    else:
        await message.answer("Модулей пока нет.")
        await state.set_state(EmptyContext.teacher_empty_context)


# Обработка команды /deletemodule
@dp.message(Command("deletemodule"), EmptyContext.teacher_empty_context)
async def handler_delete_module(message: Message, state: FSMContext) -> None:
    msg = "Список всех модулей:\n"
    modules_list = database_handler.get_modules_list()
    if len(modules_list) > 0:
        for module_id, module_name in modules_list:
            msg += f"{module_id}. {module_name}\n"
        await message.answer(msg, parse_mode=ParseMode.HTML)
        await state.set_state(DeleteModule.waiting_module_input)
        await message.answer("ВНИМАНИЕ: это действие удалит все темы в модуле.\nВведите номер модуля для удаления")
    else:
        await message.answer("Модулей пока нет.")
        await state.set_state(EmptyContext.teacher_empty_context)


# Обработка команды /deletetopic
@dp.message(Command("deletetopic"), EmptyContext.teacher_empty_context)
async def handler_delete_topic(message: Message, state: FSMContext) -> None:
    modules_list = database_handler.get_modules_list()
    there_is_at_least_one_theme = False
    if len(modules_list) > 0:
        msg = "Список всех тем по модулям:\n"
        for module_id, module_name in modules_list:
            msg += f"{module_id}. {module_name}\n"
            topics_list = database_handler.get_topics_list(module_id)
            if len(topics_list) == 0:
                msg += "   В этом модуле пока нет тем.\n"
                continue
            there_is_at_least_one_theme = True
            for topic_id, topic_name in topics_list:
                msg += f"   {topic_id}. {topic_name}\n"
        await message.answer(msg, parse_mode=ParseMode.HTML)
        if there_is_at_least_one_theme:
            await state.set_state(DeleteTopic.waiting_module_input)
            await message.answer("Введите номер модуля для удаления в нём темы")
        else:
            await state.set_state(EmptyContext.teacher_empty_context)
    else:
        await message.answer("Модулей пока нет.")
        await state.set_state(EmptyContext.teacher_empty_context)


# --------- Описание состояний ---------
@dp.message(Login.waiting_answer_for_login)
async def handle_waiting_answer_for_login(message: Message, state: FSMContext):
    msg_text = message.text.strip()
    if msg_text == "Да":
        await state.set_state(Login.waiting_password_input)
        await message.answer("Введите пароль от своего учительского профиля")
    elif msg_text == "Нет":
        await set_menu(pupils_commands)
        pupil_role_id = database_handler.get_role_id(src.constants.PUPIL_ROLE_TEXT)[0]
        user = database_handler.user_exist(message.from_user.username, pupil_role_id)
        if user is None:
            database_handler.add_new_pupil(message.from_user.username)
            await message.answer("Я сохранил твой профиль. Теперь ты можешь работать")
        else:
            await message.answer("Ты успешно авторизовался")
        await state.set_state(EmptyContext.pupil_empty_context)
    else:
        await message.answer("Не понимаю ответ, я ожидаю только Да или Нет")
        await state.set_state(EmptyContext.empty_context)


@dp.message(Login.waiting_password_input)
async def handle_waiting_password(message: Message, state: FSMContext):
    msg_text = message.text.strip()
    teacher_role_id = database_handler.get_role_id(src.constants.TEACHER_ROLE_TEXT)[0]
    user = database_handler.user_exist(message.from_user.username, teacher_role_id, msg_text)
    if not user:
        if msg_text == DEFAULT_PSSWD_FOR_TEACHER_LOGIN:
            database_handler.add_new_teacher(message.from_user.username, DEFAULT_PSSWD_FOR_TEACHER_LOGIN)
            await set_menu(teachers_commands)
            await state.set_state(EmptyContext.teacher_empty_context)
            await message.answer("Вы успешно авторизовались.")
        else:
            await set_menu(default_commands)
            await state.set_state(EmptyContext.empty_context)
            await message.answer("Такого учительского профиля не существует.")
    else:
        await set_menu(teachers_commands)
        await state.set_state(EmptyContext.teacher_empty_context)
        await message.answer("Вы успешно авторизовались.")


@dp.message(TopicSelection.waiting_module_input)
async def handle_module_selection(message: Message, state: FSMContext):
    msg_text = message.text.strip()
    if not msg_text.isdigit():
        await message.answer("Некорректный номер модуля. Пожалуйста, введи правильный номер.")
        return

    module_id = int(msg_text)
    module_name = database_handler.get_module_name(module_id)
    if not module_name:
        await message.answer("Некорректный номер модуля. Пожалуйста, введи правильный номер.")
        return

    topics = database_handler.get_topics_list(module_id)

    if not topics:
        await message.answer(f"Темы в выбранном модуле не найдены. Попробуй ввести другой номер модуля.")
        return

                                #topic_id    topic_name
    topics_list = "\n".join([f"<b>{t[0]}.</b> {t[1]}" for t in topics])

    await state.update_data(selected_module_id=module_id)
    await state.set_state(TopicSelection.waiting_topic_input)
    await message.answer(f"Выбери тему:\n{topics_list}", parse_mode=ParseMode.HTML)


@dp.message(TopicSelection.waiting_topic_input)
async def handle_topic_selection(message: Message, state: FSMContext):
    msg_text = message.text.strip()
    if not msg_text.isdigit():
        await message.answer("Некорректный номер темы. Пожалуйста, введи правильный номер.")
        return

    topic_id = int(msg_text)

    data = await state.get_data()
    selected_module_id = data.get("selected_module_id")

    topic = database_handler.get_topic(selected_module_id, topic_id)
    if not topic:
        await message.answer("Некорректный номер темы. Пожалуйста, введи правильный номер.")
        return

    await message.answer(f"{topic[4]}\n" #topic_text
                         f"------------\n"
                         f"Модуль: {topic[1]}\n" #module_name
                         f"Тема:   {topic[3]}\n", #topic_name
                         parse_mode=ParseMode.HTML)

    await state.set_state(EmptyContext.pupil_empty_context)
    await state.update_data(selected_module_id=selected_module_id, selected_topic_id=topic_id)


@dp.message(PupilQuestionSelection.waiting_module_input)
async def handle_waiting_p_quesition_module_input(message: Message, state: FSMContext) -> None:
    module_id = message.text.strip()
    if not module_id.isdigit():
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return

    module = database_handler.get_module(int(module_id))
    if module == None:
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return

    await state.update_data(selected_module_id=module_id)

    topics_list = database_handler.get_topics_list(module_id)
    if len(topics_list) > 0:
        msg = "Введите номер темы:\n"
        for topic_id, topic_name in topics_list:
            msg += f"{topic_id}. {topic_name}\n"
        await message.answer(msg, parse_mode=ParseMode.HTML)
        await state.set_state(PupilQuestionSelection.waiting_topic_input)
    else:
        await message.answer("В этом модуле пока нет тем.")
        await state.set_state(EmptyContext.pupil_empty_context)


@dp.message(PupilQuestionSelection.waiting_topic_input)
async def handle_waiting_p_quesition_topic_input(message: Message, state: FSMContext) -> None:
    topic_id = message.text.strip()
    if not topic_id.isdigit():
        await message.answer("Некорректный номер темы. Пожалуйста, введите правильный номер.")
        return

    data = await state.get_data()
    module_id = data.get("selected_module_id")
    topic = database_handler.get_topic(module_id, int(topic_id))
    if topic == None:
        await message.answer("Некорректный номер темы. Пожалуйста, введите правильный номер.")
        return

    await state.update_data(selected_topic_id=topic_id)

    topic = database_handler.get_topic(module_id, topic_id)
    questions = database_handler.get_questions_by_topic(module_id, topic_id)
    if len(questions) > 0:
        await message.answer(
            f"Популярные вопросы по теме:\n"
                          #question_text
            f"{''.join([f'{n+1}. {question[1]}\n' for n, question in enumerate(questions)])}\n"
            f"Введи номер вопроса, на который хочешь узнать ответ.\n"
            f"Если здесь нет твоего вопроса, введи свой вопрос.\n"
            f"Я отправлю его преподавателю и вернусь к тебе с ответом!",
            parse_mode=ParseMode.HTML)
    else:
        await message.answer(
            f"Введи свой вопрос по теме «{topic[3]}».\n" #topic_name
            f"Я отправлю его преподавателю и вернусь к тебе с ответом!")

    await state.set_state(PupilQuestionSelection.waiting_question_input)


@dp.message(PupilQuestionSelection.waiting_question_input)
async def handler_question_selection_or_input(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    selected_module_id = data.get("selected_module_id")
    selected_topic_id = data.get("selected_topic_id")

    msg_text = message.text.strip()
    if msg_text.isdigit():
        question_num = int(msg_text)-1
        questions = database_handler.get_questions_by_topic(selected_module_id, selected_topic_id)

        if question_num < 0 or question_num > len(questions):
            await message.answer("Здесь нет вопроса с таким номером.\nПопробуй ввести другой номер или напиши свой вопрос.")

        question_id = questions[question_num][0]

        question_with_answer = database_handler.get_question_answer(selected_module_id, selected_topic_id, question_id)
        if question_with_answer != None:
            await message.answer(f"Ответ:\n{question_with_answer[0]}", parse_mode=ParseMode.HTML) #question_answer_text
        else:
            await message.answer("Здесь нет вопроса с таким номером.\n"
                                 "Попробуй ввести другой номер или напиши свой вопрос.")
        await state.set_state(EmptyContext.pupil_empty_context)
        return

    database_handler.add_question(selected_module_id, selected_topic_id, message.from_user.username, msg_text)
    await message.answer("Хорошо, друг! Я запомнил твой вопрос и вернусь, когда преподаватель ответит на него.")
    await state.set_state(EmptyContext.pupil_empty_context)


@dp.message(DeleteQuestion.waiting_question_number_input)
async def handle_waiting_p_quesition_number_input(message: Message, state: FSMContext) -> None:
    msg_text = message.text.strip()
    if not msg_text.isdigit():
        await message.answer("Некорректный номер вопроса. Пожалуйста, введи правильный номер.")
        await state.set_state(PupilQuestionSelection.waiting_question_number_input)

    questions = database_handler.get_questions_by_user(message.from_user.username)
    selected_question = int(msg_text)-1
    if selected_question < 0 or selected_question > len(questions):
        await message.answer("Здесь нет вопроса с таким номером.\nПопробуй ввести другой номер.")
        await state.set_state(PupilQuestionSelection.waiting_question_number_input)

    question_id = questions[selected_question][0]
    database_handler.delete_question(question_id)
    await message.answer("Вопрос был удалён.")
    await state.set_state(EmptyContext.pupil_empty_context)


@dp.message(TeacherQuestionSelection.waiting_question_number_input)
async def handle_waiting_t_quesition_number_input(message: Message, state: FSMContext) -> None:
    msg_text = message.text.strip()
    if not msg_text.isdigit():
        await message.answer("Некорректный номер вопроса. Пожалуйста, введите правильный номер.")

    question_id = int(msg_text)
    question = database_handler.get_question_text(question_id)
    if not question:
        await message.answer("Некорректный номер вопроса. Пожалуйста, введите правильный номер.")

    await state.update_data(selected_question=question_id)

    await state.set_state(TeacherQuestionSelection.waiting_answer_input)
    await message.answer(f"Вы хотите ответить на этот вопрос: {question[0]}\nВведите ответ", parse_mode=ParseMode.HTML)


@dp.message(TeacherQuestionSelection.waiting_answer_input)
async def handler_answer_question_input(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    question_id = data.get("selected_question")
    answer_text = message.text.strip()
    database_handler.answer_question(question_id, answer_text)
    await state.set_state(EmptyContext.teacher_empty_context)
    await message.answer("Ответ записан.")
    username = database_handler.get_question_user(question_id)[0]
    question_text = database_handler.get_question_text(question_id)[0]
    msg = f"<b>{username}</b>, учитель ответил на твой вопрос \"{question_text}\"!\n"
    msg += f"Чтобы посмотреть ответ, используй команду /myquestions."
    bot.send_message(chat_id=username, text=msg, parse_mode=ParseMode.HTML)


@dp.message(AddNewTeacher.waiting_name_input)
async def handle_waiting_teacher_name_input(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(teacher_name=name)
    await message.answer("Введите пароль")
    await state.set_state(AddNewTeacher.waiting_psswd_input)


@dp.message(AddNewTeacher.waiting_psswd_input)
async def handle_waiting_teacher_psswd_input(message: Message, state: FSMContext):
    data = await state.get_data()
    teacher_name = data.get("teacher_name")
    psswd = message.text.strip()
    database_handler.add_new_teacher(teacher_name, psswd)
    await state.set_state(EmptyContext.teacher_empty_context)
    await message.answer("Учитель успешно добавлен.")


@dp.message(ChangePassword.waiting_psswd_input)
async def handle_waiting_new_password(message: Message, state: FSMContext):
    msg_text = message.text.strip()
    database_handler.change_teacher_password(message.from_user.username, msg_text)
    await state.set_state(EmptyContext.teacher_empty_context)
    await message.answer("Пароль успешно изменён.")


@dp.message(Module.waiting_module_input)
async def handle_waiting_module_input(message: Message, state: FSMContext):
    module_id = message.text.strip()
    if not module_id.isdigit():
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return

    module = database_handler.get_module(int(module_id))
    if module == None:
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return
    msg = f"<b>{module[0]}</b>\n"
    msg += f"{module[1]}\n"
    topics = database_handler.get_topics_list(int(module_id))
    if len(topics) > 0:
        msg += "Список тем:\n"
                                #topic_id    topic_name
        msg += "\n".join([f"   <b>{t[0]}.</b> {t[1]}" for t in topics])
    else:
        msg += "Темы в выбранном модуле не найдены."
    await message.answer(msg, parse_mode=ParseMode.HTML)
    await state.set_state(EmptyContext.teacher_empty_context)


@dp.message(Topic.waiting_module_input)
async def handle_waiting_module_input(message: Message, state: FSMContext):
    module_id = message.text.strip()
    if not module_id.isdigit():
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return

    module = database_handler.get_module(int(module_id))
    if module == None:
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return

    topics = database_handler.get_topics_list(int(module_id))
    if len(topics) > 0:
        await state.update_data(module_id=int(module_id))
        msg = "Список тем:\n"
                                #topic_id    topic_name
        msg += "\n".join([f"<b>{t[0]}.</b> {t[1]}" for t in topics])
        await message.answer(msg, parse_mode=ParseMode.HTML)
        await message.answer("Введите номер темы")
        await state.set_state(Topic.waiting_topic_input)
    else:
        await message.answer("Темы в выбранном модуле не найдены.", parse_mode=ParseMode.HTML)
        await state.set_state(EmptyContext.teacher_empty_context)


@dp.message(Topic.waiting_topic_input)
async def handle_waiting_topic_input(message: Message, state: FSMContext):
    topic_id = message.text.strip()
    if not topic_id.isdigit():
        await message.answer("Некорректный номер темы. Пожалуйста, введите правильный номер.")
        return

    data = await state.get_data()
    module_id = data.get("module_id")
    topic = database_handler.get_topic(module_id, int(topic_id))
    if topic == None:
        await message.answer("Некорректный номер темы. Пожалуйста, введите правильный номер.")
        return
    msg = f"<b>{topic[3]}</b>\n"
    msg += f"{topic[4]}\n"
    await message.answer(msg, parse_mode=ParseMode.HTML)
    await state.set_state(EmptyContext.teacher_empty_context)


@dp.message(NewModuleCreation.waiting_name_input)
async def handle_waiting_module_name_input(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(module_name=name)
    await state.set_state(NewModuleCreation.waiting_description_input)
    await message.answer("Введите описание для нового модуля")


@dp.message(NewModuleCreation.waiting_description_input)
async def handle_waiting_description_input(message: Message, state: FSMContext):
    data = await state.get_data()
    module_name = data.get("module_name")
    module_descr = message.text.strip()
    database_handler.add_new_module(module_name, module_descr)
    await state.set_state(EmptyContext.teacher_empty_context)
    await message.answer("Новый модуль успешно добавлен.")


@dp.message(NewTopicCreation.waiting_module_input)
async def handle_waiting_module_input(message: Message, state: FSMContext):
    module_id = message.text.strip()
    if not module_id.isdigit():
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return

    module_name = database_handler.get_module_name(int(module_id))
    if module_name == None:
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return

    await state.update_data(module_id=int(module_id))
    await state.set_state(NewTopicCreation.waiting_name_input)
    await message.answer("Введите название для новой темы")


@dp.message(NewTopicCreation.waiting_name_input)
async def handle_waiting_topic_name_input(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(topic_name=name)
    await state.set_state(NewTopicCreation.waiting_text_input)
    await message.answer("Введите текст для новой темы")


@dp.message(NewTopicCreation.waiting_text_input)
async def handle_waiting_topic_text_input(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    module_id = data.get("module_id")
    topic_name = data.get("topic_name")
    database_handler.add_new_topic(module_id, topic_name, text)
    await state.set_state(EmptyContext.teacher_empty_context)
    await message.answer("Новая тема успешно добавлена.")


@dp.message(ChangeModuleText.waiting_module_input)
async def handle_waiting_module_input(message: Message, state: FSMContext):
    module_id = message.text.strip()
    if not module_id.isdigit():
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return

    module_name = database_handler.get_module_name(int(module_id))
    if module_name == None:
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return

    await state.update_data(module_id=int(module_id))
    await state.set_state(ChangeModuleText.waiting_name_input)
    await message.answer("Введите новое название для модуля")


@dp.message(ChangeModuleText.waiting_name_input)
async def handle_waiting_module_name_input(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(module_name=name)
    await state.set_state(ChangeModuleText.waiting_description_input)
    await message.answer("Введите новое описание для модуля")


@dp.message(ChangeModuleText.waiting_description_input)
async def handle_waiting_module_description_input(message: Message, state: FSMContext):
    data = await state.get_data()
    module_id = data.get("module_id")
    module_name = data.get("module_name")
    module_descr = message.text.strip()
    database_handler.update_module(module_id, module_name, module_descr)
    await state.set_state(EmptyContext.teacher_empty_context)
    await message.answer("Модуль успешно изменён.")


@dp.message(ChangeTopicText.waiting_module_input)
async def handle_waiting_module_input(message: Message, state: FSMContext):
    module_id = message.text.strip()
    if not module_id.isdigit():
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return

    module_name = database_handler.get_module_name(int(module_id))
    if module_name == None:
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return

    await state.update_data(module_id=int(module_id))
    await state.set_state(ChangeTopicText.waiting_topic_input)
    await message.answer("Введите номер темы")


@dp.message(ChangeTopicText.waiting_topic_input)
async def handle_waiting_topic_input(message: Message, state: FSMContext):
    topic_id = message.text.strip()
    if not topic_id.isdigit():
        await message.answer("Некорректный номер темы. Пожалуйста, введите правильный номер.")
        return

    data = await state.get_data()
    module_id = data.get("module_id")
    topic_name = database_handler.get_topic(module_id, topic_id)
    if topic_name == None:
        await message.answer("Некорректный номер темы. Пожалуйста, введите правильный номер.")
        return

    await state.update_data(topic_id=int(topic_id))
    await state.set_state(ChangeTopicText.waiting_name_input)
    await message.answer("Введите новое название темы")


@dp.message(ChangeTopicText.waiting_name_input)
async def handle_waiting_topic_name_input(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(topic_name=name)
    await state.set_state(ChangeTopicText.waiting_text_input)
    await message.answer("Введите новый текст темы")


@dp.message(ChangeTopicText.waiting_text_input)
async def handle_waiting_topic_text_input(message: Message, state: FSMContext):
    data = await state.get_data()
    module_id = data.get("module_id")
    topic_id = data.get("topic_id")
    topic_name = data.get("topic_name")
    topic_text = message.text.strip()
    database_handler.update_topic(module_id, topic_id, topic_name, topic_text)
    await state.set_state(EmptyContext.teacher_empty_context)
    await message.answer("Тема успешно изменена.")


@dp.message(DeleteModule.waiting_module_input)
async def handle_waiting_module_input(message: Message, state: FSMContext):
    module_id = message.text.strip()
    if not module_id.isdigit():
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return

    module_name = database_handler.get_module_name(int(module_id))
    if module_name == None:
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return

    database_handler.delete_module(int(module_id))
    await state.set_state(EmptyContext.teacher_empty_context)
    await message.answer("Модуль был успешно удалён.")


@dp.message(DeleteTopic.waiting_module_input)
async def handle_waiting_module_input(message: Message, state: FSMContext):
    module_id = message.text.strip()
    if not module_id.isdigit():
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return

    module_name = database_handler.get_module_name(int(module_id))
    if module_name == None:
        await message.answer("Некорректный номер модуля. Пожалуйста, введите правильный номер.")
        return
    topics_list = database_handler.get_topics_list(int(module_id))
    if len(topics_list) == 0:
        await message.answer("В этом модуле нет тем.")
        await state.set_state(EmptyContext.teacher_empty_context)
    else:
        await state.update_data(module_id=int(module_id))
        await state.set_state(DeleteTopic.waiting_topic_input)
        await message.answer("Введите номер темы")


@dp.message(DeleteTopic.waiting_topic_input)
async def handle_waiting_topic_input(message: Message, state: FSMContext):
    topic_id = message.text.strip()
    if not topic_id.isdigit():
        await message.answer("Некорректный номер темы. Пожалуйста, введите правильный номер.")
        return

    data = await state.get_data()
    module_id = data.get("module_id")
    topic_name = database_handler.get_topic(module_id, topic_id)
    if topic_name == None:
        await message.answer("Некорректный номер темы. Пожалуйста, введите правильный номер.")
        return

    database_handler.delete_topic(module_id, int(topic_id))
    await state.set_state(EmptyContext.teacher_empty_context)
    await message.answer("Тема была успешно удалена.")


# Обработка произвольного текста вне контекста запрошенного ботом ввода для учителя
@dp.message(EmptyContext.teacher_empty_context)
async def handler_some_text_selected(message: Message) -> None:
    await message.answer("Вы можете добавить или изменить старые темы, а также поотвечать на вопросы учеников.\n"
                         "Если хотите увидеть помощь по командам, вызовите /help.")


# Обработка произвольного текста вне контекста запрошенного ботом ввода для ученика
@dp.message(EmptyContext.pupil_empty_context)
async def handler_some_text_selected(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    selected_module_id = data.get("selected_module_id")
    selected_topic_id = data.get("selected_topic_id")

    if not selected_module_id or not selected_topic_id:
        await message.answer("Если хочешь увидеть помощь по командам, вызови /help.")
    else:
        topic = database_handler.get_topic(selected_module_id, selected_topic_id)
        await message.answer(
                                    #topic_text           module_name
            f"Сейчас ты изучаешь тему «{topic[3]}»\nиз модуля «{topic[1]}».\n"
            f"Если хочешь увидеть помощь по командам, вызови /help.",
            parse_mode=ParseMode.HTML)


# Обработка произвольного текста вне контекста запрошенного ботом ввода для неавторизованного пользователя
@dp.message(EmptyContext.empty_context)
async def handler_some_text_selected(message: Message) -> None:
    await message.answer("Перед началом работы ты должен авторизоваться. Вызови команду /login")


@dp.message()
async def handler_some_text(message: Message) -> None:
    await handler_some_text_selected(message)
