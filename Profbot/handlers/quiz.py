import matplotlib.pyplot as plt
import random
from aiogram import types, Router, F
from aiogram.filters import Command, BaseFilter
from aiogram.types import Message, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from questions.questions import QUESTIONS, MAIN_QUESTION
from questions.answers import answers_map
from recommendations.common_recommend import send_end_message
from keyboards.keyboards import ans_kb, make_vuz_keyboard, rec_button, main_kb, indf_kb
from recommendations.info import COMMON_DICT_INFO
from db.db import save_result

quiz_router = Router()

class Quiz(StatesGroup):
    who_is = State()
    in_process = State()
    recommend_vuz = State()


class AnswerFilter(BaseFilter):
    def __init__(self, valid: list[str], case_insensitive: bool = True):
        if case_insensitive:
            self.valid = {v.lower() for v in valid}
        else:
            self.valid = set(valid)
        self.case_insensitive = case_insensitive

    async def __call__(self, message: Message):
        text = (message.text or "").strip()
        if self.case_insensitive:
            text = text.lower()
        return text in self.valid


def create_pic(labels, values):
    fig, ax = plt.subplots() #создание пустого холста

    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90) #создание круговой диаграммы
    ax.axis("equal") #конкретно указали, что круг
    plt.savefig("ans.png") #сохраняем картинку

    plt.close() #закрыли окно


check = ["a", "b", "c", "d"]
check_status = ["школьник", "студент", "сотрудник"]


@quiz_router.message(Command('quiz'))
async def start_test(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(Quiz.who_is)
    await message.answer(text = MAIN_QUESTION,
                         parse_mode="HTML",
                         reply_markup=indf_kb)

@quiz_router.message(Quiz.who_is, AnswerFilter(check_status))
async def indentif_message(message: Message, state: FSMContext):
    status = message.text.lower()
    await state.update_data(status=status)

    shuffled = random.sample(QUESTIONS, len(QUESTIONS))
    start_index = 1
    await state.update_data(q_index=start_index, questions=shuffled)
    await state.set_state(Quiz.in_process)
    await message.answer(text = str(start_index)+". "+shuffled[0],
                         reply_markup=ans_kb)

@quiz_router.message(Quiz.who_is)
async def input_error_indf(message: Message):
    await message.answer(text="❌ Формат ответа неверный. Введите одну из социальных групп: школьник, студент, сотрудник")


@quiz_router.message(Quiz.in_process, AnswerFilter(check))
async def handle_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("finished"):
        return
    scores = data.get("scores", {"инженер": 0, "программист": 0, "психолог": 0, "предприниматель": 0})
    q_index = data["q_index"]
    shuffled = data["questions"]
    input_text = message.text
    if input_text == "завершить тест":
        return
    profession = answers_map[q_index][input_text]
    scores[profession] += 1
    await state.update_data(scores=scores)
    q_index += 1

    if q_index-1 < len(shuffled):
        await state.update_data(q_index=q_index)
        await message.answer(text = str(q_index)+'. '+shuffled[q_index-1],
                             reply_markup=ans_kb)
    else:
        await state.update_data(finished=True)
        total = sum(scores.values())
        names = []

        for key in scores.keys():
            names.append(key)

        percentages = [(count / total) * 100 for role, count in scores.items()]
        rounded = [round(el) for el in percentages[:-1]]
        rounded.append(100 - sum(rounded))

        stickers = ['⚙️','👨‍💻','🧠','💰']
        result = '\n'.join([f"{stickers[i]}<b>{role}</b>: {rounded[i]}%" for i, (role, _) in enumerate(scores.items())])

        scores = data.get("scores", {})
        main_prof = max(scores, key=scores.get)
        await state.update_data(main_profession=main_prof)

        create_pic(names, rounded)
        photo = FSInputFile("ans.png")

        await message.answer_photo(photo, caption="Вот ваши результаты:\n\n"+result,
                                   parse_mode="HTML",
                                   reply_markup=rec_button)

        await state.set_state(Quiz.recommend_vuz)


@quiz_router.message(Quiz.in_process, F.text.lower() == "завершить тест")
async def finish_quiz(message: Message, state: FSMContext):
    result = "неизвестно"
    await save_result(
        name=message.from_user.first_name,
        user_id=message.from_user.id,
        result=result
    )
    await state.clear()
    await message.answer(
        "Спасибо за прохождение викторины!🥰\n\nВы можете пройти её до конца, воспользовавшись командой — /quiz",
        reply_markup=main_kb
    )


@quiz_router.message(Quiz.in_process)
async def invalid_answer(message: Message):
    await message.answer("❌ Формат ответа неверный. Введите одну из букв: a, b, c, d.")


@quiz_router.message(Quiz.recommend_vuz, F.text.lower() == "получить рекомендации")
async def send_recommend(message: Message, state: FSMContext):
    data = await state.get_data()
    main_prof = data["main_profession"]
    status = data["status"]
    rec_kb = make_vuz_keyboard(main_prof, status)
    await message.answer(text=send_end_message(main_prof)+"\n"+COMMON_DICT_INFO[status][main_prof],
                         parse_mode="HTML",
                         reply_markup=rec_kb)

    result = main_prof

    await save_result(
        name=message.from_user.first_name,
        user_id=message.from_user.id,
        result=result
    )

    await message.answer(text="Спасибо за прохождение викторины!🥰\n\nВы можете пройти её вновь, воспользовавшись командой - <b>/quiz</b>",
                         parse_mode="HTML",
                         reply_markup=main_kb)

    await state.clear()


@quiz_router.message(F.text.lower() == "завершить тест")
async def the_end(message: Message, state: FSMContext):
    data = await state.get_data()
    result = data["main_profession"]
    await save_result(
        name=message.from_user.first_name,
        user_id=message.from_user.id,
        result=result
    )
    await state.clear()
    await message.answer(
        "Спасибо за прохождение викторины!🥰\n\nВы можете пройти её вновь, воспользовавшись командой — /quiz, чтобы сохранить ваши ответы",
        reply_markup=main_kb
    )









