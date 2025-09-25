from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from recommendations.links import *

main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="/start"), KeyboardButton(text="/help")],
              [KeyboardButton(text="/description"), KeyboardButton(text="/quiz")]],
    resize_keyboard=True
)

indf_kb = ReplyKeyboardMarkup (
    keyboard=[
        [KeyboardButton(text="школьник")],
        [KeyboardButton(text="студент")],
        [KeyboardButton(text="сотрудник")]
    ],
    resize_keyboard=True
)
ans_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="a"), KeyboardButton(text="b")],
              [KeyboardButton(text="c"), KeyboardButton(text="d")],
              [KeyboardButton(text="завершить тест")]
              ],
    resize_keyboard=True
)


rec_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="получить рекомендации")],
              [KeyboardButton(text="завершить тест")]],
    resize_keyboard=True
)


def make_vuz_keyboard(main_prof, status) -> InlineKeyboardMarkup:
    buttons = []
    cur_double = []
    for vuz_name, vuz_link in common_dict_recommend[status][main_prof].items():
        if len(cur_double) < 2:
            cur_double.append(InlineKeyboardButton(text=vuz_name, url=vuz_link))
        else:
            buttons.append(cur_double)
            cur_double = [InlineKeyboardButton(text=vuz_name, url=vuz_link)]
    buttons.append(cur_double)

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


