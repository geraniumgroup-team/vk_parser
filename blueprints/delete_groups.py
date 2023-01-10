from vkbottle.bot import Blueprint, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text
from vkbottle.dispatch.rules import ABCRule
from vkbottle import BaseStateGroup, GroupEventType, GroupTypes, StatePeer
from vkbottle.bot import Message, rules, MessageEvent
from models import Admin_panel_db
from STATES import COMMON_STATES
from start_keyboard import start_keyboard

bp = Blueprint("for chat commands")

Admin_panel_db = Admin_panel_db()


@bp.on.message(state=COMMON_STATES.CHOOSE_GROUP)
async def handle_callback_event(message: Message):
    page_number = Admin_panel_db.fetch_page_number()

    if message.text == 'Вперёд':
        page_number += 1

        if page_number > 0:
            Admin_panel_db.set_page_number(page_number)
            await choose_group(message)

    elif message.text == 'Назад':
        page_number -= 1
        Admin_panel_db.set_page_number(page_number)
        if page_number >= 0:

            await choose_group(message)

        else:
            await bp.state_dispenser.delete(message.peer_id)
            Admin_panel_db.set_page_number(0)
            await chose_user_finished(message)

    elif message.text == 'Завершить':
        Admin_panel_db.set_page_number(0)
        await bp.state_dispenser.delete(message.peer_id)
        await chose_user_finished(message)

    else:
        Admin_panel_db.deleta_group_id(message.payload)
        await choose_group(message)


@bp.on.message(text='Удалить группы', state=None)
async def choose_group(message: Message):
    state = await bp.state_dispenser.get(message.peer_id)

    if not state:

        page_number = 0

        await bp.state_dispenser.set(message.peer_id, COMMON_STATES.CHOOSE_GROUP)
    else:
        page_number = Admin_panel_db.fetch_page_number()

    all_usrs_ids = Admin_panel_db.fetch_all_groups()
    buttons = all_usrs_ids[0 + (page_number * 6): ((page_number + 1) * 6)]


    keyboard = Keyboard()
    for count, button in enumerate(buttons):
        filtered = await bp.api.groups.get_by_id(group_id=button)

        if count == 0:
            keyboard.row()
            keyboard.add(Text(f'{filtered[0].name}', f"{button}"))
        elif count % 2 == 0:
            keyboard.row()
            keyboard.add(Text(f'{filtered[0].name}',f"{button}"))
        else:
            keyboard.add(Text(f'{filtered[0].name}',f"{button}"))

    keyboard.row()
    keyboard.add(Text('Назад'))
    keyboard.add(Text('Вперёд'))
    keyboard.row()
    keyboard.add(Text('Завершить'))
    keyboard.get_json()

    await message.answer(message="Выберите группу",keyboard=keyboard)



async def chose_user_finished(message: Message):

    await message.answer('Опять работа?', keyboard=start_keyboard)

