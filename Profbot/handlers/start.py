from aiogram import Router
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove


from commands import *
from handlers.quiz import start_test
from keyboards.keyboards import main_kb


start_router = Router()


@start_router.message(CommandStart(deep_link=True))
async def send_welcome(message: Message, command: CommandObject, state: FSMContext):
    if command.args == "quiz":
        await message.delete()
        await start_test(message, state)


@start_router.message(CommandStart())
async def start_no_args(message: Message):
    hi_let = f"✨ Добро пожаловать в мир профориентации, <b>{message.from_user.first_name}</b>! ✨\n"
    await message.answer(hi_let + START_COMMAND, parse_mode="HTML", reply_markup=main_kb)


@start_router.message(Command("help"))
async def send_help(message: Message):
    help_phrasal = f"Ознакомьтесь с нашим навигатором, <b><em>{message.from_user.first_name}</em></b> :\n"
    await message.answer(text=help_phrasal+HELP_COMMAND,
                        parse_mode="HTML",
                        reply_markup=ReplyKeyboardRemove())


@start_router.message(Command("description"))
async def send_desc(message: Message):
    await message.answer(text=DESC,
                        parse_mode="HTML",
                        reply_markup=main_kb)