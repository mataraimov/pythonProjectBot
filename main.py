import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import PollAnswer
from quizzer import Quiz

bot = Bot(token="5600572092:AAFJlwV3HAAi2AebGcxLCt_c4r0WQ3PIuS8")
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

quizzes_database = {}
quizzes_owners = {}

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    poll_keyboard.add(types.KeyboardButton(text="Создать викторину",
                                           request_poll=types.KeyboardButtonPollType(type=types.PollType.QUIZ)))
    poll_keyboard.add(types.KeyboardButton(text="Пройти тест"))
    poll_keyboard.add(types.KeyboardButton(text="Тест по JS"))
    poll_keyboard.add(types.KeyboardButton(text="Отмена"))
    await message.answer("Нажмите на кнопку ниже и создайте викторину! "
                            "Внимание: в дальнейшем она будет публичной (неанонимной).", reply_markup=poll_keyboard)


@dp.message_handler(lambda message: message.text == "Отмена")
async def action_cancel(message: types.Message):
    remove_keyboard = types.ReplyKeyboardRemove()
    await message.answer("Действие отменено. Введите /start, чтобы начать заново.", reply_markup=remove_keyboard)


@dp.message_handler(lambda message: message.text == "Пройти тест")
async def start_quiz(message: types.Message):
    if str(message.chat.id) in quizzes_database.keys():

        for item in quizzes_database[str(message.chat.id)]:
            my_quiz = await bot.send_poll(message.chat.id, item.question, item.options, type='quiz',
                                        correct_option_id=item.correct_option_id, is_anonymous=False)
            await asyncio.sleep(5)

    else:
        await message.answer('Не найдено ни одной викторины')


@dp.message_handler(lambda message: message.text == "Тест по JS")
async def js_quiz(message: types.Message):
    with open('test_js.json', 'r', encoding='utf-8') as f:
        my_data = json.load(f)
        print(my_data)

    for item in my_data:
        data = json.loads(item)

        my_quiz = await bot.send_poll(message.chat.id, data['question'], data['options'], type='quiz',
                                        correct_option_id=data['correct_option_id'], is_anonymous=False)
        await asyncio.sleep(5)


@dp.message_handler(content_types=["poll"])
async def msg_with_poll(message: types.Message):
    if not quizzes_database.get(str(message.from_user.id)):
        quizzes_database[str(message.from_user.id)] = []

    if message.poll.type != "quiz":
        await message.reply("Извините, я принимаю только викторины (quiz)!")
        return

    quizzes_database[str(message.from_user.id)].append(Quiz(
        quiz_id=message.poll.id,
        question=message.poll.question,
        options=[o.text for o in message.poll.options],
        correct_option_id=message.poll.correct_option_id,
        owner_id=message.from_user.id)
    )
    all_list = []
    for i in quizzes_database[str(message.chat.id)]:
        jsonStr = json.dumps(i.__dict__)
        all_list.append(jsonStr)

    print(all_list)

    quizzes_owners[message.poll.id] = str(message.from_user.id)
    # jsonized = json.dumps(quizzes_database, indent=4, cls=CustomEncoder)

    with open('tests.json', 'w', encoding='utf-8') as outfile:
        json.dump(all_list, outfile, indent=4, ensure_ascii=False)
    await message.reply(
        f"Викторина сохранена. Общее число сохранённых викторин: {len(quizzes_database[str(message.from_user.id)])}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
