import asyncio
import logging
import random
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import psycopg2

logging.basicConfig(level=logging.INFO)

TOKEN = "6954617858:AAHDmgeS1LtM2L0SgqL4u5XBn0vmHdovJ0k"

DBNAME = "savol_bot"
USER = "postgres"
PASSWORD = "4250507t"
HOST = "localhost"
PORT = "5432"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_answers = {}


class Database:
    def __init__(self, dbname, user, password, host, port):
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cursor = self.conn.cursor()

    def execute_query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close_connection(self):
        self.conn.close()


async def on_start(message: types.Message):
    await message.answer("Test ni boshlash uchun /start_test bosing")


async def start_test(message: types.Message):
    global user_answers
    user_answers = {}

    questions = fetch_questions_from_postgres()

    random.shuffle(questions)
    await message.answer("Test")

    for i, (questions_id, question_text, option_a, option_b, option_c, option_d, correct_answer) in enumerate(questions, start=1):
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="A"), KeyboardButton(text="B")],
                [KeyboardButton(text="C"), KeyboardButton(text="D")],
            ],
            resize_keyboard=True
        )

        await bot.send_message(message.chat.id, f"Savol {i}: \n{question_text}\n\n"
                                                f"{option_a}\n"
                                                f"{option_b}\n"
                                                f"{option_c}\n"
                                                f"{option_d}", reply_markup=markup,)

        answer = await bot.send_message(message.chat.id, text="javobingizni kiriting")
        user_answer = answer.text

        user_answers[f"Savol {i}"] = {'user_answer1': user_answer, 'correct_answer': correct_answer}

        await asyncio.sleep(5)

    await display_test_summary(message)


async def display_test_summary(message: types.Message):
    result_message = "Test yakunlandi natija:\n"
    for question_number, answers in user_answers.items():
        user_answer2 = answers["user_answer1"]
        correct_answer = answers["correct_answer"]

        result_message += f"{question_number}: Sizning javob - {user_answer2}, To'g'ri javob - {correct_answer}\n"

    await bot.send_message(message.chat.id, result_message)


def fetch_questions_from_postgres():
    db = Database(DBNAME, USER, PASSWORD, HOST, PORT)

    query = "SELECT * FROM questions;"
    questions = db.execute_query(query)

    db.close_connection()

    return questions


if __name__ == "__main__":
    from aiogram import executor

    dp.register_message_handler(on_start, commands=["start"])
    dp.register_message_handler(start_test, commands=["start_test"])

    executor.start_polling(dp, skip_updates=True)