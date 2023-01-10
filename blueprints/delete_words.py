from vkbottle.bot import Blueprint, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text
from vkbottle import BaseStateGroup, GroupEventType, GroupTypes, StatePeer
from vkbottle.bot import Message, rules, MessageEvent
from models import Admin_panel_db
from STATES import DELETE_WORD_STATES
from start_keyboard import start_keyboard

bp = Blueprint("for chat commands")

Admin_panel_db = Admin_panel_db()


@bp.on.message(state=DELETE_WORD_STATES.CHOOSE_WORD)
async def handle_callback_event(message: Message):
    page_number = Admin_panel_db.fetch_page_number()


    if message.text == 'Вперёд':
        page_number += 1

        if page_number > 0:
            Admin_panel_db.set_page_number(page_number)
            await choose_words(message)

    elif message.text == 'Назад':
        page_number -= 1
        Admin_panel_db.set_page_number(page_number)
        if page_number >= 0:

            await choose_words(message)

        else:
            await bp.state_dispenser.delete(message.peer_id)
            Admin_panel_db.set_page_number(0)
            await bp.state_dispenser.delete(message.peer_id)
            await chose_word_finished(message)


    elif message.text == 'Завершить':
        Admin_panel_db.set_page_number(0)
        await bp.state_dispenser.delete(message.peer_id)
        await chose_word_finished(message)



    else:
        Admin_panel_db.delete_word(message.text)
        await choose_words(message)


@bp.on.message(text='Удалить слова')
async def choose_words(message: Message):
    state = await bp.state_dispenser.get(message.peer_id)

    if not state:

        page_number = 0

        await bp.state_dispenser.set(message.peer_id, DELETE_WORD_STATES.CHOOSE_WORD)
    else:
        page_number = Admin_panel_db.fetch_page_number()

    all_words = Admin_panel_db.fetch_all_words()
    buttons = all_words[0 + (page_number * 6): ((page_number + 1) * 6)]


    keyboard = Keyboard()
    for count, button in enumerate(buttons):

        if count == 0:

            keyboard.row()
            keyboard.add(Text(f'{button}'))

        elif count % 2 == 0:
            keyboard.row()
            keyboard.add(Text(f'{button}'))
        else:
            keyboard.add(Text(f'{button}'))

    keyboard.row()
    keyboard.add(Text('Назад'))
    keyboard.add(Text('Вперёд'))
    keyboard.row()
    keyboard.add(Text('Завершить'))
    keyboard.get_json()

    await message.answer(message="Выберите человека",keyboard=keyboard)



async def chose_word_finished(message: Message):
    await message.answer('Опять работать?', keyboard=start_keyboard)

